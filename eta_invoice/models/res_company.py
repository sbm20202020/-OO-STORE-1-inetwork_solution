# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _ ,tools, SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from datetime import datetime , date ,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from odoo.fields import Datetime as fieldsDatetime
import calendar
from odoo import http
from odoo.http import request
from odoo import tools

import logging

LOGGER = logging.getLogger(__name__)

# selections = [('1','1'),('2','2')]


class ResCompany(models.Model):
    _inherit = 'res.company'

    # taxpayer_activity_code = fields.Selection(selection=selections, required=True, )
    branch_id = fields.Char(required=True, )
    building_number = fields.Char(required=True)
    region_city = fields.Char(required=True)
    floor = fields.Char(string="", default="", required=False, )
    room = fields.Char(string="", default="", required=False, )
    landmark = fields.Char(string="", default="", required=False, )
    additional_information = fields.Char(string="", default="", required=False, )

