# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

import time


class SinglePhaseWizard(models.TransientModel):
    _name = "single.phase.wizard"

    date_from = fields.Date(" Date From", )
    date_to = fields.Date("Date To ")
    type = fields.Selection([('standard', 'standard'), ('shnider', 'Shnider')])



    @api.constrains('date_from', 'date_to')
    def _check_from_to_date(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValidationError(_('From Date should not be bigger than To Date.'))

    def print_report_xls(self):
        active_record = self.env.context.get('active_ids', [])
        record = self.env['maintenance.request'].browse(active_record)

        data = {
            'ids': self.ids,
            'model': self._name,
            'record': record.id,
        }
        action = self.env.ref('maintenance_reports.phase_report_excel').report_action(self, data=data)
        action.update({'close_on_report_download': True})
        return action
