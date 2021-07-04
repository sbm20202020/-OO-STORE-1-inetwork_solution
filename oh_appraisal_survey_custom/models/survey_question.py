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


