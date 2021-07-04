# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools

from odoo.addons.hr_appraisal.models.hr_appraisal import HrAppraisal

COLORS_BY_STATE = {
    'new': 0,
    'cancel': 1,
    'pending': 2,
    'done': 3,
}


class HrAppraisalReport(models.Model):
    _inherit = "hr.appraisal.report"

    state = fields.Selection([
        ('new', 'To Start'),
        ('pending', 'Appraisal Sent'),
        ('done', 'Done'),
        ('cancel', "Cancelled"),
    ], 'Status', readonly=True, default='new')

    def _compute_color(self):
        for record in self:
            record.color = COLORS_BY_STATE[record.state]
