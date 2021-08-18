# -*- coding: utf-8 -*-

import json
from datetime import datetime , timedelta , date
import calendar
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api


class KpiWizard(models.TransientModel):
    _name = "kpi.wizard"
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    quarter=fields.Many2one('kpi.quarter')
    sales_person=fields.Many2many('res.users')

    @api.onchange('quarter')
    def onchange_quarter(self):
        if self.quarter :
            self.date_from =self.quarter.date_from
            self.date_to =self.quarter.date_to



    @api.constrains('date_from','date_to')
    def set_cons_date(self):
        if self.date_from != False and self.date_to != False and self.date_from > self.date_to:
                raise ValidationError(_("Start date should be less than end date"))


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






