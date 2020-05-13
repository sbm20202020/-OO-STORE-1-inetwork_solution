from odoo import fields, models, _, api, exceptions
import datetime
from datetime import timedelta
import logging


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cst_po_number_id = fields.Many2one('cst.po.number',string="CST PO Number")

    # @api.multi
    def action_confirm(self):

        res = super(SaleOrder, self).action_confirm()
        print("jjjjjjjjjjjjjjjj", res)

        for order in self:
            if order.cst_po_number_id and order.attention:
                print("jjjjjjjjjjjjjjjj",order.picking_ids)
                for line in order.picking_ids:
                    line.write({'cst_po_number_id': order.cst_po_number_id.id, 'attention': order.attention.id})
        return res


class CSTPONumber(models.Model):
    _name = 'cst.po.number'

    name = fields.Char(string="CST PO Number",required=True)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    cst_po_number_id = fields.Many2one('cst.po.number',string="CST PO Number")

    # @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.cst_po_number_id and order.attention:
                for line in order.picking_ids:
                    line.write({'cst_po_number_id': order.cst_po_number_id.id, 'attention': order.attention.id})
        return res
