# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AvailabilityAvailability(models.Model):
    _name = 'availability.availability'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=1)
