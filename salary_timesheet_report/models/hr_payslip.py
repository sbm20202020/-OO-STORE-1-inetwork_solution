# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError
from odoo.tools import float_compare, float_is_zero

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'
    can_print=fields.Boolean(related='salary_rule_id.can_print')

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    can_print=fields.Boolean()
