# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    lot_id = fields.Many2one('stock.production.lot', string="Logistics Serial Number",track_visibility='onchange',help="The unique serial number that associated with the Equipmen")
    product_id =fields.Many2one('product.product',related="lot_id.product_id",readonly=True,index=True ,string="Associated Product")
    product_tmpl_id = fields.Many2one('product.template', related="product_id.product_tmpl_id", readonly=True, index=True,
                                 string="Associated Product Template")
    created_from_stock_lot= fields.Boolean(string="Created from Stock Lot", readonly=True)
    current_stock_location_id= fields.Many2one('stock.location',readonly=True, string="Current Stock Location",track_visibility='onchange')
    history_count = fields.Integer(string="Moves History Count", compute='_compute_equipment_move_count',readonly=True)
    stock_move_lines = fields.One2many('stock.move.line','equipment_id',"Moves History")

    @api.depends("stock_move_lines")
    def _compute_equipment_move_count(self):
        """
        calculate count of moves for the each equipment
        :return:
        """
        for equip in self:
            equip.history_count = len(equip.stock_move_lines)


    def action_view_equipment_moves(self):
        '''
        This function returns an action that display stock moves
        of the current equipment.
        '''
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        moves_lines = self.mapped('stock_move_lines')
        if self.stock_move_lines:
            action['domain'] = [('id', 'in', moves_lines.ids),('lot_id','=',self.lot_id.id)]
        return action