# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import calendar
from datetime import datetime, date


class EmployeeWork(models.Model):
    _name = 'employee.work'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name='employee_id'
    user_id = fields.Many2one(
        'res.users', string='person', index=True, tracking=2, default=lambda self: self.env.user,)
    employee_id =fields.Many2one('hr.employee',required=True,tracking=1,readonly=1, states={'draft': [('readonly', False)]})
    company_id=fields.Many2one('res.company',related='employee_id.company_id',store=True,tracking=3,)
    date=fields.Date(required=True,readonly=1, states={'draft': [('readonly', False)]})
    state=fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')],readonly=True,tracking=4,default='draft')
    type=fields.Selection([('input_type','Input'),('work_entry_type','Work Entry')],required=True,readonly=1, states={'draft': [('readonly', False)]})
    input_type_id=fields.Many2one('hr.payslip.input.type','Input Type',readonly=1, states={'draft': [('readonly', False)]},domain="[('input_path','=',True)]")
    amount=fields.Float(readonly=1, states={'draft': [('readonly', False)]})
    work_entry_type_id=fields.Many2one('hr.work.entry.type','Work Entry Type',domain="[('appear_on_payslip','=',True)]",readonly=1, states={'draft': [('readonly', False)]})
    number_of_days=fields.Float(readonly=1, states={'draft': [('readonly', False)]} )
    number_of_hours=fields.Float(readonly=1, states={'draft': [('readonly', False)]})
    date_day = fields.Char('Day',compute='_get_day_of_date',store=True)

    @api.depends('date')
    def _get_day_of_date(self):
        for r in self:
            if r.date != False:
               selected = fields.Datetime.from_string(r.date)
               r.date_day = calendar.day_name[selected.weekday()]

    @api.onchange('type','work_entry_type_id')
    def _change_type(self):
        for rec in self:
            if rec.type == False :
                rec.input_type_id =False
                rec.amount=0.0
                rec.number_of_days=0.0
                rec.number_of_hours=0.0
                rec.work_entry_type_id=False
            elif rec.type =='input_type' :
                rec.number_of_days=0.0
                rec.number_of_hours=0.0
                rec.work_entry_type_id=False
            elif rec.type == 'work_entry_type':
                rec.input_type_id =False
                rec.amount=0.0
                if rec.work_entry_type_id.code == 'WORK100':
                      rec.number_of_days = 29.0
                else:
                    rec.number_of_days = 0.0


    # fields

    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise ValidationError(_("you can't delete employee work is confirm"))

        return super(EmployeeWork, self).unlink()


    @api.constrains('amount','number_of_days','number_of_hours')
    def not_minus(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError(_('Amount should not minus.'))
            if rec.number_of_hours < 0:
                raise ValidationError(_('Number Of Hours should not minus.'))
            if rec.number_of_days < 0:
                raise ValidationError(_('Number Of Days should not minus.'))

    def set_to_draft(self):
        for rec in self:
          rec.write({'state': 'draft'})


    def cancel(self):
        for rec in self:
          rec.write({'state': 'cancel'})


    def confirm(self):
        for rec in self:
          rec.write({'state': 'confirm'})


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    employee_work_ids=fields.One2many('employee.work','employee_id')
