from .tf2it import tf2it
from odoo import fields, models, _, api, exceptions
import datetime
from datetime import timedelta
import logging
from num2words import num2words



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    tafqeet_total = fields.Text(compute="calc_amount_tafqeet",store=True)
    attention = fields.Many2one('res.partner', domain="[('id','in',attention_ids)]")
    attention_ids = fields.Many2many('res.partner', 'par_purchase_relation', 'att1_purchase', 'att2_purchase', compute='child_ids', store=True)

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

    @api.depends('amount_total')
    def calc_amount_tafqeet(self):
        b = tf2it()
        for rec in self:
            # rec.tafqeet_total = b.convertNumber(rec.amount_total)+ ' جنيه فقط لا غير'
            rec.tafqeet_total =str(num2words(rec.amount_total, to='currency',
                                          lang='en')).upper()