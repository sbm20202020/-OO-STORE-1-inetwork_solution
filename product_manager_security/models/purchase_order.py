# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
from openerp import SUPERUSER_ID



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification',
                     subtype=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        res = super(PurchaseOrder, self).message_post(body=body, subject=subject, message_type=message_type,
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
        res = super(PurchaseOrder, self.sudo()).create(vals)
        return res


    def write(self, vals):
        res = super(PurchaseOrder, self.sudo()).write(vals)
        return res

    total_state = fields.Char('Total State', compute='calc_state', store=True)
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('confirmed_line', 'Confirmed'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    @api.constrains('total_state')
    def change_state(self):
        for line in self:
            if line.total_state == 'Confirm Complate':
                line.state = 'confirmed_line'
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

    def button_confirm(self):
        res=super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.state in ['confirmed_line']:
                order.write({'state': 'to approve'})
        return res



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self.sudo()).create(vals)
        return res


    def write(self, vals):
        res = super(PurchaseOrderLine, self.sudo()).write(vals)
        return res

    state_confirm = fields.Selection([
        ('confirm', 'Confirm')], store=True,copy=False)

#     @api.onchange('state_confirm')
#     def _check_manager(self):
#         for line in self:
#             if line.product_id:
#                 if self.env.user.has_group('base.group_system') or self.env.user.has_group('purchase.group_purchase_manager'):
#                     pass
#                 elif  self.env.user.has_group('purchase.group_purchase_user') and self.env.user.is_confirm_purchase_order_line == True :
#                     pass

#                 else:
#                     raise ValidationError("Purchases Administrator Should Confirm")












