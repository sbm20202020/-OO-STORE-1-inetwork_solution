# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import ast


class AccountAccount(models.Model):
    _inherit = 'account.account'
    is_cash_flow= fields.Boolean()
