# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _prepare_equipment_vals(self,product,lot_id,location_dest_id):
        """
        Prepare values to create Equipment
        :param product:
        :param lot_id:
        :param location_dest_id:
        :return: vals for create equipment
        """
        return {
            'name':product.name,
            'equipment_assign_to':product.equipment_assign_to,
            'maintenance_team_id':product.maintenance_team_id.id,
            'technician_user_id':product.technician_user_id.id,
            'model': product.model,
            'lot_id':lot_id and lot_id.id,
            'category_id':product.default_equipment_category_id.id,
            'created_from_stock_lot':True,
            'current_stock_location_id':location_dest_id.id,
            'serial_no': lot_id and lot_id.name
        }


    def button_validate(self):
        """
        override button validate to create equipment if the picking type is incoming and update current location of
        equipment if the picking type is internal
        :return:
        """
        res=super(StockPicking, self).button_validate()
        for ml in self.move_line_ids:
            if ml.product_id.is_equipment  and ml.product_id.tracking == 'serial':
                picking_type_id = ml.move_id.picking_type_id
                if picking_type_id:
                    # Check if the picking is incoming (Shipment) and use create lots is enabled
                    if picking_type_id.code == 'incoming' and picking_type_id.use_create_lots and  ml.is_equipment:
                        # Check if move lot is set
                        if ml.lot_id:
                            if ml.product_id:
                                equipment_vals=self._prepare_equipment_vals(ml.product_id,ml.lot_id,ml.location_dest_id)
                                equipment_id = self.env['maintenance.equipment'].create(equipment_vals)
                                ml.lot_id.equipment_id = equipment_id
                    if picking_type_id.code == 'internal':
                        equipment_id = ml.lot_id.equipment_id
                        if equipment_id:
                            equipment_id.update({'current_stock_location_id':ml.location_dest_id.id})
        return res