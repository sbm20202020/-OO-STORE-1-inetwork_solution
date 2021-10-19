# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pytz
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY, \
    make_aware, datetime_to_string, string_to_datetime
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    # checkin_device_id = fields.Many2one('attendance.device', string='Checkin Device', readonly=False, index=True,
    #                                     help='The device with which user took check in action')
    # checkout_device_id = fields.Many2one('attendance.device', string='Checkout Device', readonly=False, index=True,
    #                                      help='The device with which user took check out action')
class hr_absence_rule_line(models.Model):
    _inherit = 'hr.absence.rule.line'
    times = [
        ('1', 'First Time'),
        ('2', 'Second Time'),
        ('3', 'Third Time'),
        ('4', 'Fourth Time'),
        ('5', 'Fifth Time'),
        ('6', 'Sixth Time'),
        ('7', 'Seventh Time'),
        ('8', 'Eighth Time'),
        ('9', 'Ninth Time'),
        ('10', 'Tenth Time'),


    ]
    counter = fields.Selection(string="Times", selection=times, required=True, )
class hrAttandancePolicy(models.Model):

    _inherit = 'hr.overtime.rule'
    first_sign_out= fields.Selection([
        ('0', '12:00 AM'), ('0.5', '0:30 AM'),
        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
        ('12', '12:00 PM'), ('12.5', '0:30 PM'),
        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
        ('23', '11:00 PM'), ('23.5', '11:30 PM')], string='First Sign Out')
    sec_sign_out = fields.Selection([
        ('0', '12:00 AM'), ('0.5', '0:30 AM'),
        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
        ('12', '12:00 PM'), ('12.5', '0:30 PM'),
        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
        ('23', '11:00 PM'), ('23.5', '11:30 PM')], string='Second Sign out')
    rate_ids = fields.One2many(comodel_name="hr.overtime.hour", inverse_name="overtime_id", string="Rates", required=False, )


class hrovertime(models.Model):
    _name = 'hr.overtime.hour'
    _rec_name = 'to_time'

    to_time = fields.Float(string="Hour To", required=False, )
    from_time = fields.Float(string="Hour From", required=False, )
    request_hour_from = fields.Selection([
        ('0', '12:00 AM'), ('0.5', '0:30 AM'),
        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
        ('12', '12:00 PM'), ('12.5', '0:30 PM'),
        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
        ('23', '11:00 PM'), ('23.5', '11:30 PM')], string='Hour from')
    request_hour_to = fields.Selection([
        ('0', '12:00 AM'), ('0.5', '0:30 AM'),
        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
        ('12', '12:00 PM'), ('12.5', '0:30 PM'),
        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
        ('23', '11:00 PM'), ('23.5', '11:30 PM')], string='Hour to')
    rate = fields.Float(string='Rate')
    overtime_id = fields.Many2one(comodel_name="hr.overtime.rule", string="overtime", required=False, )
    # @api.constrains('to_time', 'from_time')
    # def check_time(self):
    #     for sheet in self:
    #         if self.from_time>self.to_time:
    #            raise ValidationError(
    #                     _('From time must be less than to time ' ))
    #         if self.from_time >24:
    #             raise ValidationError(
    #                 _('From time must be less than 24 '))
    #         if self.from_time <1:
    #             raise ValidationError(
    #                 _('From time must be positive number '))
    #         if self.to_time > 24:
    #             raise ValidationError(
    #                 _('to time must be less than or equal 24 '))
    #         if self.to_time < 1:
    #             raise ValidationError(
    #                 _('to time must be positive number '))

class HrAttendancePolicy(models.Model):
    _inherit = 'hr.attendance.policy'

    def get_absence(self, period, cnt):
        res = period
        flag = False
        if self:
            abs_ids=[]
            if self.absence_rule_id:
                abs_ids = self.absence_rule_id.line_ids.sorted(key=lambda r: int(r.counter), reverse=True)
                #abs_ids = self.absence_rule_id.line_ids
                # for line in self.absence_rule_id.line_ids:
                #     abs_ids.append(line.counter)
                # abs_ids.sort()
                #
                for ln in abs_ids:
                    # print(ln.counter)
                    if cnt >= int(ln.counter):
                        res = ln.rate * period
                        # print('rate', cnt, ln.counter, ln.rate)
                        flag = True
                        break
                if not flag:
                    res = 0
        return res
    def get_overtime(self):
        self.ensure_one()
        res = {}
        if self:
            overtime_ids = self.overtime_rule_ids
            wd_ot_id = self.overtime_rule_ids.search(
                [('type', '=', 'workday'), ('id', 'in', overtime_ids.ids)],
                order='id', limit=1)
            we_ot_id = self.overtime_rule_ids.search(
                [('type', '=', 'weekend'), ('id', 'in', overtime_ids.ids)],
                order='id', limit=1)
            ph_ot_id = self.overtime_rule_ids.search(
                [('type', '=', 'ph'), ('id', 'in', overtime_ids.ids)],
                order='id', limit=1)
            if wd_ot_id:
                res['wd_rate'] = wd_ot_id.rate
                res['wd_after'] = wd_ot_id.rate_ids
                res['wd_f_sign_out'] = wd_ot_id.first_sign_out
                res['wd_sec_sign_out'] = wd_ot_id.sec_sign_out



            else:
                res['wd_Frate'] = 1
                res['wd_after'] = []
                res['wd_f_sign_out'] =0
                res['wd_sec_sign_out'] =0

            if we_ot_id:
                res['we_rate'] = we_ot_id.rate
                res['we_after'] = we_ot_id.active_after

            else:
                res['we_rate'] = 1
                res['we_after'] = []


            if ph_ot_id:
                res['ph_rate'] = ph_ot_id.rate
                res['ph_after'] = ph_ot_id.active_after

            else:
                res['ph_rate'] = 1
                res['ph_after'] = []

        else:
            res['wd_rate'] = res['wd_rate'] = res['ph_rate'] = 1
            res['wd_after'] = res['we_after'] = res['ph_after']= []
            res['wd_f_sign_out']=  res['wd_sec_sign_out'] = 0

        return res
class AttendanceSheet(models.Model):
    _inherit = 'attendance.sheet'

    def get_attendances(self):
        for att_sheet in self:
            contract = att_sheet.contract_id
            att_sheet.line_ids.unlink()
            att_line = self.env["attendance.sheet.line"]
            from_date = att_sheet.date_from
            to_date = att_sheet.date_to
            emp = att_sheet.employee_id
            tz = pytz.timezone(emp.tz)
            if not tz:
                raise exceptions.Warning(
                    "Please add time zone for employee : %s" % emp.name)
            calendar_id = emp.contract_id.resource_calendar_id
            if not calendar_id:
                raise ValidationError(_(
                    'Please add working hours to the %s `s contract ' % emp.name))
            policy_id = att_sheet.att_policy_id
            if not policy_id:
                raise ValidationError(_(
                    'Please add Attendance Policy to the %s `s contract ' % emp.name))

            all_dates = [(from_date + timedelta(days=x)) for x in
                         range((to_date - from_date).days + 1)]
            abs_cnt = 0
            for day in all_dates:
                day_start = datetime(day.year, day.month, day.day)
                day_end = day_start.replace(hour=23, minute=59,
                                            second=59)
                day_str = str(day.weekday())
                date = day.strftime('%Y-%m-%d')
                if contract.multi_shift:
                    work_intervals = att_sheet.employee_id.get_employee_shifts(
                        day_start,
                        day_end, tz)
                    work_intervals = calendar_id.att_interval_clean(
                        work_intervals)

                else:
                    work_intervals = calendar_id.att_get_work_intervals(
                        day_start,
                        day_end, tz)
                attendance_intervals = self.get_attendance_intervals(emp,
                                                                     day_start,
                                                                     day_end,
                                                                     tz)
                leaves = self._get_emp_leave_intervals(emp, day_start, day_end)
                public_holiday = self.get_public_holiday(date, emp)
                reserved_intervals = []
                overtime_policy = policy_id.get_overtime()
                abs_flag = False
                if work_intervals:
                    if public_holiday:
                        if attendance_intervals:
                            for attendance_interval in attendance_intervals:
                                overtime = attendance_interval[1] - \
                                           attendance_interval[0]
                                float_overtime = overtime.total_seconds() / 3600
                                if float_overtime <= overtime_policy[
                                    'ph_after']:
                                    act_float_overtime = float_overtime = 0
                                else:
                                    act_float_overtime = (float_overtime -
                                                          overtime_policy[
                                                              'ph_after'])
                                    float_overtime = (float_overtime -
                                                      overtime_policy[
                                                          'ph_after']) * \
                                                     overtime_policy['ph_rate']
                                ac_sign_in = pytz.utc.localize(
                                    attendance_interval[0]).astimezone(tz)
                                float_ac_sign_in = self._get_float_from_time(
                                    ac_sign_in)
                                ac_sign_out = pytz.utc.localize(
                                    attendance_interval[1]).astimezone(tz)
                                worked_hours = attendance_interval[1] - \
                                               attendance_interval[0]
                                float_worked_hours = worked_hours.total_seconds() / 3600
                                float_ac_sign_out = float_ac_sign_in + float_worked_hours
                                values = {
                                    'date': date,
                                    'day': day_str,
                                    'ac_sign_in': float_ac_sign_in,
                                    'ac_sign_out': float_ac_sign_out,
                                    'worked_hours': float_worked_hours,
                                    'overtime': float_overtime,
                                    'act_overtime': act_float_overtime,
                                    'att_sheet_id': self.id,
                                    'status': 'ph',
                                    'note': _("working on Public Holiday")
                                }
                                att_line.create(values)
                        else:
                            values = {
                                'date': date,
                                'day': day_str,
                                'att_sheet_id': self.id,
                                'status': 'ph',
                            }
                            att_line.create(values)
                    else:
                        for i, work_interval in enumerate(work_intervals):
                            float_worked_hours = 0
                            att_work_intervals = []
                            diff_intervals = []
                            late_in_interval = []
                            diff_time = timedelta(hours=00, minutes=00,
                                                  seconds=00)
                            late_in = timedelta(hours=00, minutes=00,
                                                seconds=00)
                            overtime = timedelta(hours=00, minutes=00,
                                                 seconds=00)
                            for j, att_interval in enumerate(
                                    attendance_intervals):
                                if max(work_interval[0], att_interval[0]) < min(
                                        work_interval[1], att_interval[1]):
                                    current_att_interval = att_interval
                                    if i + 1 < len(work_intervals):
                                        next_work_interval = work_intervals[
                                            i + 1]
                                        if max(next_work_interval[0],
                                               current_att_interval[0]) < min(
                                            next_work_interval[1],
                                            current_att_interval[1]):
                                            split_att_interval = (
                                                next_work_interval[0],
                                                current_att_interval[1])
                                            current_att_interval = (
                                                current_att_interval[0],
                                                next_work_interval[0])
                                            attendance_intervals[
                                                j] = current_att_interval
                                            attendance_intervals.insert(j + 1,
                                                                        split_att_interval)
                                    att_work_intervals.append(
                                        current_att_interval)
                            reserved_intervals += att_work_intervals
                            pl_sign_in = self._get_float_from_time(
                                pytz.utc.localize(work_interval[0]).astimezone(
                                    tz))
                            pl_sign_out = self._get_float_from_time(
                                pytz.utc.localize(work_interval[1]).astimezone(
                                    tz))
                            pl_sign_in_time = pytz.utc.localize(
                                work_interval[0]).astimezone(tz)
                            pl_sign_out_time = pytz.utc.localize(
                                work_interval[1]).astimezone(tz)
                            ac_sign_in = 0
                            ac_sign_out = 0
                            status = ""
                            note = ""
                            if att_work_intervals:
                                if len(att_work_intervals) > 1:
                                    # print("there is more than one interval for that work interval")
                                    late_in_interval = (
                                        work_interval[0],
                                        att_work_intervals[0][0])
                                    overtime_interval = (
                                        work_interval[1],
                                        att_work_intervals[-1][1])
                                    if overtime_interval[1] < overtime_interval[
                                        0]:
                                        overtime = timedelta(hours=0, minutes=0,
                                                             seconds=0)
                                    else:
                                        overtime = overtime_interval[1] - \
                                                   overtime_interval[0]
                                    remain_interval = (
                                        att_work_intervals[0][1],
                                        work_interval[1])
                                    # print'first remain intervals is',remain_interval
                                    for att_work_interval in att_work_intervals:
                                        float_worked_hours += (
                                                                      att_work_interval[
                                                                          1] -
                                                                      att_work_interval[
                                                                          0]).total_seconds() / 3600
                                        # print'float worked hors is', float_worked_hours
                                        if att_work_interval[1] <= \
                                                remain_interval[0]:
                                            continue
                                        if att_work_interval[0] >= \
                                                remain_interval[1]:
                                            break
                                        if remain_interval[0] < \
                                                att_work_interval[0] < \
                                                remain_interval[1]:
                                            diff_intervals.append((
                                                remain_interval[
                                                    0],
                                                att_work_interval[
                                                    0]))
                                            remain_interval = (
                                                att_work_interval[1],
                                                remain_interval[1])
                                    if remain_interval and remain_interval[0] <= \
                                            work_interval[1]:
                                        diff_intervals.append((remain_interval[
                                                                   0],
                                                               work_interval[
                                                                   1]))
                                    ac_sign_in = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              0]).astimezone(
                                            tz))
                                    ac_sign_out = self._get_float_from_time(
                                        pytz.utc.localize(
                                            att_work_intervals[-1][
                                                1]).astimezone(tz))
                                    ac_sign_out = ac_sign_in + ((
                                                                        att_work_intervals[
                                                                            -1][
                                                                            1] -
                                                                        att_work_intervals[
                                                                            0][
                                                                            0]).total_seconds() / 3600)
                                else:
                                    late_in_interval = (
                                        work_interval[0],
                                        att_work_intervals[0][0])
                                    overtime_interval = (
                                        work_interval[1],
                                        att_work_intervals[-1][1])
                                    if overtime_interval[1] < overtime_interval[
                                        0]:
                                        overtime = timedelta(hours=0, minutes=0,
                                                             seconds=0)
                                        diff_intervals.append((
                                            overtime_interval[
                                                1],
                                            overtime_interval[
                                                0]))
                                    else:
                                        overtime = overtime_interval[1] - \
                                                   overtime_interval[0]
                                    ac_sign_in = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              0]).astimezone(
                                            tz))
                                    ac_sign_out = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              1]).astimezone(
                                            tz))
                                    worked_hours = att_work_intervals[0][1] - \
                                                   att_work_intervals[0][0]
                                    float_worked_hours = worked_hours.total_seconds() / 3600
                                    ac_sign_out = ac_sign_in + float_worked_hours
                            else:
                                late_in_interval = []
                                diff_intervals.append(
                                    (work_interval[0], work_interval[1]))

                                status = "ab"
                            if diff_intervals:
                                for diff_in in diff_intervals:
                                    if leaves:
                                        status = "leave"
                                        diff_clean_intervals = calendar_id.att_interval_without_leaves(
                                            diff_in, leaves)
                                        for diff_clean in diff_clean_intervals:
                                            diff_time += diff_clean[1] - \
                                                         diff_clean[0]
                                    else:
                                        diff_time += diff_in[1] - diff_in[0]
                            if late_in_interval:
                                if late_in_interval[1] < late_in_interval[0]:
                                    late_in = timedelta(hours=0, minutes=0,
                                                        seconds=0)
                                else:
                                    if leaves:
                                        late_clean_intervals = calendar_id.att_interval_without_leaves(
                                            late_in_interval, leaves)
                                        for late_clean in late_clean_intervals:
                                            late_in += late_clean[1] - \
                                                       late_clean[0]
                                    else:
                                        late_in = late_in_interval[1] - \
                                                  late_in_interval[0]
                            float_overtime = overtime.total_seconds() / 3600
                            # if float_overtime <= overtime_policy['wd_after']:
                            #     act_float_overtime = float_overtime = 0
                            # else:
                            #     act_float_overtime = float_overtime
                            #     float_overtime = float_overtime * \
                            #                      overtime_policy[
                            #                          'wd_rate']
                            tem_sign_out = ac_sign_out  # add overtime based on signout
                            if overtime_policy['wd_after']:
                                f_tem_overtime = 0
                                f_tem_overtime_value = 0
                                s_tem_overtime = 0
                                s_tem_overtime_value = 0
                                float_overtime_line = 0
                                flag = False
                                flag1 = False
                                first_sign_out = float(overtime_policy['wd_f_sign_out'])
                                sec_sign_out = float(overtime_policy['wd_sec_sign_out'])
                                if float(first_sign_out) <= 12:
                                    first_sign_out += 24
                                if float(sec_sign_out) <= 12:
                                    sec_sign_out += 24
                                for line in overtime_policy['wd_after']:
                                    hour_from = float(float(line.request_hour_from))
                                    hour_to = float(line.request_hour_to)
                                    if float(line.request_hour_to) <= 12:
                                        hour_to += 24
                                    if ac_sign_out >= float(first_sign_out) and flag == False:
                                        tem_sign_out = float(first_sign_out)
                                        f_tem_overtime = float(first_sign_out) - pl_sign_out
                                        if tem_sign_out >= float(line.request_hour_from) and tem_sign_out <= hour_to:
                                            f_tem_overtime_value = f_tem_overtime * line.rate
                                            flag = True
                                            # print('temp', f_tem_overtime, f_tem_overtime_value)
                                    elif ac_sign_out >= float(sec_sign_out) and flag1 == False:
                                        if float(sec_sign_out) > float(first_sign_out):
                                            tem_sign_out = float(sec_sign_out)
                                            s_tem_overtime = float(sec_sign_out) - float(first_sign_out)
                                            if tem_sign_out >= float(line.request_hour_from) and tem_sign_out <= hour_to:
                                                s_tem_overtime_value = s_tem_overtime * line.rate
                                                flag1 = True
                                                # print('sectemp', s_tem_overtime, s_tem_overtime_value)
                                    elif ac_sign_out >= float(line.request_hour_from) and ac_sign_out <= hour_to:
                                        act_float_overtime = float_overtime
                                        float_overtime1 = float_overtime - (f_tem_overtime + s_tem_overtime)
                                        float_overtime_line = float_overtime1 * line.rate
                                float_overtime_line = float_overtime_line + f_tem_overtime_value + s_tem_overtime_value
                                float_overtime_hour = s_tem_overtime + f_tem_overtime + float_overtime1
                                if float_overtime_line > 0:
                                    float_overtime = float_overtime_line
                                    act_float_overtime = float_overtime
                                else:
                                    act_float_overtime = float_overtime = 0
                            else:
                                act_float_overtime = float_overtime = 0
                            float_late = late_in.total_seconds() / 3600
                            act_float_late = late_in.total_seconds() / 3600
                            policy_late = policy_id.get_late(float_late)
                            float_diff = diff_time.total_seconds() / 3600
                            if status == 'ab':
                                if not abs_flag:
                                    abs_cnt += 1
                                abs_flag = True

                                act_float_diff = float_diff
                                float_diff = policy_id.get_absence(float_diff,
                                                                   abs_cnt)
                            else:
                                act_float_diff = float_diff
                                float_diff = policy_id.get_diff(float_diff)
                            values = {
                                'date': date,
                                'day': day_str,
                                'pl_sign_in': pl_sign_in,
                                'pl_sign_out': pl_sign_out,
                                'ac_sign_in': ac_sign_in,
                                'ac_sign_out': ac_sign_out,
                                'late_in': policy_late,
                                'act_late_in': act_float_late,
                                'worked_hours': float_worked_hours,
                                'overtime': float_overtime,
                                'act_overtime': act_float_overtime,
                                'diff_time': float_diff,
                                'act_diff_time': act_float_diff,
                                'status': status,
                                'att_sheet_id': self.id
                            }
                            att_line.create(values)
                        out_work_intervals = [x for x in attendance_intervals if
                                              x not in reserved_intervals]
                        if out_work_intervals:
                            for att_out in out_work_intervals:
                                overtime = att_out[1] - att_out[0]
                                ac_sign_in = self._get_float_from_time(
                                    pytz.utc.localize(att_out[0]).astimezone(
                                        tz))
                                ac_sign_out = self._get_float_from_time(
                                    pytz.utc.localize(att_out[1]).astimezone(
                                        tz))
                                float_worked_hours = overtime.total_seconds() / 3600
                                ac_sign_out = ac_sign_in + float_worked_hours
                                float_overtime = overtime.total_seconds() / 3600
                                tem_sign_out = ac_sign_out  # add overtime based on signout
                                if overtime_policy['wd_after']:
                                    f_tem_overtime = 0
                                    f_tem_overtime_value = 0
                                    s_tem_overtime = 0
                                    s_tem_overtime_value = 0
                                    float_overtime_line = 0
                                    flag = False
                                    flag1 = False
                                    first_sign_out = float(overtime_policy['wd_f_sign_out'])
                                    sec_sign_out = float(overtime_policy['wd_sec_sign_out'])
                                    if float(first_sign_out) <= 12:
                                        first_sign_out += 24
                                    if float(sec_sign_out) <= 12:
                                        sec_sign_out += 24
                                    for line in overtime_policy['wd_after']:
                                        hour_from = float(float(line.request_hour_from))
                                        hour_to = float(line.request_hour_to)
                                        if float(line.request_hour_to) <= 12:
                                            hour_to += 24
                                        if ac_sign_out >= float(first_sign_out) and flag == False:
                                            tem_sign_out = float(first_sign_out)
                                            f_tem_overtime = float(first_sign_out) - pl_sign_out
                                            if float(line.request_hour_from) <= tem_sign_out <= hour_to:
                                                f_tem_overtime_value = f_tem_overtime * line.rate
                                                flag = True
                                                # print('temp', f_tem_overtime, f_tem_overtime_value)
                                        elif ac_sign_out >= float(sec_sign_out) and flag1 == False:
                                            if float(sec_sign_out) > float(first_sign_out):
                                                tem_sign_out = float(sec_sign_out)
                                                s_tem_overtime = float(sec_sign_out) - float(first_sign_out)
                                                if tem_sign_out >= float(line.request_hour_from) and tem_sign_out <= hour_to:
                                                    s_tem_overtime_value = s_tem_overtime * line.rate
                                                    flag1 = True
                                                    # print('sectemp', s_tem_overtime, s_tem_overtime_value)
                                        elif ac_sign_out >= float(line.request_hour_from) and ac_sign_out <= hour_to:
                                            act_float_overtime = float_overtime
                                            float_overtime1 = float_overtime - (f_tem_overtime + s_tem_overtime)
                                            float_overtime_line = float_overtime1 * line.rate
                                    float_overtime_line = float_overtime_line + f_tem_overtime_value + s_tem_overtime_value
                                    float_overtime_hour = s_tem_overtime + f_tem_overtime + float_overtime1
                                    if float_overtime_line > 0:
                                        float_overtime = float_overtime_line
                                        act_float_overtime = float_overtime
                                    else:
                                        act_float_overtime = float_overtime = 0
                                else:
                                    act_float_overtime = float_overtime = 0
                                # if float_overtime <= overtime_policy[
                                #     'wd_after']:
                                #     float_overtime = act_float_overtime = 0
                                # else:
                                #     act_float_overtime = float_overtime
                                #     float_overtime = act_float_overtime * \
                                #                      overtime_policy['wd_rate']
                                values = {
                                    'date': date,
                                    'day': day_str,
                                    'pl_sign_in': 0,
                                    'pl_sign_out': 0,
                                    'ac_sign_in': ac_sign_in,
                                    'ac_sign_out': ac_sign_out,
                                    'overtime': float_overtime,
                                    'worked_hours': float_worked_hours,
                                    'act_overtime': act_float_overtime,
                                    'note': _("overtime out of work intervals"),
                                    'att_sheet_id': self.id
                                }
                                att_line.create(values)
                else:
                    if attendance_intervals:
                        # print "thats weekend be over time "
                        for attendance_interval in attendance_intervals:
                            overtime = attendance_interval[1] - \
                                       attendance_interval[0]
                            ac_sign_in = pytz.utc.localize(
                                attendance_interval[0]).astimezone(tz)
                            ac_sign_out = pytz.utc.localize(
                                attendance_interval[1]).astimezone(tz)
                            float_overtime = overtime.total_seconds() / 3600
                            if float_overtime <= overtime_policy['we_after']:
                                float_overtime = 0
                                act_float_overtime = 0
                            else:
                                act_float_overtime = float_overtime
                                float_overtime = act_float_overtime * \
                                                 overtime_policy['we_rate']
                            ac_sign_in = pytz.utc.localize(
                                attendance_interval[0]).astimezone(tz)
                            ac_sign_out = pytz.utc.localize(
                                attendance_interval[1]).astimezone(tz)
                            worked_hours = attendance_interval[1] - \
                                           attendance_interval[0]
                            float_worked_hours = worked_hours.total_seconds() / 3600
                            values = {
                                'date': date,
                                'day': day_str,
                                'ac_sign_in': self._get_float_from_time(
                                    ac_sign_in),
                                'ac_sign_out': self._get_float_from_time(
                                    ac_sign_out),
                                'overtime': float_overtime,
                                'act_overtime': act_float_overtime,
                                'worked_hours': float_worked_hours,
                                'att_sheet_id': self.id,
                                'status': 'weekend',
                                'note': _("working in weekend")
                            }
                            att_line.create(values)
                    else:
                        values = {
                            'date': date,
                            'day': day_str,
                            'att_sheet_id': self.id,
                            'status': 'weekend',
                            'note': ""
                        }
                        att_line.create(values)



