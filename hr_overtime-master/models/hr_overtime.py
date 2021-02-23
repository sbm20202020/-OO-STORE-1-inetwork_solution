# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-2015 Asmaa Aly.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import itertools
from lxml import etree
import time

import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Department(models.Model):
    _inherit = "hr.department"
    manager_id = fields.Many2one('hr.employee', string='Manager', track_visibility='onchange',
                                 domain="[('manager','=',True)]")

    @api.model
    def create(self, vals):
        res = super(Department, self).create(vals)
        if res.manager_id:
            se_manager = self.env['hr.employee'].search([('id', '=', res.manager_id.id)])
            se_manager_del = self.env['hr.employee'].search(
                [('manager', '=', True), ('department_id', '=', res.parent_id.id)])

            if se_manager and se_manager_del:

                for line in se_manager_del:
                    line.write({'department_id': False, 'parent_id': False})

                se_manager.write({'department_id': res.parent_id.id, 'parent_id': res.parent_id.manager_id.id})

            if se_manager and not se_manager_del:
                se_manager.write({'department_id': res.parent_id.id, 'parent_id': res.parent_id.manager_id.id})

        return res

    # @api.multi
    def write(self, vals):
        res = super(Department, self).write(vals)
        if self.manager_id:
            se_manager = self.env['hr.employee'].search([('id', '=', self.manager_id.id)])
            se_manager_del = self.env['hr.employee'].search(
                [('manager', '=', True), ('department_id', '=', self.parent_id.id)])

            if se_manager and se_manager_del:

                for line in se_manager_del:
                    line.write({'department_id': False, 'parent_id': False})

                se_manager.write({'department_id': self.parent_id.id, 'parent_id': self.parent_id.manager_id.id})

            if se_manager and not se_manager_del:
                se_manager.write({'department_id': self.parent_id.id, 'parent_id': self.parent_id.manager_id.id})

        return res


class hr_employee(models.Model):
    _inherit = "hr.employee"
    parent_id = fields.Many2one('hr.employee', 'Manager', domain="[('manager','=',True)]")
    manager = fields.Boolean()


class hr_overtime(models.Model):
    _name = "hr.overtime"
    _inherit = ['mail.thread']
    _description = "HR Overtime"

    activity_ids = fields.One2many('mail.activity', 'calendar_event_id', string='Activities')

    @api.depends('to_date', 'from_date')
    def compute_total(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        for rec in self:
            if rec.from_date != False and rec.to_date != False:
                from_date = datetime.strptime(str(rec.from_date), DATETIME_FORMAT)
                to_date = datetime.strptime(str(rec.to_date), DATETIME_FORMAT)
                timedelta = to_date - from_date
                diff_day = (float(timedelta.seconds) / 86400) * 24
                rec.total_time = diff_day
                if rec.payment_type == 'time' and rec.total_time == 0.0:
                    raise ValidationError(
                        _('total time is 0 you should greater than 0.'))
                from_date1 = datetime.strftime(rec.from_date, '%Y-%m-%d %H-%M-%S')
                to_date1 = datetime.strftime(rec.to_date, '%Y-%m-%d %H-%M-%S')
                if from_date1 > to_date1:
                    raise ValidationError(
                        _('From Date should not greater than To Date.'))

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    name = fields.Char(string="Name", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    reason = fields.Text(string="Overtime Reason")
    from_date = fields.Datetime(srting="From Date", required=True)
    to_date = fields.Datetime(srting="To Date", required=True)
    # actaul_leave_time = fields.Datetime(string="Actual Leave Time", readonly=True)
    total_time = fields.Float(string="Total Time", compute='compute_total', store=True)
    type = fields.Selection([
        ('official_leave', 'Official Leave'),
        ('working_day', 'Working Day'),
        ('weekend', 'WeekEnd'),
    ], string="Overtime Type")
    cash = fields.Integer()
    payment_type = fields.Selection([('time', 'Time'),
                                     ('cash', 'Cash'), ], required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('declined', 'Declined'),
    ], string="Status", default="draft")

    @api.onchange('payment_type')
    def empty(self):
        if self.payment_type == 'time':
            self.cash = 0.0
        if self.payment_type == 'cash':
            self.total_time = 0.0
        if self.payment_type == False:
            self.total_time = 0.0
            self.cash = 0.0

    @api.constrains('cash')
    def not_minus(self):
        for rec in self:
            if rec.cash < 0:
                raise ValidationError(_('Cash is not minus'))
            if rec.cash == 0 and rec.payment_type == 'cash':
                raise ValidationError(_('Cash is not zero'))

    # @api.multi
    def unlink(self):
        for line in self:
            if line.state == 'submit' or line.state == 'approve' or line.state == 'declined':
                raise ValidationError(_('you can not delete overtime that is submit or approve or declined.'))

        return super(hr_overtime, self).unlink()

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('hr.ov.req') or '/'
        values['name'] = seq
        res = super(hr_overtime, self).create(values)
        from_date = datetime.strftime(res.from_date, '%H:%M:%S')
        to_date = datetime.strftime(res.to_date, '%H:%M:%S')
        from_date2 = datetime.strftime(res.from_date, '%Y-%m-%d')
        to_date2 = datetime.strftime(res.to_date, '%Y-%m-%d')
        print(from_date, to_date, from_date2, to_date2)
        search_overtime = self.search(
            [('employee_id', '=', res.employee_id.id), ('id', '!=', res.id), ('state', '!=', 'declined')])
        print(search_overtime)

        if search_overtime:
            for line in search_overtime:
                if datetime.strftime(line.from_date, '%Y-%m-%d') == from_date2 and datetime.strftime(line.to_date,
                                                                                                     '%Y-%m-%d') == to_date2 and datetime.strftime(
                        line.from_date, "%H:%M:%S") <= from_date and datetime.strftime(line.to_date,
                                                                                       "%H:%M:%S") >= to_date \
                        or datetime.strftime(line.from_date, '%Y-%m-%d') == from_date2 and datetime.strftime(
                            line.to_date, '%Y-%m-%d') == to_date2 and datetime.strftime(line.from_date,
                                                                                        "%H:%M:%S") <= from_date and datetime.strftime(
                            line.to_date, "%H:%M:%S") <= to_date:
                    raise ValidationError(
                        _('do not allow to create two overtime in the same time and the same employee.'))
        return res

    # @api.multi
    def write(self, values):
        res = super(hr_overtime, self).write(values)
        from_date = datetime.strftime(self.from_date, '%H:%M:%S')
        to_date = datetime.strftime(self.to_date, '%H:%M:%S')
        from_date2 = datetime.strftime(self.from_date, '%Y-%m-%d')
        to_date2 = datetime.strftime(self.to_date, '%Y-%m-%d')
        search_overtime = self.search(
            [('employee_id', '=', self.employee_id.id), ('id', '!=', self.id), ('state', '!=', 'declined')])
        if search_overtime:
            for line in search_overtime:
                if datetime.strftime(line.from_date, '%Y-%m-%d') == from_date2 and datetime.strftime(line.to_date,
                                                                                                     '%Y-%m-%d') == to_date2 and datetime.strftime(
                        line.from_date, "%H:%M:%S") <= from_date and datetime.strftime(line.to_date,
                                                                                       "%H:%M:%S") >= to_date \
                        or datetime.strftime(line.from_date, '%Y-%m-%d') == from_date2 and datetime.strftime(
                            line.to_date, '%Y-%m-%d') == to_date2 and datetime.strftime(line.from_date,
                                                                                        "%H:%M:%S") <= from_date and datetime.strftime(
                            line.to_date, "%H:%M:%S") <= to_date:
                    raise ValidationError(
                        _('do not allow to create two overtime in the same time and the same employee.'))

        return res

    # @api.multi
    def action_sumbit(self):
        return self.write({'state': 'submit'})

    # @api.multi
    def action_approve(self):
        return self.write({'state': 'approve'})

    # @api.multi
    def action_set_to_draft(self):
        return self.write({'state': 'declined'})

    # @api.multi
    def action_set_to_drafts(self):
        return self.write({'state': 'draft'})

    @api.onchange('from_date', 'employee_id')
    def onchange_from_date(self):
        day_list = []
        type = ''
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.from_date:
            contract_id = self.env['hr.employee'].sudo().browse(self.employee_id.id).contract_id.id
            for con in self.env['hr.contract'].sudo().browse(contract_id):
                for con_day in con.resource_calendar_id.attendance_ids:
                    day_list.append(con_day.dayofweek)
            request_date = datetime.strptime(str(self.from_date), DATETIME_FORMAT).date()
            request_day = request_date.weekday()
            if str(request_day) in day_list:
                type = 'working_day'
            else:
                type = 'weekend'
            self.type = type


class hr_overtime_structure(models.Model):
    _name = "hr.overtime.structure"
    _inherit = ['mail.thread']
    _description = "Overtime Structure"

    name = fields.Char(string="Structure Name")
    code = fields.Char(string="Code", required=True)
    department_ids = fields.Many2many('hr.department', string="Department (s)")
    overtime_method = fields.Selection([
        ('ov_request', 'According to Request'),
        ('ov_attendance', 'According to Attendance'),
    ], string="Overtime Method", required=True)
    hr_ov_structure_rule_ids = fields.One2many('hr.ov.structure.rule', 'hr_overtime_structure_id',
                                               string="Overtime Structure Line")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('apply', 'Applied')
    ], string="Status", default="draft")

    @api.model
    def create(self, values):
        values['name'] = str(values['name']) + "( " + str(values['code']) + " )"
        res = super(hr_overtime_structure, self).create(values)
        return res

    # @api.one
    def apply_ov_structure(self):
        dep_list = []
        emp_list = []
        for dep in self.department_ids:
            dep_list.append(dep.id)
        employee_ids = self.env['hr.employee'].search([('department_id', 'in', dep_list)])
        for emp in employee_ids:
            emp_list.append(emp.id)
        contract_ids = self.env['hr.contract'].sudo().search([('employee_id', 'in', emp_list)])
        for contract in contract_ids:
            contract.write({'overtime_structure_id': self.id})
        self.write({'state': 'apply'})


class hr_ov_structure_rule(models.Model):
    _name = "hr.ov.structure.rule"
    _description = "Overtime Structure Rule"

    type = fields.Selection([
        ('official_leave', 'Official Leave'),
        ('working_day', 'Working Day'),
        ('weekend', 'WeekEnd')
    ], string="Overtime Type", default="working_day")

    rate = fields.Float(string="Rate", widget="float_time", required=True, default=1)
    begin_after = fields.Float(string="Begin After")

    hr_overtime_structure_id = fields.Many2one('hr.overtime.structure', string="Overtime Structure Ref.",
                                               ondelete='cascade')


class hr_contract(models.Model):
    _inherit = "hr.contract"

    overtime_structure_id = fields.Many2one('hr.overtime.structure', string="Overtime Structure")


class hr_payroll(models.Model):
    _inherit = 'hr.payslip'
    cash = fields.Float()
    days = fields.Float()

    # @api.multi
    def compute_sheet(self):
        for payslip in self:
            se_cash = self.env['hr.overtime'].search(
                [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'approve')])
            time = 0
            cash = 0
            for line in se_cash:
                if line.payment_type == 'time' and datetime.strftime(line.from_date, '%Y-%m-%d') >= datetime.strftime(
                        payslip.date_from, '%Y-%m-%d') and \
                                datetime.strftime(line.to_date, '%Y-%m-%d') <= datetime.strftime(payslip.date_to,
                                                                                                 '%Y-%m-%d'):
                    time += line.total_time

                if line.payment_type == 'cash' and datetime.strftime(line.from_date, '%Y-%m-%d') >= datetime.strftime(
                        payslip.date_from, '%Y-%m-%d') and \
                                datetime.strftime(line.to_date, '%Y-%m-%d') <= datetime.strftime(payslip.date_to,
                                                                                                 '%Y-%m-%d'):
                    cash += line.cash

            payslip.days = time
            payslip.cash = cash

        return super(hr_payroll, self).compute_sheet()
