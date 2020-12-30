# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools.float_utils import float_compare


class StockInventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    check_missing = fields.Boolean(default=False, copy=False)

    def action_validate(self):
        if self.check_missing is False:
            products = []
            inventory_obj = self.env['stock.inventory.line'].search([('inventory_id', '=', self.id)])
            for rec in inventory_obj:
                # if rec.inventory_id.product_ids:
                #     if rec.product_id.qty_available <= 0 and rec.product_id not in rec.inventory_id.product_ids.ids:
                #         products.append(rec.product_id.id)
                # else:
                products.append(rec.product_id.id)
                '''domain = [
                    ('id', '!=', rec.id),
                    ('product_id', '=', rec.product_id.id),
                    ('location_id', '=', rec.location_id.id),
                    ('partner_id', '=', rec.partner_id.id),
                    ('package_id', '=', rec.package_id.id),
                    ('prod_lot_id', '=', rec.prod_lot_id.id),('inventory_id', '=', rec.inventory_id.id)]
                existings = self.env['stock.inventory.line'].search_count(domain)
                if existings:'''
            print("LEN", len(set(products)),
                  len(self.env['product.product'].search([('id', 'not in', products), ('type', '=', 'product')]).ids))
            ctx = {'default_inventory_id': self.id,
                   'default_location_ids': self.location_ids.ids,
                   'default_product_ids': self.env['product.product'].search(
                       [('id', 'not in', products), ('id', 'in', self.product_ids.ids), ('type', '=', 'product'),
                        ('qty_available', '>', 0)]).ids, }
            return {'name': _("Missing Items"),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'res_model': 'missing.item.wizard',
                    'target': 'new',
                    'view_id': self.env.ref('inventory_adjustments_access_right.view_missing_item_wizard').id,
                    'context': ctx}
        else:
            if not self.exists():
                return
            self.ensure_one()
            if not self.user_has_groups('stock.group_stock_manager'):
                raise UserError(_("Only a stock manager can validate an inventory adjustment."))
            if self.state != 'confirm':
                raise UserError(_(
                    "You can't validate the inventory '%s', maybe this inventory " +
                    "has been already validated or isn't ready.") % (self.name))
            inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot',
                                                                                         'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
            lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1,
                                                                   precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
            if inventory_lines and not lines:
                wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in
                             inventory_lines.mapped('product_id')]
                wiz = self.env['stock.track.confirmation'].create(
                    {'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
                return {
                    'name': _('Tracked Products in Inventory Adjustment'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'res_model': 'stock.track.confirmation',
                    'target': 'new',
                    'res_id': wiz.id,
                }
            self._action_done()
            self.line_ids._check_company()
            self._check_company()
            return True

    '''def action_open_inventory_lines(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('stock.stock_inventory_line_tree2').id, 'tree')],
            'view_mode': 'tree',
            'name': _('Inventory Lines'),
            'res_model': 'stock.inventory.line',
        }
        context = {
            'default_is_editable': True,
            'default_inventory_id': self.id,
            'default_company_id': self.company_id.id,
        }
        # Define domains and context
        domain = [
            ('is_editable', '=', True),
            ('inventory_id', '=', self.id),
            ('location_id.usage', 'in', ['internal', 'transit'])
        ]
        if self.location_ids:
            context['default_location_id'] = self.location_ids[0].id
            if len(self.location_ids) == 1:
                if not self.location_ids[0].child_ids:
                    context['readonly_location_id'] = True

        if self.product_ids:
            if len(self.product_ids) == 1:
                context['default_product_id'] = self.product_ids[0].id

        action['context'] = context
        action['domain'] = domain
        return action'''

    def _get_inventory_lines_values(self):
        # TDE CLEANME: is sql really necessary ? I don't think so
        locations = self.env['stock.location']
        if self.location_ids:
            locations = self.env['stock.location'].search([('id', 'child_of', self.location_ids.ids)])
        else:
            locations = self.env['stock.location'].search(
                [('company_id', '=', self.company_id.id), ('usage', 'in', ['internal', 'transit'])])
        domain = ' location_id in %s AND quantity != 0 AND active = TRUE'
        args = (tuple(locations.ids),)

        vals = []
        Product = self.env['product.product']
        # Empty recordset of products available in stock_quants
        quant_products = self.env['product.product']

        # If inventory by company
        if self.company_id:
            domain += ' AND company_id = %s'
            args += (self.company_id.id,)
        if self.product_ids:
            domain += ' AND product_id in %s'
            args += (tuple(self.product_ids.ids),)

        self.env['stock.quant'].flush(
            ['company_id', 'product_id', 'quantity', 'location_id', 'lot_id', 'package_id', 'owner_id'])
        self.env['product.product'].flush(['active'])
        self.env.cr.execute("""SELECT product_id, sum(quantity) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
            FROM stock_quant
            LEFT JOIN product_product
            ON product_product.id = stock_quant.product_id
            WHERE %s
            GROUP BY product_id, location_id, lot_id, package_id, partner_id """ % domain, args)

        for product_data in self.env.cr.dictfetchall():
            product_data['company_id'] = self.company_id.id
            product_data['inventory_id'] = self.id
            # replace the None the dictionary by False, because falsy values are tested later on
            for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                product_data[void_field] = False
            product_data['theoretical_qty'] = product_data['product_qty']
            if self.prefill_counted_quantity == 'zero':
                product_data['product_qty'] = 0
            if product_data['product_id']:
                product_data['product_uom_id'] = Product.browse(product_data['product_id']).uom_id.id
                quant_products |= Product.browse(product_data['product_id'])
            vals.append(product_data)
        return []


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'
    check_activity_sent = fields.Boolean(string='Check Activity Sent', default=False)

    @api.model
    def create(self, vals):
        res = super(StockInventoryLine, self).create(vals)
        users = self.env['res.users'].search([])
        if vals.get('inventory_id'):
            inventory_obj = self.env['stock.inventory'].browse(vals.get('inventory_id'))
            for user in users:
                if res.check_activity_sent == False and user.has_group(
                        'inventory_adjustments_access_right.group_inventory_adjustments_access_right') and not user.has_group(
                    'base.group_system'):
                    inventory_obj.activity_schedule(
                        'inventory_adjustments_access_right.schdule_activity_stock_inventory_manager_id',
                        user_id=user.id,
                        summary='Inventory Adjustment' + ' ' + str(
                            inventory_obj.name) + ' ' + 'still not validated')
                    vals['check_activity_sent'] = True

        return res

    @api.onchange('product_id', 'location_id', 'product_uom_id', 'prod_lot_id', 'partner_id', 'package_id')
    def _onchange_quantity_context(self):
        product_qty = False
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
        if self.product_id and self.location_id and self.product_id.uom_id.category_id == self.product_uom_id.category_id:  # TDE FIXME: last part added because crash
            theoretical_qty = self.product_id.get_theoretical_quantity(
                self.product_id.id,
                self.location_id.id,
                lot_id=self.prod_lot_id.id,
                package_id=self.package_id.id,
                owner_id=self.partner_id.id,
                to_uom=self.product_uom_id.id,
            )
        else:
            theoretical_qty = 0
        # Sanity check on the lot.
        if self.prod_lot_id:
            if self.product_id.tracking == 'none' or self.product_id != self.prod_lot_id.product_id:
                self.prod_lot_id = False

        if self.prod_lot_id and self.product_id.tracking == 'serial':
            # We force `product_qty` to 1 for SN tracked product because it's
            # the only relevant value aside 0 for this kind of product.
            self.product_qty = 1
        elif self.product_id and float_compare(self.product_qty, self.theoretical_qty,
                                               precision_rounding=self.product_uom_id.rounding) == 0:
            # We update `product_qty` only if it equals to `theoretical_qty` to
            # avoid to reset quantity when user manually set it.
            # self.product_qty = theoretical_qty
            self.product_qty = 0.0
        self.theoretical_qty = theoretical_qty
