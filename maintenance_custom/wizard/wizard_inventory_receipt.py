from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockInventoryWizard(models.TransientModel):
    _name = "stock.inventory.receipt"
    _description = "Stock Inventory Wizard"

    def _get_picking_in(self):
        pick_in = self.env.ref('stock.picking_type_in', raise_if_not_found=False)
        company = self.env.company
        if not pick_in or pick_in.sudo().warehouse_id.company_id.id != company.id:
            pick_in = self.env['stock.picking.type'].search(
                [('warehouse_id.company_id', '=', company.id), ('code', '=', 'incoming')],
                limit=1,
            )
        return pick_in

    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      help="This will determine picking type of outgoing shipment", required=True, default=_get_picking_in)
    des_location_id = fields.Many2one('stock.location', 'Destination Location', required=True, domain=[('usage', '<>', 'view')])
    location_id = fields.Many2one('stock.location', "Location", required=True, domain=[('usage', '<>', 'view')])
    product_id = fields.Many2one('product.product', 'Device', required=True)
    serial = fields.Char('Serial', required=True)
    qty = fields.Float('QTY', required=True)
    partner = fields.Many2one('res.partner', required=True)

    @api.constrains('qty')
    def not_minus(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('QTY should not minus. or 0'))


    def create_picking(self):
        self.ensure_one()
        # Create new picking for products
        active_id = self._context.get('active_ids', []) or []
        maintenance = self.env['maintenance.request'].browse(active_id)
        pick_type_id = self.picking_type_id.id
        new_picking = self.env["stock.picking"].create({
            'move_lines': [],
            'picking_type_id': pick_type_id,
            'state': 'draft',
            'origin': maintenance.name,
            'partner_id': self.partner.id,
            'picking_type_code': 'incoming',
            'location_id': self.location_id.id,
            'location_dest_id': self.des_location_id.id,
            # 'group_id': self.rma_id.order_id.procurement_group_id.id,
        })
        x = self.env["stock.move"].create({
            'product_id': self.product_id.id,
            'product_uom_qty': float(self.qty),
            'name': self.product_id.partner_ref,
            'product_uom': self.product_id.uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'origin': self.serial,
            'location_id': self.location_id.id,
            'location_dest_id': self.des_location_id.id,
            'picking_type_id': self.picking_type_id.id,
            'warehouse_id': self.picking_type_id.warehouse_id.id,
            'procure_method': 'make_to_stock',
            # 'group_id': self.rma_id.order_id.procurement_group_id.id,
        })
        maintenance.picking_id = new_picking.id
        maintenance.picking_count = 1
        maintenance.receipt_created = True
        return new_picking, pick_type_id


class SalesOrderWizard(models.TransientModel):
    _name = "sales.order.wizard"
    _description = "Sales Order Wizard"

    date_order = fields.Date('Order Date')

    def create_so(self):
        self.ensure_one()
        # Create new sales order for products
        active_id = self._context.get('active_ids', []) or []
        maintenance = self.env['maintenance.request'].browse(active_id)
        new_order = self.env["sale.order"].create({
            'company_id': maintenance.picking_id.company_id.id,
            'partner_id': maintenance.picking_id.partner_id.id,
            'date_order': self.date_order,
        })
        for line in maintenance.picking_id.move_ids_without_package:
            sol = self.env['sale.order.line'].create({
                'product_id': line.product_id.id,
                'order_id': new_order.id,
                'name': line.product_id.name,
                'product_uom_qty': float(line.product_uom_qty),
                'product_uom': line.product_id.uom_id.id,
                'price_unit': line.product_id.list_price,
            })
        stage_obj = self.env['maintenance.stage'].search([('name', '=', 'Created SO')])
        maintenance.stage_id = stage_obj.id
        maintenance.stage_name = 'Created SO'
        maintenance.sales_order_id = new_order.id

        return new_order