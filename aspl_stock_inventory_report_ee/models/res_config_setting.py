# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api, _
import ast


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_inventory_report = fields.Boolean(string="Stock Inventory Report")
    inventory_report_user_ids = fields.Many2many('res.users', string="Users")
    stock_inventory_report_email_template_id = fields.Many2one("mail.template", string="Email Template")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter']
        email_template_id = self.env.ref('aspl_stock_inventory_report_ee.stock_inventory_mail_template').id
        inventory_report_user_ids = param_obj.sudo().get_param('inventory_report_user_ids')
        if inventory_report_user_ids:
             res.update({'inventory_report_user_ids':ast.literal_eval(inventory_report_user_ids)})
        res.update({
                'stock_inventory_report': bool(param_obj.sudo().get_param('aspl_stock_inventory_report_ee.stock_inventory_report')),
                'stock_inventory_report_email_template_id': email_template_id,
                })
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param_obj = self.env['ir.config_parameter']
        param_obj.sudo().set_param('aspl_stock_inventory_report_ee.stock_inventory_report', self.stock_inventory_report)
        param_obj.sudo().set_param('aspl_stock_inventory_report_ee.stock_inventory_report_email_template_id', self.stock_inventory_report_email_template_id.id)
        param_obj.sudo().set_param('inventory_report_user_ids', self.inventory_report_user_ids.ids)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
