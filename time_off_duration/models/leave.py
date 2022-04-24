# -*- coding: utf-8 -*-

from odoo import models, fields,api


class hr_leave_c(models.Model):

    _inherit = "hr.leave"


    # @api.onchage
    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        res=super(hr_leave_c, self)._onchange_leave_dates()

        if self.date_from and self.date_to:
            self.number_of_days = round((self.request_date_to-self.request_date_from).total_seconds() / (3600*24),0)+1
        else:
            self.number_of_days = 0
        return res
