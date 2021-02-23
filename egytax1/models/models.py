# -*- coding: utf-8 -*-

from odoo import models, fields,api


class taxyear(models.Model):
    _name = 'egytax.taxyear'
    _rec_name='name'

    name = fields.Char()
    tax_examption = fields.Float()
    year_from = fields.Date()
    year_to = fields.Date()
    lines = fields.One2many('egytax.taxyear.line', 'taxyear_id', string="tax year lines")


class taxyearline(models.Model):
    _name = 'egytax.taxyear.line'

    taxyear_id = fields.Many2one('egytax.taxyear', ondelete='cascade', string="")
    lowwer = fields.Float()
    upper = fields.Float()
    percentage = fields.Float()
    examption_limit = fields.Float()

class payslip(models.Model):
    _inherit = 'hr.payslip'
    taxedsalary = fields.Float('Taxed Salary', compute='calc_taxed_salary')
    taxedsalary1 = fields.Float('Taxed Salary', )


    def compute_sheet(self):
        self.taxedsalary1=0
        return super(payslip, self).compute_sheet()


    def calc_taxed_salary(self):
        for rec in self:
            taxedsalary=0
            for line in rec.line_ids:
                if line.salary_rule_id.include:
                    taxedsalary = taxedsalary + (line.amount * line.qty * line.rate / 100.0)
            rec.taxedsalary=taxedsalary

class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    include= fields.Boolean('Include in eg incom tax')

    def _compute_rule(self,localdict):

        rule = self
        taxedsalary=0
        pp=localdict.get('payslip', False)
        if localdict.get('payslip', False):
            if self.code == 'ST':
                taxedsalary = pp.taxedsalary1
                emp = localdict['employee']
                contract = emp['contract_id'][0]
                # payslip object
                payslip = localdict.get('payslip', False)
                taxedsalary = taxedsalary
                payslip_date_from = payslip.date_from
                payslip_date_to = payslip.date_to
                tax_year_obj = self.env['egytax.taxyear']

                # get only one tax year object
                taxyear_ids = tax_year_obj.search( [
                    ('year_from', '<', payslip_date_from), ('year_to', '>', payslip_date_to)], order='id', limit=1,
                                                  )
                tax_limit_final = 0

                if taxyear_ids:
                    taxedsalary = taxedsalary * 12 - taxyear_ids[0].tax_examption
                    tax_year_lines_obj = self.env['egytax.taxyear.line']
                    tax_year_lines_ids = tax_year_lines_obj.search([
                        ('taxyear_id', '=', taxyear_ids[0].id)], order='id')

                    tax = 0.0
                    remain = 0.0
                    tax_line_chk = 0.0
                    tax_line_chk = taxedsalary
                    remain = taxedsalary

                    tax_def = 0
                    v_percentage = 0
                    # calculating the tax
                    for line in tax_year_lines_ids:
                        if tax_line_chk <= line.upper and tax_line_chk > line.lowwer:
                            v_percentage = line.percentage
                        if (taxedsalary > line.lowwer and taxedsalary <= line.upper):
                            tax = tax + remain * line.percentage / 100
                            remain = 0
                        else:
                            if remain != 0:
                                tax = tax + (line.upper - line.lowwer) * line.percentage / 100
                                remain = remain - (line.upper - line.lowwer)
                    if (remain > 0):
                        line = tax_year_lines_ids[-1]
                        tax = tax + remain * line.percentage / 100

         ###### added by marwa osama to apply examption limit related to task DT-39
                    for limit in tax_year_lines_ids:
                        if (limit.lowwer <= 0):
                            limit_taxedsalary = 0
                        else:

                            limit_taxedsalary = taxedsalary
                        if (limit_taxedsalary <= limit.upper and limit_taxedsalary > limit.lowwer):
                            tax_def = tax * limit.examption_limit / 100
                            tax_limit_final = round((tax - tax_def), 2)

                #changed by marwa osama return tax / 12, -1, 100
                return tax_limit_final / 12, -1, 100
    ###########################################
            else:
                amount, qty, rate = super(hr_salary_rule, self)._compute_rule(localdict)
                if (self.include):

                    taxedsalary = taxedsalary + (amount * qty * rate / 100.0)
                    pp.taxedsalary1+=taxedsalary
                return  amount, qty, rate
        else:
            amount, qty, rate = super(hr_salary_rule, self)._compute_rule(localdict)
            if (self.include):
                taxedsalary = taxedsalary + (amount * qty * rate / 100.0)
            return  amount, qty, rate
