
import pytz
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY, \
    make_aware, datetime_to_string, string_to_datetime
import logging

_logger = logging.getLogger()

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"
class attendance_sheet_wizard(models.TransientModel):
    _name = "attendance.sheet.wizard"
    date_from = fields.Date(string='Date From', required=True,
                            default=lambda self: fields.Date.to_string(
                                date.today().replace(day=1)), )
    date_to = fields.Date(string='Date To', required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1,
                                                              days=-1)).date()))
    # company_id = fields.Many2one('res.company', string='Company',
    #                              copy=False, required=False,
    #                              default=lambda self: self.env.company,
    #                              )
    employees_ids = fields.Many2many(comodel_name="hr.employee", relation="hr_employees_rel", column1="id", column2="employee_id", string="Employees", )


    @api.constrains('date_from','date_to')
    def _check_date(self):
        for rec in self:
            if rec.date_from >=rec.date_to:
                raise ValidationError(
                    _('Date Form must be less than Date To'))


    def apply(self):
        domain=[('contract_id','!=',False)]
        employees=[]
        attendance_sheet_domain=[]
        att_sheet_ids = []
        # if self.company_id:
        #     domain=[('company_id', '=', self.company_id.id)]
        if self.employees_ids:
            domain +=[('id','in',self.employees_ids.ids)]
        # if self.department_ids:
        #     domain += [('department_id', 'in', self.department_ids.ids)]
        # if self.positions_ids:
        #     domain += [('job_id', 'in', self.positions_ids.ids)]
        employees_ids=self.env['hr.employee'].search(domain)
        for emp in employees_ids:
            if  emp.contract_id and emp.contract_id.state=='open':
                employees.append(emp)
        for emp in employees:
            # contracts = emp._get_contracts(self.date_from, self.date_to)
            contract_id = emp.contract_id
            name = 'Attendance Sheet - %s - %s' % (emp.name or '',
                                                        format_date(self.env,
                                                                    self.date_from,
                                                                    date_format="MMMM y"))
            if not contract_id:
                raise ValidationError(
                    _('There Is No Valid Contract For Employee %s' % emp.name))

            if not contract_id.att_policy_id:
                raise ValidationError(_(
                    "Employee %s does not have attendance policy" % emp.name))
            vals={'name':name,'employee_id':emp.id,'date_from':self.date_from,'date_to':self.date_to,'company_id':emp.company_id.id,'contract_id':contract_id.id,'att_policy_id':contract_id.att_policy_id.id}
            attendance_sheet=self.env['attendance.sheet'].create(vals)
            attendance_sheet.get_attendances()
            att_sheet_ids.append(attendance_sheet.id)
        attendance_sheet_domain=[('id','in',att_sheet_ids)]
        return {
            'domain': attendance_sheet_domain,
            'name': _('Attendace sheets'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'attendance.sheet',
            'type': 'ir.actions.act_window',
        }

