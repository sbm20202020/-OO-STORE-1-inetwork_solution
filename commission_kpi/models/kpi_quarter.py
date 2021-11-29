# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import ast
from datetime import datetime
from dateutil import relativedelta
from odoo.exceptions import ValidationError, UserError

class KPIQuarter(models.Model):
    _name= 'kpi.quarter'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name=fields.Char(required=True)
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date",required=True)
    active=fields.Boolean(default=True)

    @api.constrains('date_from','date_to')
    def set_cons_date(self):

        if self.date_from != False and self.date_to != False and self.date_from > self.date_to:
                raise ValidationError(_("Start date should be less than end date"))

        if self.date_from != False and self.date_to != False and relativedelta.relativedelta(datetime.strptime(str(self.date_to), '%Y-%m-%d'), datetime.strptime(str(self.date_from), '%Y-%m-%d')).months +1 != 3:
                raise ValidationError(_("Quarter should be 3 months only"))

        if self.date_from != False and self.date_to != False and datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime("%Y") !=  datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime("%Y"):
            raise ValidationError(_("Quarter should be in the same year"))

        aleardy_quarter=self.search([('date_from','>=',self.date_from),('date_to','<=',self.date_to),('id','!=',self.id)])
        aleardy_quarter2=self.search([('date_from','>',self.date_from),('date_to','>',self.date_to),('id','!=',self.id)])
        # aleardy_quarter3=self.search([('date_from','<',self.date_from),('date_to','<',self.date_to),('id','!=',self.id)])
        if aleardy_quarter or aleardy_quarter2 :
            raise ValidationError(_("This period on Quarter aleardy created"))
