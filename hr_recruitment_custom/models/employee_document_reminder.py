# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta



class EmployeeDocumentReminder(models.Model):
    _name = 'employee.document.reminder'

    def reminder(self):
        employees = self.env['hr.employee'].search([])
        for rec in employees:
            start_dt = fields.Datetime.from_string(rec.create_date)
            finish_dt = fields.Datetime.from_string(datetime.now())
            difference = relativedelta(finish_dt, start_dt)
            days = difference.days
            users=self.env['res.users'].search([])
            for user in users.filtered(lambda self:self.has_group('hr.group_hr_manager')):
                if days == 15 and rec.mobile_phone == False:
                        rec.activity_schedule('hr_recruitment_custom.schdule_activity_reminder_id',datetime.now().date(),
                                                      user_id=user.id,
                                                      summary='Please Add Work Mobile')
                if days == 30 and rec.Form1_Social_insurance == False:
                        rec.activity_schedule('hr_recruitment_custom.schdule_activity_reminder_id',datetime.now().date(),
                                                      user_id=user.id,
                                                      summary='Please Add Form 1 Social insurance')
                if days == 30 and rec.bank_account_id.id == False:
                        rec.activity_schedule('hr_recruitment_custom.schdule_activity_reminder_id',datetime.now().date(),
                                                      user_id=user.id,
                                                      summary='Please Add Bank Account Number')
                if days == 60 and rec.card_id == False:
                        rec.activity_schedule('hr_recruitment_custom.schdule_activity_reminder_id',datetime.now().date(),
                                                      user_id=user.id,
                                                      summary='Please Add ID Document')
                if days == 60 and rec.employee_contract == False:
                        rec.activity_schedule('hr_recruitment_custom.schdule_activity_reminder_id',datetime.now().date(),
                                                      user_id=user.id,
                                                      summary='Please Add Employee contract Document')

                if days == 60 and rec.military_certificate == False:
                        rec.activity_schedule('hr_recruitment_custom.schdule_activity_reminder_id',datetime.now().date(),
                                                      user_id=user.id,
                                                      summary='Please Add Military Certificate')

                if days == 60 and rec.driver_license == False:
                        rec.activity_schedule('hr_recruitment_custom.schdule_activity_reminder_id',datetime.now().date(),
                                                      user_id=user.id,
                                                      summary='Please Add Driver License')



