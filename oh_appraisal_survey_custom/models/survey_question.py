# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from collections import Counter, OrderedDict
from itertools import product
from werkzeug import urls
import random
class SurveyLabel(models.Model):
    _inherit = 'survey.label'
    value2= fields.Char('Second value', translate=True)
    value3 = fields.Char('third value', translate=True)
    question_header_label=fields.Many2one('survey.question')



class SurveyQuestion(models.Model):
    _inherit = 'survey.question'
    color=fields.Char()
    color_yellow=fields.Boolean()
    color_green=fields.Boolean()
    as_table=fields.Boolean()
    multi_row=fields.Boolean()
    need_header=fields.Boolean()
    header_labels=fields.One2many('survey.label','question_header_label')


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    # quizz_passed = fields.Boolean('Quizz Passed', compute='_compute_quizz_passed', store=True, compute_sudo=True)
    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id')
    def _compute_quizz_score(self):
        for user_input in self:
            if user_input.survey_id.id == self.env.ref('oh_appraisal_survey_custom.survey_inetwork').id:
                total_possible_score = 92

                if total_possible_score == 0:
                    user_input.quizz_score = 0
                else:
                    score = (sum(user_input.user_input_line_ids.mapped('answer_score')) / total_possible_score) * 100
                    user_input.quizz_score = round(score, 2) if score > 0 else 0
                    print('total', total_possible_score,score)

            else:
                return super(SurveyUserInput, self)._compute_quizz_score()

