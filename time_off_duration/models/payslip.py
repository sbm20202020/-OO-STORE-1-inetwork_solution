# -*- coding: utf-8 -*-

from odoo import models, fields,api

from datetime import date, datetime, time
from collections import defaultdict
from odoo import api, fields, models
from odoo.tools import date_utils
class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _get_work_hours(self, date_from, date_to):
        """
        Returns the amount (expressed in hours) of work
        for a contract between two dates.
        If called on multiple contracts, sum work amounts of each contract.
        :param date_from: The start date
        :param date_to: The end date
        :returns: a dictionary {work_entry_id: hours_1, work_entry_2: hours_2}
        """

        generated_date_max = min(fields.Date.to_date(date_to), date_utils.end_of(fields.Date.today(), 'month'))
        self._generate_work_entries(date_from, generated_date_max)
        date_from = datetime.combine(date_from, datetime.min.time())
        date_to = datetime.combine(date_to, datetime.max.time())
        work_data = defaultdict(int)

        # First, found work entry that didn't exceed interval.
        work_entries = self.env['hr.work.entry'].read_group(
            [
                ('state', 'in', ['validated', 'draft','conflict']),
                ('date_start', '>=', date_from),
                ('date_stop', '<=', date_to),
                ('contract_id', 'in', self.ids),
            ],
            ['hours:sum(duration)'],
            ['work_entry_type_id']
        )
        work_data.update(
            {data['work_entry_type_id'][0] if data['work_entry_type_id'] else False: data['hours'] for data in
             work_entries})
        #Add by abeer
        # work_entries = self.env['hr.work.entry'].read_group(
        #     [
        #         ('state', 'in', ['conflict']),
        #         ('date_start', '>=', date_from),
        #         ('date_stop', '<=', date_to),
        #         ('contract_id', 'in', self.ids),
        #         ('is_overtime', '=', True),
        #     ],
        #     ['hours:sum(duration)'],
        #     ['work_entry_type_id']
        # )
        # work_data.update(
        #     {data['work_entry_type_id'][0] if data['work_entry_type_id'] else False: data['hours'] for data in
        #      work_entries})
        # Second, found work entry that exceed interval and compute right duration.
        work_entries = self.env['hr.work.entry'].search(
            [
                '&', '&',
                ('state', 'in', ['validated', 'draft']),
                ('contract_id', 'in', self.ids),
                '|', '|', '&', '&',
                ('date_start', '>=', date_from),
                ('date_start', '<', date_to),
                ('date_stop', '>', date_to),
                '&', '&',
                ('date_start', '<', date_from),
                ('date_stop', '<=', date_to),
                ('date_stop', '>', date_from),
                '&',
                ('date_start', '<', date_from),
                ('date_stop', '>', date_to),
            ]
        )

        for work_entry in work_entries:
            date_start = max(date_from, work_entry.date_start)
            date_stop = min(date_to, work_entry.date_stop)
            if work_entry.work_entry_type_id.is_leave:
                contract = work_entry.contract_id
                calendar = contract.resource_calendar_id
                contract_data = contract.employee_id._get_work_days_data(date_start, date_stop, compute_leaves=False,
                                                                         calendar=calendar)
                work_data[work_entry.work_entry_type_id.id] += contract_data.get('hours', 0)
            else:
                dt = date_stop - date_start
                work_data[work_entry.work_entry_type_id.id] += dt.days * 24 + dt.seconds / 3600  # Number of hours
        return work_data
class workEntryType(models.Model):
    _inherit ='hr.work.entry.type'
    is_overtime = fields.Boolean()
class workEntry(models.Model):
    _inherit ='hr.work.entry'
    is_overtime = fields.Boolean(compute='_compute_is_ovtime')
    def _compute_is_ovtime(self):
        for work in self:
            is_overtime=False
            if work.work_entry_type_id:
               if  work.work_entry_type_id.is_overtime ==True:
                   is_overtime=True
            work.is_overtime=is_overtime

    def _get_duration(self, date_start, date_stop):
        if not date_start or not date_stop:
            return 0
        if self.work_entry_type_id and (self.work_entry_type_id.is_leave or self.leave_id )and not self.is_overtime:
            calendar = self.contract_id.resource_calendar_id
            contract_data = self.contract_id.employee_id._get_work_days_data(date_start, date_stop, compute_leaves=False, calendar=calendar)
            return contract_data.get('hours', 0)
        elif self.work_entry_type_id and self.leave_id and self.is_overtime:
            contract = self.employee_id.contract_id
            calendar = contract.resource_calendar_id
            if  self.leave_id.holiday_status_id.request_unit=='day':
                return (self.leave_id.number_of_days * calendar.hours_per_day)
            #number_of_hours_display
            #
            else:
               return (self.leave_id.number_of_hours_display)
        else :
           dt = date_stop - date_start
           return dt.days * 24 + dt.seconds / 3600  # Number of hours
        #return super()._get_duration(date_start, date_stop)

class HrPayslip(models.Model):
    _inherit ='hr.payslip'
    def _get_worked_day_lines(self):
        res=super(HrPayslip, self)._get_worked_day_lines()
        lines = {}
        return res

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        res = super(HrPayslip, self)._onchange_employee()
        return res

