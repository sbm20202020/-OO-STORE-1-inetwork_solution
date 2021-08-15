# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2020-TODAY .
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import models, fields, api, tools, _
import babel
import time
from datetime import datetime, timedelta

class HrAttendancePolicy(models.Model):
    _inherit = 'hr.attendance.policy'
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
            out_ot_id = self.overtime_rule_ids.search(
                [('type', '=', 'outside'), ('id', 'in', overtime_ids.ids)],
                order='id', limit=1)
            if wd_ot_id:
                res['wd_rate'] = wd_ot_id.rate
                res['wd_after'] = wd_ot_id.active_after
            else:
                res['wd_rate'] = 1
                res['wd_after'] = 0
            if we_ot_id:
                res['we_rate'] = we_ot_id.rate
                res['we_after'] = we_ot_id.active_after
            else:
                res['we_rate'] = 1
                res['we_after'] = 0

            if ph_ot_id:
                res['ph_rate'] = ph_ot_id.rate
                res['ph_after'] = ph_ot_id.active_after
            else:
                res['ph_rate'] = 1
                res['ph_after'] = 0
            if out_ot_id:
                res['out_rate'] = out_ot_id.rate
                res['out_after'] = out_ot_id.active_after
            else:
                res['out_rate'] = 1
                res['out_after'] = 0
        else:
            res['wd_rate'] = res['wd_rate'] = res['ph_rate'] = res['out_rate'] = 1
            res['wd_after'] = res['we_after'] = res['ph_after'] = res['out_after']= 0
        return res
class HrPolicy_overtimeLine(models.Model):
    _inherit = 'hr.policy.overtime.line'
    type = [
        ('weekend', 'Week End'),
        ('workday', 'Working Day'),
        ('ph', 'Public Holiday'),
        ('outside', 'Ph outside')

    ]
    type = fields.Selection(selection=type, string="Type", default='workday')
class HrOvertimeRule(models.Model):
    _inherit = 'hr.overtime.rule'
    type = [
        ('weekend', 'Week End'),
        ('workday', 'Working Day'),
        ('ph', 'Public Holiday'),
        ('outside', 'Ph outside')
        ]
    type = fields.Selection(selection=type, string="Type", default='workday')