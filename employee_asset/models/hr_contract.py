# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, _, api, exceptions

class HrContract(models.Model):
    _inherit= 'hr.contract'

    allowances = fields.Float(string='Allowances')
    medical_insurance = fields.Float(string='Medical Insurance')
    phone_allowances = fields.Float(string='Phone-allowances')
    transfer_allowances = fields.Float(string='Transfer-allowances')

    @api.constrains('allowances','medical_insurance' , 'phone_allowances','transfer_allowances')
    def check_values(self):
        for rec in self:
            if rec.allowances < 0.0:
                raise ValidationError('Allowances value must be positive.')
            if rec.medical_insurance < 0.0:
                raise ValidationError('Medical Insurance value must be positive.')
            if rec.phone_allowances < 0.0:
                raise ValidationError('Phone-allowances value must be positive.')
            if rec.transfer_allowances < 0.0:
                raise ValidationError('Transfer-allowances value must be positive.')

