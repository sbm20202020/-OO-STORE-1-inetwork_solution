# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeeAsset(models.Model):
    _name = 'hr.asset'
    _rec_name = 'name'
    name = fields.Char(string='Asset', required=True)

class HrEmployee(models.Model):

    _inherit = 'hr.employee'
    asset_ids = fields.Many2many('hr.asset', string="Asset")
