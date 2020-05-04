from odoo import fields, models, _, api, exceptions
import datetime
from datetime import timedelta
import logging


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    description = fields.Char(string="Description")
