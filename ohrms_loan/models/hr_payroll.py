# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment", help="Loan installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        result=super(HrPayslip, self)._onchange_employee()
        if self.employee_id:
                lon_obj = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'approve')])
                res=[]
                input=''
                for loan in lon_obj:
                    for loan_line in loan.loan_lines:
                        print(self.date_from)
                        if self.date_from <= loan_line.date <= self.date_to and not loan_line.paid:
                            other_input = self.env['hr.payslip.input.type'].search(
                                [('struct_ids', 'in', [self.struct_id.id]), ('code', '=', 'LO')])
                            for line in other_input:
                                lines = {
                                    'input_type_id': line.id,
                                    'amount': loan_line.amount,
                                    'loan_line_id': loan_line.id,
                                }
                                res.append(lines)
                                self.input_line_ids = [(0, 0, lines)]


        return result

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()
