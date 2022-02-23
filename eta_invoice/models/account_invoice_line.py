# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _ ,tools, SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from datetime import datetime , date ,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from odoo.fields import Datetime as fieldsDatetime
import calendar
from odoo import http
from odoo.http import request
from odoo import tools

import logging

LOGGER = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sales_total = fields.Monetary(compute='compute_total_amount', store=False, currency_field='company_currency_id')
    total = fields.Monetary(compute='compute_total_amount', store=False, currency_field='company_currency_id')
    net_total = fields.Monetary(compute='compute_total_amount', store=False, currency_field='company_currency_id')
    total_taxable_fees = fields.Monetary(compute='compute_total_amount', store=False, currency_field='company_currency_id')
    items_discount = fields.Monetary(compute='compute_total_amount', store=False, currency_field='company_currency_id')

    @api.depends('price_unit','price_total','quantity','tax_ids')
    def compute_total_amount(self):

        for rec in self:
            if rec.currency_id and rec.company_currency_id and rec.currency_id != rec.company_currency_id:
                currency = rec.currency_id
                comp_currency = rec.company_currency_id
                inv_date = rec.move_id.date
                company = rec.company_id or self.env.user.company_id
                price_unit = currency._convert( rec.price_unit, comp_currency, company, inv_date)
                sales_total = rec.quantity * price_unit
                rec.sales_total = sales_total
                discount_amount = sales_total * rec.discount / 100.0
                net_total = sales_total - discount_amount
                rec.net_total = net_total
                # rec.net_total = currency._convert( net_total , comp_currency, company, inv_date)
                tax_amount = currency._convert((rec.price_total - rec.price_subtotal), comp_currency, company, inv_date)
                rec.total =  net_total + tax_amount
                price_unit_wo_discount = rec.price_unit * (1 - (rec.discount / 100.0))

                force_sign = -1 if rec.move_id.type in ('out_invoice', 'in_refund', 'out_receipt') else 1
                taxes_res = rec.tax_ids.filtered(lambda i: i.tax_type in ('T5','T6','T7','T8','T9','T10','T11','T12') ).with_context(force_sign=force_sign).compute_all(price_unit_wo_discount,
                                                                                              quantity=rec.quantity,
                                                                                              currency=rec.move_id.currency_id,
                                                                                              product=rec.product_id,
                                                                                              partner=rec.partner_id,
                                                                                              is_refund=rec.move_id.type in (
                                                                                              'out_refund', 'in_refund'))

                total_taxable_fees = sum(tax['amount'] for tax in taxes_res['taxes'])
                rec.total_taxable_fees = currency._convert( total_taxable_fees, comp_currency, company, inv_date)
                rec.items_discount = 0
            else:
                rec.sales_total = rec.quantity * rec.price_unit
                discount_amount = rec.sales_total * rec.discount / 100.0
                rec.net_total = rec.sales_total - discount_amount
                rec.total = rec.net_total + (rec.price_total - rec.price_subtotal)
                price_unit_wo_discount = rec.price_unit * (1 - (rec.discount / 100.0))

                force_sign = -1 if rec.move_id.type in ('out_invoice', 'in_refund', 'out_receipt') else 1
                taxes_res = rec.tax_ids.filtered(
                    lambda i: i.tax_type in ('T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12')).with_context(
                    force_sign=force_sign).compute_all(price_unit_wo_discount,
                                                       quantity=rec.quantity,
                                                       currency=rec.move_id.currency_id,
                                                       product=rec.product_id,
                                                       partner=rec.partner_id,
                                                       is_refund=rec.move_id.type in (
                                                           'out_refund', 'in_refund'))

                rec.total_taxable_fees = sum(tax['amount'] for tax in taxes_res['taxes'])
                rec.items_discount = 0

    def get_taxable_items(self):
        items = {}
        currency = self.currency_id
        comp_currency = self.company_currency_id
        inv_date = self.move_id.date
        company = self.company_id or self.env.user.company_id
        price_unit_wo_discount = self.price_unit * (1 - (self.discount / 100.0))

        force_sign = -1 if self.move_id.type in ('out_invoice', 'in_refund', 'out_receipt') else 1
        taxes_res = self.tax_ids.with_context(
            force_sign=force_sign).compute_all(price_unit_wo_discount,
                                               quantity=self.quantity,
                                               currency=self.move_id.currency_id,
                                               product=self.product_id,
                                               partner=self.partner_id,
                                               is_refund=self.move_id.type in ('out_refund', 'in_refund'))

        for tax_item in taxes_res['taxes']:
            tax_id = tax_item['id']
            tax = self.env['account.tax'].browse(tax_id)
            if currency != comp_currency:
                tax_item_amount = currency._convert(tax_item['amount'], comp_currency, company, inv_date)
            else:
                tax_item_amount = tax_item['amount']

            if not tax.tax_type in items:
                t4=1
                if tax.tax_type== 'T4':
                    t4=-1

                items[tax.tax_type] = {
                    'tax_type': tax.tax_type,
                    'sub_type': tax.sub_type,
                    'rate': tax.amount * t4,
                    'amount': tax_item_amount * t4,
                }
            else:
                items[tax.tax_type] += tax_item_amount

        return items
