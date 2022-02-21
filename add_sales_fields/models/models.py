# -*- coding: utf-8 -*-

from odoo import models, fields, api



class AccountMove(models.Model):
    _inherit = 'account.move'

    site_name = fields.Char(string='Site')
    cst_po_number= fields.Char(string="Case Number")



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    site_name = fields.Char(string='Site',required=True)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            for line in order.picking_ids:
                line.write({'site_name': order.site_name})

        return res


    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['site_name'] = self.site_name
        res['cst_po_number'] = self.cst_po_number

        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    availability_id = fields.Many2one("availability.availability",string='Availability')





class StockPicking(models.Model):
    _inherit = 'stock.picking'
    site_name = fields.Char(string='Site')






