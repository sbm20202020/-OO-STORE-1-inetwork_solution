# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    equipment_id = fields.Many2one('maintenance.equipment', readonly=True,
                                   string="Equipment", help="The Equipment linked to this lot for equipment movement tracking.")