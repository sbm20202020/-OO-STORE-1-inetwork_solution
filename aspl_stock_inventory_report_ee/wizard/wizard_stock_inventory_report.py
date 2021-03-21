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
from odoo.exceptions import ValidationError
from io import BytesIO
import xlwt
import base64
from datetime import datetime, date
import random


class stock_inventory_wizard(models.TransientModel):
    _name = "stock.inventory.wizard"
    _description = "Stock Inventory Wizard"

    @api.model
    def send_inventory_report(self):
        ir_config_obj = self.env['ir.config_parameter']
        template_id = ir_config_obj.sudo().get_param(
            'aspl_stock_inventory_report_ee.stock_inventory_report_email_template_id')
        if template_id:
            email_template_id = self.env['mail.template'].search([('id', '=', int(template_id))])
            if ir_config_obj.sudo().get_param(
                    'aspl_stock_inventory_report_ee.stock_inventory_report') and email_template_id:
                config_ids = self.env['res.config.settings'].search([], order="id desc", limit=1)
                for each in config_ids.inventory_report_user_ids.filtered(lambda l: l.email):
                    warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', each.company_id.id)])
                    inventory_wizard_id = self.create({
                        'company_id': each.company_id.id,
                        'start_date': date.today(),
                        'end_date': date.today(),
                        'warehouse_ids': [(6, 0, warehouse_ids.ids)],
                        'is_today_movement': True
                    })
                    inventory_wizard_id.generate_pdf_report()
                    email_subject = 'Stock Inventory Report ' + str(date.today())
                    email_template_id.with_context(
                        {'user_email': each.email, 'email_subject': email_subject}).send_mail(inventory_wizard_id.id,
                                                                                              force_send=True)

    start_date = fields.Date(string="Start Date", default=date.today())
    end_date = fields.Date(string="End Date", default=date.today())
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id,
                                 required=True)
    warehouse_ids = fields.Many2many('stock.warehouse', 'warehouse_wizard_stock_rel', string="Warehouse", required=True)
    location_id = fields.Many2one('stock.location', string="Location")
    filter_by = fields.Selection([('product', 'Product'), ('category', 'Category')], string="Filter By")
    group_by_categ = fields.Boolean(string="Category Group By")
    with_zero = fields.Boolean(string="With Zero Values")
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    name = fields.Char(string='File Name', readonly=True)
    data = fields.Binary(string='File', readonly=True)
    product_ids = fields.Many2many('product.product', 'product_stock_inv_rel', string="Products")
    category_ids = fields.Many2many('product.category', 'product_categ_stock_inv_rel', string="Categories")
    is_today_movement = fields.Boolean(string="Today Movement")

    @api.onchange('warehouse_ids')
    def onchange_warehouse_ids(self):
        if self.warehouse_ids:
            self.location_id = False

    @api.onchange('filter_by')
    def onchange_filter_by(self):
        self.product_ids = self.category_ids = False

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            self.warehouse_ids = self.location_id = False

    def check_date_range(self):
        if self.end_date < self.start_date:
            raise ValidationError(_('Enter proper date range'))

    def generate_pdf_report(self):
        self.check_date_range()
        datas = {'form':
            {
                'company_id': self.company_id.id,
                'warehouse_ids': [y.id for y in self.warehouse_ids],
                'location_id': self.location_id and self.location_id.id or False,
                'start_date': date.today() if self.is_today_movement else self.start_date,
                'end_date': date.today() if self.is_today_movement else self.end_date,
                'id': self.id,
                'product_ids': self.product_ids.ids,
                'product_categ_ids': self.category_ids.ids
            },
        }
        return self.env.ref('aspl_stock_inventory_report_ee.action_report_stock_inv').report_action(self, data=datas)

    def generate_xls_report(self):
        self.check_date_range()
        report_stock_inv_obj = self.env['report.aspl_stock_inventory_report_ee.stock_inv_template']
        workbook = xlwt.Workbook(encoding="utf-8")
        header_style = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        font = xlwt.Font()
        fontP = xlwt.Font()
        font.bold = True
        font.height = 240
        font.colour_index = 2
        fontP.bold = True
        header_different = []

        # for all data tab
        header_style1 = xlwt.XFStyle()
        pattern1 = xlwt.Pattern()
        pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour = 22
        header_style1.font = fontP
        header_style1.alignment = alignment
        header_style1.pattern = pattern1
        header_different.append(header_style1)
        i=24
        for header in range(0,len(self.warehouse_ids)):
            header_style1 = xlwt.XFStyle()
            # Cell Color
            pattern1 = xlwt.Pattern()
            pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
            # pattern1.pattern_fore_colour = random.randint(0, 255)
            pattern1.pattern_fore_colour = i
            i+=1
            header_style1.font = fontP
            header_style1.alignment = alignment
            header_style1.pattern = pattern1
            header_different.append(header_style1)
        # Cell Color
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = 22

        header_style.font = fontP
        header_style.alignment = alignment
        header_style.pattern = pattern

        header_data = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        header_data.alignment = alignment

        total_value_style = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        total_value_style.alignment = alignment
        total_value_style.font = fontP
        base_col = 0
        global_data = {}
        avail_categ = []
        for warehouse in self.warehouse_ids:
            worksheet = workbook.add_sheet(warehouse.name)
            rows = 0
            worksheet.write_merge(rows, rows+1, 0, 8, "Stock Report", style=header_style)
            # Excel Sheet Header Data
            upper_header_lst = ['Company', 'Warehouse', 'Location', 'Start Date', 'End Date', 'Generated By',
                                'Generated Date']
            col = base_col
            for header in upper_header_lst:
                worksheet.write(5, col, header, style=header_style)
                col += 1
            upper_header_lst_data = [self.company_id.name, warehouse.name,
                                     self.location_id.name if self.location_id else "All",
                                     str(self.start_date), str(self.end_date), self.env.user.name,
                                     str(datetime.today().date())]
            col = base_col
            for header_value in upper_header_lst_data:
                worksheet.write(6, col, header_value, style=header_data)
                col += 1
            lower_header_lst = ['Beginning', 'Received', 'Sales', 'Internal', 'Adjustments', 'Ending']
            col = base_col + 3
            for header in lower_header_lst:
                worksheet.write(9, col, header, style=header_style)
                col += 1
            rows = 10
            worksheet.write_merge(rows-1, rows-1, 0, 2, "Products", style=header_style)
            prod_beginning_qty = prod_qty_in = prod_qty_out = prod_qty_int = prod_qty_adjust = prod_ending_qty = 0.00
            if not self.group_by_categ:
                product_ids = report_stock_inv_obj._get_products(self)
                for product in product_ids:
                    beginning_qty = report_stock_inv_obj._get_beginning_inventory(self, product, warehouses=warehouse)
                    product_val = report_stock_inv_obj.get_product_sale_qty(self, product, warehouses=warehouse)
                    today_movment_qty = product_val.get('product_qty_in') + product_val.get('product_qty_out') \
                                        + product_val.get('product_qty_internal') + product_val.get(
                        'product_qty_adjustment')

                    ending_qty = beginning_qty + product_val.get('product_qty_in') + product_val.get('product_qty_out') \
                                 + product_val.get('product_qty_internal') + product_val.get('product_qty_adjustment')
                    if not self.with_zero and beginning_qty == 0.0 and product_val.get(
                            'product_qty_in') == 0.0 and product_val.get('product_qty_out') == 0.0 and \
                            product_val.get('product_qty_internal') == 0.0 and product_val.get(
                        'product_qty_adjustment') == 0:
                        continue
                    elif today_movment_qty == 0.00 and self.is_today_movement:
                        continue
                    if global_data.get(str(product.id)):
                        global_data[str(product.id)].update({warehouse: [beginning_qty,
                                                                                  product_val.get('product_qty_in'),
                                                                                  abs(product_val.get(
                                                                                      'product_qty_out')),
                                                                                  product_val.get(
                                                                                      'product_qty_internal'),
                                                                                  product_val.get(
                                                                                      'product_qty_adjustment'),
                                                                                  ending_qty]})
                    else:
                        global_data[str(product.id)] = {warehouse: [beginning_qty,
                                                                             product_val.get('product_qty_in'),
                                                                             abs(product_val.get('product_qty_out')),
                                                                             product_val.get('product_qty_internal'),
                                                                             product_val.get('product_qty_adjustment'),
                                                                             ending_qty]}
                    worksheet.write_merge(rows, rows, 0, 2, product.name_get()[0][1])
                    worksheet.write(rows, base_col + 3, beginning_qty)
                    worksheet.write(rows, base_col + 4, product_val.get('product_qty_in'))
                    worksheet.write(rows, base_col + 5, abs(product_val.get('product_qty_out')))
                    worksheet.write(rows, base_col + 6, product_val.get('product_qty_internal'))
                    worksheet.write(rows, base_col + 7, product_val.get('product_qty_adjustment'))
                    worksheet.write(rows, base_col + 8, ending_qty)
                    prod_qty_in += product_val.get('product_qty_in')
                    prod_qty_out += product_val.get('product_qty_out')
                    prod_qty_int += product_val.get('product_qty_internal')
                    prod_qty_adjust += product_val.get('product_qty_adjustment')
                    prod_ending_qty += ending_qty
                    prod_beginning_qty += beginning_qty
                    rows += 1
                if global_data.get('Total'):
                    global_data['Total'].update({warehouse: [prod_beginning_qty,
                                                             prod_qty_in,
                                                             abs(prod_qty_out),
                                                             prod_qty_int,
                                                             prod_qty_adjust,
                                                             prod_ending_qty]})
                else:
                    global_data['Total'] = {warehouse: [prod_beginning_qty,
                                                        prod_qty_in,
                                                        abs(prod_qty_out),
                                                        prod_qty_int,
                                                        prod_qty_adjust,
                                                        prod_ending_qty]}
                worksheet.write_merge(rows + 1, rows + 1, 0, 2, 'Total', style=header_style)
                worksheet.write(rows + 1, base_col + 3, prod_beginning_qty, style=header_style)
                worksheet.write(rows + 1, base_col + 4, prod_qty_in, style=header_style)
                worksheet.write(rows + 1, base_col + 5, abs(prod_qty_out), style=header_style)
                worksheet.write(rows + 1, base_col + 6, prod_qty_int, style=header_style)
                worksheet.write(rows + 1, base_col + 7, prod_qty_adjust, style=header_style)
                worksheet.write(rows + 1, base_col + 8, prod_ending_qty, style=header_style)
            else:
                rows += 1
                product_val = report_stock_inv_obj.get_product_sale_qty(self, warehouses=warehouse)
                if product_val:
                    for categ, product_value in product_val.items():
                        categ_prod_beginning_qty = categ_prod_qty_in = categ_prod_qty_out = categ_prod_qty_int = categ_prod_qty_adjust = categ_prod_ending_qty = 0.00
                        worksheet.write_merge(rows, rows, base_col + 0, base_col + 8,
                                              self.env['product.category'].browse(categ).name, style=header_style)
                        if not avail_categ.count(self.env['product.category'].browse(categ)):
                            avail_categ.append(self.env['product.category'].browse(categ))
                        rows += 1
                        for product in product_value:
                            product_id = self.env['product.product'].browse(product['product_id'])
                            beginning_qty = report_stock_inv_obj._get_beginning_inventory(self, product_id.id,
                                                                                          warehouses=warehouse)
                            ending_qty = beginning_qty + product.get('product_qty_in') + product.get('product_qty_out')\
                                    + product.get('product_qty_internal') + product.get('product_qty_adjustment')
                            if not self.with_zero and beginning_qty == 0.0 and product.get(
                                    'product_qty_in') == 0.0 and product.get('product_qty_out') == 0.0 and \
                                    product.get('product_qty_internal') == 0.0 and product.get(
                                'product_qty_adjustment') == 0:
                                continue
                            if global_data.get(str(product_id.id)):
                                global_data[str(product_id.id)].update({warehouse: [beginning_qty,
                                                                                             product.get(
                                                                                                 'product_qty_in'),
                                                                                             abs(product.get(
                                                                                                 'product_qty_out')),
                                                                                             product.get(
                                                                                                 'product_qty_internal'),
                                                                                             product.get(
                                                                                                 'product_qty_adjustment'),
                                                                                             ending_qty]})
                            else:
                                global_data[str(product_id.id)] = {warehouse: [beginning_qty,
                                                                                        product.get('product_qty_in'),
                                                                                        abs(product.get(
                                                                                            'product_qty_out')),
                                                                                        product.get(
                                                                                            'product_qty_internal'),
                                                                                        product.get(
                                                                                            'product_qty_adjustment'),
                                                                                        ending_qty]}
                            worksheet.write_merge(rows, rows, 0, 2, product_id.name_get()[0][1])
                            worksheet.write(rows, base_col + 3, beginning_qty)
                            worksheet.write(rows, base_col + 4, product.get('product_qty_in'))
                            worksheet.write(rows, base_col + 5, abs(product.get('product_qty_out')))
                            worksheet.write(rows, base_col + 6, product.get('product_qty_internal'))
                            worksheet.write(rows, base_col + 7, product.get('product_qty_adjustment'))
                            worksheet.write(rows, base_col + 8, ending_qty)
                            categ_prod_qty_in += product.get('product_qty_in')
                            categ_prod_qty_out += product.get('product_qty_out')
                            categ_prod_qty_int += product.get('product_qty_internal')
                            categ_prod_qty_adjust += product.get('product_qty_adjustment')
                            categ_prod_ending_qty += ending_qty
                            categ_prod_beginning_qty += beginning_qty
                            rows += 1
                        worksheet.write_merge(rows, rows, 0, 2, 'Total', style=total_value_style)
                        worksheet.write(rows, base_col + 3, categ_prod_beginning_qty, style=total_value_style)
                        worksheet.write(rows, base_col + 4, categ_prod_qty_in, style=total_value_style)
                        worksheet.write(rows, base_col + 5, abs(categ_prod_qty_out), style=total_value_style)
                        worksheet.write(rows, base_col + 6, categ_prod_qty_int, style=total_value_style)
                        worksheet.write(rows, base_col + 7, categ_prod_qty_adjust, style=total_value_style)
                        worksheet.write(rows, base_col + 8, categ_prod_ending_qty, style=total_value_style)
                        prod_qty_in += categ_prod_qty_in
                        prod_qty_out += categ_prod_qty_out
                        prod_qty_int += categ_prod_qty_int
                        prod_qty_adjust += categ_prod_qty_adjust
                        prod_ending_qty += categ_prod_ending_qty
                        prod_beginning_qty += categ_prod_beginning_qty
                        if global_data.get('Total'):
                            global_data['Total'].update({warehouse: [prod_beginning_qty,
                                                                     prod_qty_in,
                                                                     abs(prod_qty_out),
                                                                     prod_qty_int,
                                                                     prod_qty_adjust,
                                                                     prod_ending_qty]})
                        else:
                            global_data['Total'] = {warehouse: [prod_beginning_qty,
                                                                prod_qty_in,
                                                                abs(prod_qty_out),
                                                                prod_qty_int,
                                                                prod_qty_adjust,
                                                                prod_ending_qty]}
                        rows += 1
                worksheet.write_merge(rows + 1, rows + 1, 0, 2, "Grand Total", style=header_style)
                worksheet.write(rows + 1, base_col + 3, prod_beginning_qty, style=header_style)
                worksheet.write(rows + 1, base_col + 4, prod_qty_in, style=header_style)
                worksheet.write(rows + 1, base_col + 5, abs(prod_qty_out), style=header_style)
                worksheet.write(rows + 1, base_col + 6, prod_qty_int, style=header_style)
                worksheet.write(rows + 1, base_col + 7, prod_qty_adjust, style=header_style)
                worksheet.write(rows + 1, base_col + 8, prod_ending_qty, style=header_style)
            for cols_width in range(0, 9):
                worksheet.col(cols_width).width = 4500

        file_data = BytesIO()
        workbook.save(file_data)
        self.write({
            'state': 'get',
            'data': base64.encodestring(file_data.getvalue()),
            'name': 'stock_inventory.xls'
        })
        return {
            'name': 'Stock Inventory Report',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }


class stock_location(models.Model):
    _inherit = 'stock.location'

    @api.model
    def name_search(self, name, args, operator='ilike', limit=100):
        if self._context.get('company_id'):
            domain = [('company_id', '=', self._context.get('company_id')), ('usage', '=', 'internal')]
            if self._context.get('warehouse_ids') and self._context.get('warehouse_ids')[0][2]:
                warehouse_ids = self._context.get('warehouse_ids')[0][2]
                stock_ids = []
                for warehouse in self.env['stock.warehouse'].browse(warehouse_ids):
                    stock_ids.append(warehouse.view_location_id.id)
                domain.append(('location_id', 'child_of', stock_ids))
            args += domain
        return super(stock_location, self).name_search(name, args, operator, limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
