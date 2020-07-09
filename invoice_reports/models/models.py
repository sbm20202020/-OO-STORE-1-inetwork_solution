# -*- coding: utf-8 -*-

from odoo import models, fields, api

### related to task INS-13

class  rescompany_inherit(models.Model):
    _inherit = 'res.company'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    commercial_record = fields.Char(related='partner_id.commercial_record', string="Commercial Record", readonly=False)
    tax_file = fields.Char(related='partner_id.tax_file', string="Tax file", readonly=False)
    sales_taxes = fields.Char(related='partner_id.sales_taxes', string="Sales taxes", readonly=False)


class Partner_inherit(models.Model):
    _inherit = "res.partner"

    commercial_record = fields.Char(string='Commercial Record', help="The Commercial Record. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
    tax_file = fields.Char(string='Tax file', help="The Tax file. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
    sales_taxes = fields.Char(string='Sales taxes', help="The Sales taxes. Complete it if the contact is subjected to government taxes. Used in some legal statements.")


class InvoiceOrder(models.Model):

    _inherit = 'account.move'

    # @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
            print(rec.num_word)

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')

 ######################################################