from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime

from datetime import datetime


class HrLoan(models.Model):
    _inherit = 'hr.loan'

    loan_type = fields.Selection([
        ('loan', 'Loan'),
        ('advance_salary', 'Advance Salary'),
    ], string="Type", track_visibility='onchange', copy=False, )

    @api.constrains('loan_amount')
    def not_minus(self):
        for rec in self:
            if rec.loan_amount <= 0:
                raise ValidationError('Loan  should not be minus 0')

    # @api.constrains('loan_amount', 'employee_id', 'loan_type')
    # def request_loan(self):
    #     loan_obj = self.search(
    #         [('employee_id', '=', self.employee_id.id),('date', '<', self.date), ('state', '=', 'approve')])
    #     list_index = []
    #     if len(loan_obj) >= 1:
    #         for rec in loan_obj:
    #             month_dd = datetime.strptime((str(rec.date)), '%Y-%m-%d').strftime('%m')
    #             month_obj_date = datetime.strptime((str(self.date)), '%Y-%m-%d').strftime('%m')
    #             year_dd = datetime.strptime((str(self.date)), '%Y-%m-%d').strftime('%y')
    #             year_obj = datetime.strptime((str(rec.date)), '%Y-%m-%d').strftime('%y')
    #             if month_dd == month_obj_date and year_dd == year_obj:
    #                 list_index.append(rec.date)
    #         last_loan = max(list_index)
    #         contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
    #         for l in contract_obj:
    #             employe_salary = l.wage
    #             work_day_count = employe_salary / 30
    #             now_date = datetime.now().strftime('%m')
    #             count = 0
    #             attend_obj = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
    #             for line in attend_obj:
    #                 month_d = datetime.strptime(str(line.check_in), '%Y-%m-%d %H:%M:%S').strftime('%m')
    #                 if month_d == now_date and datetime.strftime(line.check_in, '%Y-%m-%d') > datetime.strftime(
    #                         last_loan, '%Y-%m-%d'):
    #                     count += 1
    #             loan = (count * work_day_count) * .5
    #             # doaa added loan_type condition
    #             if self.loan_amount > loan and self.loan_type == 'advance_salary':
    #                 raise ValidationError("You Cant Request Loan With This Amount")
    #
    #     else:
    #         contract_obj2 = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
    #         for l in contract_obj2:
    #             employe_salary2 = l.wage
    #             work_day_count = employe_salary2 / 30
    #             now_date2 = datetime.now().strftime('%m')
    #             count = 0
    #             attend_obj2 = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
    #             for line in attend_obj2:
    #                 month_d = datetime.strptime(str(line.check_in), '%Y-%m-%d %H:%M:%S').strftime('%m')
    #                 if month_d == now_date2 and datetime.strftime(line.check_in, '%Y-%m-%d') <= datetime.strftime(
    #                         self.date, '%Y-%m-%d'):
    #                     count += 1
    #             loan2 = (count * work_day_count) * .5
    #             # doaa added loan_type condition
    #             if self.loan_amount > loan2 and self.loan_type == 'advance_salary':
    #                 raise ValidationError("You Cant Request Loan With This Amount")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    loan = fields.Float('loan')

    # @api.multi
    def compute_sheet(self):
        for rec in self:
            emp_obj = self.env['hr.loan'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'approve')])
            loan_total = 0
            for line in emp_obj.loan_lines:
                # changed by marwa osama related to task INV-38 to fix Loan Management not calculated correctly
                # if line.loan_amount and rec.date_from <= line.date <= rec.date_to:
                if line.amount and rec.date_from <= line.date <= rec.date_to:
                    loan_total += line.amount
            rec.loan = loan_total
        return super(HrPayslip, self).compute_sheet()

