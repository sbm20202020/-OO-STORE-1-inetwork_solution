# -*- coding: utf-8 -*-


from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    # remove default domain on employee field
    # def _get_employees(self):
    #     # YTI check dates too
    #     return self.env['hr.employee'].search(self._get_available_contracts_domain())

    def _get_employees(self):
        # YTI check dates too
        empy_list=[]
        return empy_list

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
                                    default=lambda self: self._get_employees(), required=True)

class HrPayslipRun(models.Model):

    _inherit= 'hr.payslip.run'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Verify'),
        ('cancel', 'Cancel'),
        ('close', 'Done'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')

    # def _are_payslips_cancel(self):
    #     for slip in self.mapped('slip_ids'):
    #         slip.acton_payslip_cancel()


    def action_cancel(self):
        for rec in self:
            for slip in rec.mapped('slip_ids'):
                slip.write({'state' : 'cancel'})
            rec.write({'state': 'cancel'})
