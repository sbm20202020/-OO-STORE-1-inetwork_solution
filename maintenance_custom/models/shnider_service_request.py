# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, SUPERUSER_ID


class ShniderServiceRequest(models.Model):
    _inherit = 'maintenance.request'

    shnider_stage_id = fields.Selection([
        ('new_request', 'New Request'),
        ('inspection', 'Inspection'),
        ('fixable', 'Fixable'),
        ('not_fixable', 'Not Fixable'),
        ('tested', 'Tested'),
        ('created_DO', 'Created DO'),
        ('replaced', 'Replaced'),
        ('closed_without_fees', 'Closed Without Fees'),
        ('create_DO_to_CL', 'Create DO to CL'),
        ('closed', 'Closed'),
        ('create_DO_to_MT', 'Create DO to MT'),
        ('create_DO_to_Shnider', 'Create DO to Schneider'),
        # ('created_CI', 'Created CI'),
    ], 'Stage', default='new_request')
    product_ids = fields.Many2many('product.product', string="Products")
    product_id = fields.Many2one('product.product', string="Product")
    product_price=fields.Float(related='product_id.lst_price')
    # replaced_product_ids = fields.Many2many('product.product', string="Replaced Products")
    invoice_id = fields.Many2one('account.move', 'Customer Invoice')
    delivery_order_id_to_MT = fields.Many2one('stock.picking', string='Delivery Order to MT', copy=False, store=True)
    delivery_order_id_to_shnider = fields.Many2one('stock.picking', string='Delivery Order to Schneider', copy=False, store=True)
    replaced = fields.Boolean('replaced')
    fixable = fields.Boolean('replaced')
    type = fields.Selection([('standard', 'Standard'), ('shnider', 'Schneider')], 'Type', store=True)


    def action_not_replace(self):
        if self.type == 'shnider':
            self.shnider_stage_id = 'closed_without_fees'
            self.stage_name = 'closed_without_fees'

    def action_replace(self):
        if self.type == 'shnider':
            self.shnider_stage_id = 'replaced'
            self.stage_name = 'replaced'
            self.replaced = True

    def action_test(self):
        if self.type == 'shnider':
            self.shnider_stage_id = 'tested'
            self.stage_name = 'tested'

    def action_create_invoice(self):
        self.ensure_one()
        picking_id = self.picking_id
        invoice = self.env["account.move"].create(
            {
                "name": self.name,
                "partner_id": picking_id.partner_id.id,
                "ref": self.name,
                "state": "draft",
                "type": "in_invoice",
            }
        )
        for line in self.product_ids:
            line = self.env["account.move.line"].create({
                'product_id': line.id,
                'name': line.partner_ref,
                "move_id": invoice.id,
                "account_id":line.property_account_expense_id.id,
                "price_unit": line.lst_price,
            })
        self.invoice_id = invoice.id
        if self.type == 'standard':
            stage_obj = self.env['maintenance.stage'].search([('name', '=', 'Created CI')])
            self.stage_id = stage_obj.id
            self.stage_name = 'Created CI'
        return invoice
    def action_create_delivery_order_to_cl(self):
        self.ensure_one()
        # Create new Delivery Order for products
        location = self.env['stock.location'].search(
            [('shnider_location', '=', True)],
            limit=1,
        )
        picking_internal = self.env['stock.picking.type'].search(
            [('code', '=', 'internal')],
            limit=1,
        )
        picking_id = self.picking_id
        picking_type_id = self.env.ref('stock.picking_type_out')
        new_delivery_order = self.env["stock.picking"].create({
            'move_lines': [],
            'picking_type_id': picking_internal.id,
            'state': 'draft',
            'origin': self.name,
            'maintenance_request_id': self.id,
            'partner_id': picking_id.partner_id.id,
            'picking_type_code': 'internal',
            'location_id': picking_id.location_dest_id.id,
            'location_dest_id': location.id,
        })

        for line in picking_id.move_ids_without_package:
            x = self.env["stock.move"].create({
                'product_id': line.product_id.id,
                'product_uom_qty': float(line.product_uom_qty),
                 'name': line.product_id.partner_ref,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': new_delivery_order.id,
                'state': 'draft',
                'origin': line.origin,
                'location_id': line.location_dest_id.id,
                'location_dest_id': location.id,
                'picking_type_id': picking_internal.id,
                'warehouse_id': picking_type_id.warehouse_id.id,
                'procure_method': 'make_to_order',
            })
        self.action_create_delivery_order_to_cl2()
        if self.type == 'shnider':
            self.shnider_stage_id = 'create_DO_to_CL'
            self.stage_name = 'create_DO_to_CL'

    def action_create_delivery_order_to_cl2(self):
        self.ensure_one()

        location = self.env['stock.location'].search(
            [('main_location', '=', True)],
            limit=1,
        )
        # Create new Delivery Order for products
        picking_id = self.picking_id
        picking_type_id = self.env.ref('stock.picking_type_out')
        new_delivery_order = self.env["stock.picking"].create({
            'move_lines': [],
            'picking_type_id': picking_type_id.id,
            'state': 'draft',
            'origin': self.name,
            'maintenance_request_id': self.id,
            'partner_id': picking_id.partner_id.id,
            'picking_type_code': 'outgoing',
            'location_id': location.id,
            'location_dest_id': picking_id.location_id.id,
        })

        for line in picking_id.move_ids_without_package:
            x = self.env["stock.move"].create({
                'product_id': self.product_id.id,
                'product_uom_qty': float(line.product_uom_qty),
                'name': self.product_id.partner_ref,
                'product_uom': self.product_id.uom_id.id,
                'picking_id': new_delivery_order.id,
                'state': 'draft',
                'origin': line.origin,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'picking_type_id': picking_type_id.id,
                'warehouse_id': picking_type_id.warehouse_id.id,
                'procure_method': 'make_to_order',
            })






    def action_create_delivery_order_to_mt(self):
        self.ensure_one()
        # Create new Delivery Order for products
        picking_id = self.picking_id
        picking_type_id = self.env.ref('stock.picking_type_out')
        new_delivery_order = self.env["stock.picking"].create({
            'move_lines': [],
            'picking_type_id': picking_type_id.id,
            'state': 'draft',
            'origin': self.name,
            'partner_id': picking_id.partner_id.id,
            'maintenance_request_id': self.id,
            'picking_type_code': 'outgoing',
            'location_id': picking_id.location_id.id,
            'location_dest_id': picking_id.location_dest_id.id,
            # 'group_id': self.rma_id.order_id.procurement_group_id.id,
        })
        for line in picking_id.move_ids_without_package:
            x = self.env["stock.move"].create({
                'product_id': line.product_id.id,
                'product_uom_qty': float(line.product_uom_qty),
                'name': line.product_id.partner_ref,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': new_delivery_order.id,
                'state': 'draft',
                'origin': line.origin,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'picking_type_id': picking_type_id.id,
                'warehouse_id': picking_type_id.warehouse_id.id,
                'procure_method': 'make_to_order',
            })
        self.delivery_order_id_to_MT = new_delivery_order.id
        if self.type == 'shnider':
            self.shnider_stage_id = 'create_DO_to_MT'
            self.stage_name = 'create_DO_to_MT'

        return new_delivery_order, picking_type_id

    def action_create_delivery_order_to_shnider(self):
        self.ensure_one()
        # Create new Delivery Order for products
        picking_id = self.picking_id
        picking_type_id = self.env.ref('stock.picking_type_out')
        new_delivery_order = self.env["stock.picking"].create({
            'move_lines': [],
            'picking_type_id': picking_type_id.id,
            'state': 'draft',
            'origin': self.name,
            'partner_id': picking_id.partner_id.id,
            'maintenance_request_id':self.id,
            'picking_type_code': 'outgoing',
            'location_id': picking_id.location_id.id,
            'location_dest_id': picking_id.location_dest_id.id,
            # 'group_id': self.rma_id.order_id.procurement_group_id.id,
        })
        for line in picking_id.move_ids_without_package:
            x = self.env["stock.move"].create({
                'product_id': line.product_id.id,
                'product_uom_qty': float(line.product_uom_qty),
                'name': line.product_id.partner_ref,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': new_delivery_order.id,
                'state': 'draft',
                'origin': line.origin,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'picking_type_id': picking_type_id.id,
                'warehouse_id': picking_type_id.warehouse_id.id,
                'procure_method': 'make_to_order',
            })
        self.delivery_order_id_to_shnider = new_delivery_order.id
        if self.type == 'shnider':
            self.shnider_stage_id = 'create_DO_to_Shnider'
            self.stage_name = 'create_DO_to_Shnider'
        return new_delivery_order, picking_type_id


class StockLocation(models.Model):
    _inherit = 'stock.location'

    main_location=fields.Boolean('Main Location')
    maintaince_location=fields.Boolean('Maintained Location')
    shnider_location=fields.Boolean('Schneider Location')


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    maintenance_request_id=fields.Many2one('maintenance.request',string='Maintainece')
