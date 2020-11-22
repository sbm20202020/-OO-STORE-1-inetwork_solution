# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools.float_utils import float_compare


class StockInventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    check_missing = fields.Boolean(default=False, copy=False)

    def action_validate(self):
        if self.check_missing == False:
            products = []
            inventory_obj = self.env['stock.inventory.line'].search([('inventory_id', '=', self.id)])
            for rec in inventory_obj:
                products.append(rec.product_id.id)
            print("LEN", len(set(products)),
                  len(self.env['product.product'].search([('id', 'not in', products), ('type', '=', 'product')]).ids))
            ctx = {'default_inventory_id': self.id,
                   'default_location_ids': self.location_ids.ids,
                   'default_product_ids': self.env['product.product'].search(
                       [('id', 'not in', products), ('type', '=', 'product')]).ids, }
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

    def action_open_inventory_lines(self):
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
        return action


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
