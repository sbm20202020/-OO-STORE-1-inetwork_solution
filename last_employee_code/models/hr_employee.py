# -*- coding: utf-8 -*-

from odoo import models, fields, api,_, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.osv import expression




class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    dep_code = fields.Char(related='department_id.code',string='Department Code')
    location_id=fields.Many2one('hr.location',string='Location',required=True)
    location_code = fields.Char(related='location_id.code',string='Location Code')
    last_employee_code=fields.Char(string='Last Employee Code',)
    code_con=fields.Char(string='Next Code')

    _sql_constraints = [
        ('code_con', 'unique (code_con)', 'Next Code must be unique!'),
    ]

    @api.constrains('code_con')
    def code_constraint_unique(self):
        for rec in self:
            if len(self.search([('code_con', '=', rec.code_con) ])) > 1:
                raise ValidationError(_('Next Code must be unique!'))



    # to get last code for employee that has the same department and location
    @api.onchange('location_id','department_id')
    def get_last_employee_code(self):
        for rec in self:
            if rec.department_id and rec.location_id:
                last_employee_id=self.env['hr.employee'].search([('department_id','=',rec.department_id.id),('location_id','=',rec.location_id.id)]).sorted(
                    key=lambda l: l.create_date)
                if last_employee_id:
                    last_employee = last_employee_id[-1]
                    last_code=last_employee.code_con
                    rec.last_employee_code=last_code
                    rec.code_con = str(last_code)

                else:
                    # rec.last_employee_code = str('1')
                    rec.code_con = str(rec.dep_code) + str(rec.location_code) + str('1')





    # to search by next code  in any m2o  field from employee model

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('code_con', 'ilike', name)]
        sat_code_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(sat_code_ids).with_user(name_get_uid))



class HrContract(models.Model):
    _inherit = 'hr.contract'

    renewal_date=fields.Date(string='Renewal Date')




class HrEmployeepublic(models.Model):
    _inherit = 'hr.employee.public'
    location_id = fields.Many2one('hr.location', string='Location', required=True)
    location_code = fields.Char(related='location_id.code', string='Location Code')
    last_employee_code = fields.Char(string='Last Employee Code', )
