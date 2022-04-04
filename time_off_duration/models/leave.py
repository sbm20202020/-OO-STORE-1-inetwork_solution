# -*- coding: utf-8 -*-

from odoo import models, fields,api


class hr_leave_c(models.Model):

    _inherit = "hr.leave"


    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_number_of_days(self):
        res=super(hr_leave_c, self)._compute_number_of_days()
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                holiday.number_of_days =  round((holiday.date_to-holiday.date_from).total_seconds() / (3600*24),0)+1
                # print((holiday.date_to-holiday.date_from).total_seconds() ,"number_of_days")
            else:
                holiday.number_of_days = 0


        # print(res)
        return res

