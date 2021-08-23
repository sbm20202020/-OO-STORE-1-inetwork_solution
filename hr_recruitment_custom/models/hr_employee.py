# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    graduated_certificate = fields.Binary(string='Graduated Certificate')
    graduated_certificate_name = fields.Char(string='Graduated Certificate Name')
    certificate_of_birth = fields.Binary(string='Certificate Of Birth')
    certificate_of_birth_name = fields.Char(string='Certificate Of Birth Name')
    fesh= fields.Binary(string='Fesh')
    fesh_name = fields.Char(string='Fesh Name')
    personal_photo= fields.Binary(string=' Personal Photo')
    military_certificate= fields.Binary(string='Military Certificate')
    military_certificate_name = fields.Char(string='Military Certificate Name')
    passport= fields.Binary(string='Passport')
    passport_name = fields.Char(string='Passport Name')
    medical_card= fields.Binary(string='Medical Card')
    medical_card_name = fields.Char(string='Medical Card Name')
    Form1_Social_insurance= fields.Binary(string='Form 1 Social insurance')
    Form1_Social_insurance_name = fields.Char(string='Form 1 Social insurance Name')
    Form6= fields.Binary(string='Form 6')
    Form6_name= fields.Char(string='Form 6 Name')
    employee_contract= fields.Binary(string='Employee Contract')
    employee_contract_name= fields.Char(string='Employee Contract Name')
    driver_license= fields.Binary(string='Driver License')
    driver_license_name= fields.Char(string='Driver License Name')
    card_id= fields.Binary(string='ID')
    card_id_name= fields.Char(string='ID Name')

    def _get_default_value(self):
        # default value to field country_of_birth , country_id
        search_id = self.env['res.country'].search([('is_default', '=', True)]).id
        if search_id:
            return search_id

    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', groups="hr.group_hr_user", tracking=True, default=_get_default_value)




class ResCountry(models.Model):
    _inherit='res.country'
    is_default= fields.Boolean()

