# -*- coding: utf-8 -*-

from odoo import models, fields, api,_



class HrDepartment(models.Model):
    _inherit = 'hr.department'

    code = fields.Char(string='Code', size=64,copy=False)


    # override create function to add sequence code
    # remove sequence function and make field editable (task mms-10)
    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('hr.department.code')
        return super(HrDepartment, self).create(vals)