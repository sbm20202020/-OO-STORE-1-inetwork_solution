# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _


class HREmployee(models.Model):

    _inherit = 'hr.employee'
    _description = "Generate employee sequence id"

    emp_id = fields.Char("Employee Id")
    emp_sequence_id = fields.Many2one('ir.sequence', 'Employee Sequence',default=lambda self: self.env['ir.sequence'].search([('code','=','seqemp.seqemp')]).id)

    def name_get(self):
        res = super(HREmployee, self).name_get()
        for employee in self:
            name = employee.name
            if employee.emp_id:
                name = "%s [%s]" % (employee.name, employee.emp_id)
            res.append((employee.id, name))
        return res

    @api.model
    def create(self, values):
        values['emp_id'] = self.env[
            'ir.sequence'].next_by_code('seqemp.seqemp')
        values['emp_sequence_id'] = self.env[
            'ir.sequence'].search([('code','=','seqemp.seqemp')]).id
        return super(HREmployee, self).create(values)



class HrContract(models.Model):
    _inherit= 'hr.contract'
    emp_id = fields.Char("Employee Id", related="employee_id.emp_id", store=True)
class HREmployeepuplic(models.Model):

    _inherit = 'hr.employee.public'
    emp_id = fields.Char("Employee Id")
    emp_sequence_id = fields.Many2one('ir.sequence', 'Employee Sequence',default=lambda self: self.env['ir.sequence'].search([('code','=','seqemp.seqemp')]).id)

