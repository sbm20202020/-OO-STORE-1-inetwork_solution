# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

import time


class MissingItemWizard(models.TransientModel):
    _name = "missing.item.wizard"

    inventory_id = fields.Many2one('stock.inventory', string="Inventory Adjustment")
    line_ids = fields.Many2many('product.product', string='Inventories Products', compute='compute_inventory_line_ids')
    product_ids = fields.Many2many('product.product', string="Missing Items", required=True,
                                   domain="[('id', 'not in', line_ids),('type', '=', 'product'),('qty_available','>',0)]")
    location_ids = fields.Many2many('stock.location', string="Locations")

    @api.depends('inventory_id')
    def compute_inventory_line_ids(self):
        products = []
        inventory_obj = self.env['stock.inventory.line'].search([('inventory_id', '=', self.inventory_id.id)])
        for rec in inventory_obj:
            # if rec.inventory_id.product_ids:
            #     if rec.product_id.qty_available <= 0 and rec.product_id not in rec.inventory_id.product_ids.ids:
            #         products.append(rec.product_id.id)
            # else:
            if rec.product_id not in rec.inventory_id.product_ids.ids:
                products.append(rec.product_id.id)
            '''domain = [
                ('id', '!=', rec.id),
                ('product_id', '=', rec.product_id.id),
                ('location_id', '=', rec.location_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('package_id', '=', rec.package_id.id),
                ('prod_lot_id', '=', rec.prod_lot_id.id),('inventory_id', '=', rec.inventory_id.id)]
            existings = self.env['stock.inventory.line'].search_count(domain)
            if existings:'''
        print("Len Product", len(products))
        self.line_ids = [(6, 0, products)]

    def create_inventory_adjustment_for_missing(self):
        active_record = self.env.context.get('active_ids', [])
        record = self.env['stock.inventory'].browse(active_record)
        # record.action_validate()
        # inventory_adjustment = self.env['stock.inventory'].create({
        #     'name': str(self.inventory_id.name) + ":" + 'Inventory For Missing Items',
        # })
        # inventory_adjustment.action_start()
        for product in self.product_ids:
            if self.location_ids:
                self.inventory_id.write({
                    'line_ids': [
                        (0, 0, {'product_id': product.id, 'product_qty': 0,
                                'location_id': self.location_ids[0].id or self.env['stock.location'].search(
                                    [('usage', 'in', ['internal', 'transit'])], limit=1).id, 'is_editable': True,
                                }),
                    ]
                })
                # inventory_adjustment.write({
                #     'line_ids': [
                #         (0, 0, {'product_id': product.id, 'product_qty': 0,
                #                 'location_id': self.location_ids[0].id or self.env['stock.location'].search(
                #                     [('usage', 'in', ['internal', 'transit'])], limit=1).id, 'is_editable': True,
                #                 }),
                #     ]
                # })
            else:
                self.inventory_id.write({
                    'line_ids': [
                        (0, 0, {'product_id': product.id, 'product_qty': 0,
                                'location_id': self.env['stock.location'].search(
                                    [('usage', 'in', ['internal', 'transit'])], limit=1).id, 'is_editable': True,
                                }),
                    ]
                })
                # inventory_adjustment.write({
                #     'line_ids': [
                #         (0, 0, {'product_id': product.id, 'product_qty': 0,
                #                 'location_id': self.env['stock.location'].search(
                #                     [('usage', 'in', ['internal', 'transit'])], limit=1).id, 'is_editable': True,
                #                 }),
                #     ]
                # })
        self.inventory_id.check_missing = True
