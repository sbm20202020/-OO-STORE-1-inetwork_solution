from odoo import fields, models, _, api, exceptions
from odoo.exceptions import  ValidationError

import datetime
from datetime import timedelta
import logging


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cst_po_number= fields.Char(string="CST PO Number")

    # @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if not order.cst_po_number:
                raise ValidationError(" You Should Enter CST PO Number Before Confirm order")

            for line in order.picking_ids:
                line.write({'cst_po_number': order.cst_po_number, 'attention': order.attention.id})

        return res



# edit by marwa ahmed 16/6

# class CSTPONumber(models.Model):
#     _name = 'cst.po.number'
#
#     name = fields.Char(string="CST PO Number",required=True)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # edit by marwa ahmed 16/6
    # cst_po_number_id = fields.Many2one('cst.po.number',string="CST PO Number")

    cst_po_number= fields.Char(string="CST PO Number")

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            # if not order.cst_po_number:
            #     raise ValidationError(" You Should Enter CST PO Number Before Confirm order")

            for line in order.picking_ids:
                line.write({'cst_po_number': order.cst_po_number, 'attention': order.attention.id})


        return res
