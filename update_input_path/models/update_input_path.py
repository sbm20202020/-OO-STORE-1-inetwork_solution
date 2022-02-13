# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError


class UpdateInputPath(models.Model):
    _name = 'update.input.path'
    employee_id = fields.Many2one('hr.employee',readonly=True)
    employee_code = fields.Integer(related="employee_id.id",store=True)
    code_con=fields.Char(related="employee_id.code_con",store=True,string='Next Code')
    job_title=fields.Char(related="employee_id.job_title",store=True)
    basic_wage = fields.Float(compute='_basic_wage',store=True)
    location_id = fields.Many2one('hr.location',related="employee_id.location_id",store=True)
    department_id=fields.Many2one('hr.department',related='employee_id.department_id',store=True)
    payslip = fields.Many2one('hr.payslip',readonly=True)
    payslip_run_id = fields.Many2one('hr.payslip.run',related='payslip.payslip_run_id',store=True)
    company_id = fields.Many2one('res.company',related='payslip.company_id',store=True)
    date = fields.Date()
    month = fields.Char()
    state = fields.Selection([('draft','Draft'),('confirm','Confirm')],default='draft',readonly=True)

    @api.depends('employee_id')
    def _basic_wage(self):
        for rec in self:
            contract=self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id)
                                                        ,('state','not in',['close','cancel'])],limit=1)
            rec.basic_wage=contract.wage

    def write(self, vals):
        res=super(UpdateInputPath, self).write(vals)
    # if 'my_many2many_field' in vals:
        self.env['ir.rule'].clear_caches()
        return res

    def action_draft(self):
        for rec in self:
            if rec.state != 'draft':
              rec.state='draft'
            else:
                raise ValidationError(_("you can't draft path %s is aleardy drafted") %(rec.payslip.name))



    def action_confirm(self):
        res={'value':[]}
        for rec in self:
            if rec.state == 'draft':
                for pay in rec.payslip:
                    for work_days in pay.worked_days_line_ids:
                        namefieldhours = 'x_' + str(work_days.work_entry_type_id.id) + '_hours'
                        namefielddays = 'x_' + str(work_days.work_entry_type_id.id) + '_days'
                        work_days.write({
                                'number_of_days': rec.read([namefielddays])[0][namefielddays],
                                'number_of_hours': rec.read([namefieldhours])[0][namefieldhours],

                            })

                    for input in pay.input_line_ids:
                        namefield = 'x_' + str(input.input_type_id.id)
                        input.write({
                                'amount': rec.read([namefield])[0][namefield],

                            })



                rec.state='confirm'

            elif rec.state == 'confirm':
                raise ValidationError(_("you can't confirm path %s is aleardy confirmed")%(rec.payslip.name))
