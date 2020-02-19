# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
from openerp import SUPERUSER_ID



class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification',
                     subtype=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        res = super(SaleOrder, self).message_post(body=body, subject=subject, message_type=message_type,
                                                  subtype=subtype, parent_id=parent_id, attachments=attachments,
                                                  content_subtype=content_subtype, **kwargs)

        if self._context.get('uid'):
            if self._context['uid'] != self.env.user.id:
                partner_id = self.env['res.users'].browse(self._context['uid']).partner_id.id
                res.write({'author_id': partner_id})
        return res






    @api.model
    def create(self, vals):
        if 'order_line' not in vals:
            raise UserError("Please add lines in Quotation")
        res = super(SaleOrder, self.sudo()).create(vals)
        return res


    def write(self, vals):
        res = super(SaleOrder, self.sudo()).write(vals)
        return res

    total_state = fields.Char('Total State', compute='calc_state', store=True)

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('confirmed_line', 'Confirmed'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.constrains('total_state')
    def change_state(self):
        for line in self:
            if line.total_state == 'Confirm Complate':
                line.state = 'confirmed_line'
                # commission_group = self.env.ref('sales_team.group_sale_manager')
                # commission_group.write({'users': [(4,self.env.user.id)]})
            elif line.total_state == 'Waiting Confirm' or line.total_state == ' ':
                line.state = 'draft'



    @api.depends('order_line.state_confirm')
    def calc_state(self):
        list = []
        for line in self:
            if line.order_line:
                for rec in line.order_line:
                    list.append(rec.state_confirm)

            print (list)

            if list.count(False) > 0:
                line.total_state = 'Waiting Confirm'

            elif list.count(False) == 0 and list.count('confirm') == 0:

                line.total_state = ' '
            else:

                line.total_state = 'Confirm Complate'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self.sudo()).create(vals)
        return res


    def write(self, vals):
        res = super(SaleOrderLine, self.sudo()).write(vals)
        return res

    state_confirm = fields.Selection([
        ('confirm', 'Confirm')], store=True,copy=False)

#     @api.onchange('state_confirm')
#     def _check_manager(self):
#         for line in self:
#             if line.product_id:
#                 if self.env.user.has_group('base.group_system') or self.env.user.has_group('sales_team.group_sale_manager'):
#                     pass
#                 elif  self.env.user.has_group('sales_team.group_sale_salesman') and self.env.user.is_confirm_sale_order_line == True :
#                     pass
#                 elif  self.env.user.has_group('sales_team.group_sale_salesman_all_leads') and self.env.user.is_confirm_sale_order_line == True :
#                     pass
#                 else:
#                     raise ValidationError("Sales Administrator Should Confirm")












