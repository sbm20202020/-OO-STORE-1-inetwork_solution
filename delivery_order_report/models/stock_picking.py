from odoo import fields, models, _, api, exceptions
import datetime
from datetime import timedelta
import logging


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # cst_po_number_id = fields.Many2one('cst.po.number',string="CST PO Number")
    cst_po_number= fields.Char(string="CST PO Number")

    attention = fields.Many2one('res.partner', domain="[('id','in',attention_ids)]")
    attention_ids = fields.Many2many('res.partner', 'par_picking_relation', 'att1_picking', 'att2_picking',
                                     compute='child_ids')

    @api.depends('partner_id')
    def child_ids(self):
        child = []
        for l in self:
            if l.partner_id:
                for rec in l.partner_id.child_ids:
                    print(rec)
                    child.append(rec.id)
                if child:
                    l.attention_ids = child
                else:
                    l.attention_ids = False
            else:
                l.attention_ids = False

class StockMove(models.Model):
    _inherit = 'stock.move'
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    lot_name = fields.Char('Lot/Serial Number Name')


