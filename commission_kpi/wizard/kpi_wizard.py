# -*- coding: utf-8 -*-

import json
from datetime import datetime , timedelta , date
import calendar
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api,_


class KpiWizard(models.TransientModel):
    _name = "kpi.wizard"
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    quarter_date=fields.Char(compute='assign_quarter',string='Quarter')
    quarter=fields.Many2one('kpi.quarter')
    sales_person=fields.Many2many('res.users')
    kpi_ref_ids=fields.Many2many('kpi.user',string='KPI Ref',compute='_get_kpi_ref')


    def get_quarter(self,month):
      if  month in range(1,4):
          return 'Q1'
      elif  month in range(4,7):
          return 'Q2'
      elif  month in range(7,10):
          return 'Q3'
      elif  month in range(10,13):
          return 'Q4'

    @api.depends('date_from','date_to')
    def assign_quarter(self):
        for rec in self:
            if rec.date_from != False and rec.date_to != False:
                month1 = rec.date_from.strftime('%m')
                month2 = rec.date_to.strftime('%m')
                if self.get_quarter(int(month1)) == self.get_quarter(int(month2)):
                    rec.quarter_date = self.get_quarter(int(month1))
                else:
                    rec.quarter_date = False
            else:
                    rec.quarter_date = False





    @api.onchange('quarter')
    def onchange_quarter(self):
        if self.quarter :
            self.date_from =self.quarter.date_from
            self.date_to =self.quarter.date_to


    @api.depends('sales_person','date_from','date_to')
    def _get_kpi_ref(self):
        for rec in self:
            kpis=self.env['kpi.user'].search([('user_id','in',rec.sales_person.ids),('date_from','=',rec.date_from),('date_to','=',rec.date_to)])
            rec.kpi_ref_ids=kpis

    @api.constrains('date_from','date_to','sales_person')
    def set_cons_date(self):
        if self.date_from != False and self.date_to != False and self.date_from > self.date_to:
                raise ValidationError(_("Start date should be less than end date"))
        if not self.kpi_ref_ids :
            raise ValidationError(
                _('firstly please add KPI to sales person in the same period'))

        for salesperson in self.sales_person:
             if self.kpi_ref_ids.filtered(lambda s: s.user_id == salesperson).id == False:
                  raise ValidationError(
                     _('firstly please add KPI to sales person %s in the same period') % (salesperson.name))

    def generate_xlsx_report(self):
        active_record = self.env.context.get('active_ids', [])
        record = self.env['sale.order'].browse(active_record)

        data = {
            'ids': self.ids,
            'model': self._name,
            'record': record.id,
        }
        action = self.env.ref('commission_kpi.commission_kpi_report_excel_id').report_action(self, data=data)
        # action.update({'close_on_report_download': True})
        return action






