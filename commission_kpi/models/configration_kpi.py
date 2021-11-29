# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import ast
from odoo.exceptions import ValidationError, UserError


class SalesVolume(models.Model):
    _name = 'sales.volume'
    name=fields.Char(required=True)
    basic=fields.Percent(required=True)
    actual=fields.Percent(required=True)
    user_id=fields.Many2one('res.users')
    kpi_user_id=fields.Many2one('kpi.user')

    @api.onchange('actual')
    def onchange_basic(self):
        if self.actual > self.basic:
            raise ValidationError(_("Actual should n't bigger than Basic"))


class PerformanceValue(models.Model):
    _name = 'performance.value'
    name=fields.Char(required=True)
    basic=fields.Percent(required=True)
    actual=fields.Percent(required=True)
    user_id=fields.Many2one('res.users')
    kpi_user_id=fields.Many2one('kpi.user')


    @api.onchange('actual')
    def onchange_basic(self):
        if self.actual > self.basic:
            raise ValidationError(_("Actual should n't bigger than Basic"))





class MarketShare(models.Model):
    _name = 'market.share'
    name=fields.Char(required=True)
    basic=fields.Percent(required=True)
    actual=fields.Percent(required=True)
    user_id=fields.Many2one('res.users')
    kpi_user_id=fields.Many2one('kpi.user')


    @api.onchange('actual')
    def onchange_basic(self):
        if self.actual > self.basic:
            raise ValidationError(_("Actual should n't bigger than Basic"))





class PurchaseSalesCommision(models.Model):
    _name = 'purchase.sales.commision'
    name=fields.Char(required=True)
    basic=fields.Percent(required=True)
    actual=fields.Percent(required=True)
    user_id=fields.Many2one('res.users')
    kpi_user_id=fields.Many2one('kpi.user')


    @api.onchange('actual')
    def onchange_basic(self):
        if self.actual > self.basic:
            raise ValidationError(_("Actual should n't bigger than Basic"))




