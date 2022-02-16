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


class Partner(models.Model):
    _inherit = 'res.partner'

    branch_id = fields.Char(required=True, )
    building_number = fields.Char(required=True)
    # company_type = fields.Selection(selection_add=[('foreigner', 'Foreigner')])
    region_city = fields.Char( )
    national_id = fields.Char( )
    floor = fields.Char(string="", default="", required=False, )
    room = fields.Char(string="", default="", required=False, )
    landmark = fields.Char(string="", default="", required=False, )
    additional_information = fields.Char(string="", default="", required=False, )
    is_foreigner = fields.Boolean(string="Is Foreigner", default=False  )

    def get_company_type(self):
        if not self.is_foreigner:
            alias = {
                'company': 'B',
                'person': 'P',
                # 'foreigner': 'F',
            }
            return alias[self.company_type]
        else:
            return 'F'

