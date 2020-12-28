from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Relational fields
    product_category_id = fields.Many2one('product.category')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_picking_id = fields.Many2one('account.move', compute='_get_invoice_picking_id')

    invoice_state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], related='invoice_picking_id.state',store=True)

    invoice_state_2 = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], related='invoice_picking_id.state',store=True)

    # @api.multi
    @api.depends('partner_id')
    def _get_invoice_picking_id(self):
        for rec in self:
            if rec.sale_id.invoice_ids:
                for line in rec.sale_id.invoice_ids:
                    rec.invoice_picking_id = line.id
            else:
                rec.invoice_picking_id = False


class SaleOrderCustomize(models.Model):
    _inherit = 'sale.order.line'

    sales_price = fields.Float(compute='get_sales_price')

    # @api.multi
    @api.onchange('product_id')
    def get_sales_price(self):
        for item in self:
            item.sales_price = item.product_id.lst_price
