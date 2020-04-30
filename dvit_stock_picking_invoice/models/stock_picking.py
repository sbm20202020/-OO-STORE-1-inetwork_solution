# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class Picking(models.Model):
    _inherit='stock.picking'
    invoice_state = fields.Selection(string="Invoice Control",
        selection=[('invoiced', 'Invoiced'),
        ('2binvoiced', 'To Be Invoiced'),
        ('none', 'Not Applicable'), ],  default='none')
    invoice_id = fields.Many2one('account.move', string="Account Invoice",readonly=True ,copy=False)

    # Override copy to take into account the invoice_id and status
    # when copying we want to unlink invoice_id and set invoice control to 2binvoiced
    @api.model
    def create(self, vals):
        if vals.get('invoice_id'):
            vals['invoice_id'] = ''
            vals['invoice_state'] = '2binvoiced'
        return super(Picking, self).create(vals)


    def create_invoice(self):
        invoice_obj = self.env['account.move']
        i_line_obj = self.env['account.move.line']
        sale_journal = self.env['account.journal'].search([('type','=','sale')])[0]
        sale_journal_id = sale_journal.id
        purch_journal = self.env['account.journal'].search([('type','=','purchase')])[0]
        purch_journal_id = purch_journal.id


        for obj in self:
            # Vendor Refund
            if obj.location_dest_id.usage == 'supplier':
                global inv_id
                i_line_id=[]
                for i in obj.move_lines:
                    accounts = i.product_id.product_tmpl_id.get_product_accounts()
                    price_unit = i.product_id.uom_id._compute_price(i.product_id.standard_price, i.product_uom)
                    line={
                    # 'invoice_id':inv_id.id,
                    'product_id':i.product_id.id,
                    'price_unit': price_unit,
                    'name':i.name,
                    'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                                  accounts['expense'].id,
                    'quantity':i.product_uom_qty,
                    # 'uom_id':i.product_uom.id,
                    }
                    i_line_id.append(line)
                inv_id= invoice_obj.create({
                    'partner_id':obj.partner_id.id,
                    'picking_id': self.id,
                    'invoice_date':obj.date_done,
                    'origin':obj.name,
                    'type':'in_refund',
                    'journal_id':purch_journal_id,
                    'invoice_line_ids':  i_line_id,
                    # 'account_id': obj.partner_id.property_account_payable_id.id,
                 })

            # Vendor Invoice
            elif obj.location_id.usage == 'supplier':
                    i_line_id=[]
                    for i in obj.move_lines:
                        accounts = i.product_id.product_tmpl_id.get_product_accounts()
                        price_unit = i.product_id.uom_id._compute_price(i.product_id.standard_price, i.product_uom)
                        line={
                        # 'move_id':inv_id.id,
                        'product_id':i.product_id.id,
                        'price_unit': price_unit,
                        'name':i.name,
                        'account_id':accounts.get('stock_input') and accounts['stock_input'].id or accounts['expense'].id,
                        'quantity':i.product_uom_qty,
                        # 'uom_id':i.product_uom.id,
                        }
                        i_line_id.append(line)

                    inv_id= invoice_obj.create({
                        'partner_id':obj.partner_id.id,
                        'picking_id': self.id,
                        'invoice_date': obj.date_done,
                        'type':'in_invoice',
                        'journal_id':purch_journal_id,
                        'invoice_line_ids': i_line_id,

                        # 'account_id': obj.partner_id.property_account_payable_id.id,
                            })


            # Customer Refund
            elif obj.location_id.usage == 'customer':
                i_line_id=[]
                for i in obj.move_lines:
                    accounts = i.product_id.product_tmpl_id.get_product_accounts()
                    price_unit = i.product_id.uom_id._compute_price(i.product_id.lst_price, i.product_uom)
                    line={
                        # 'invoice_id':inv_id.id,
                        'product_id':i.product_id.id,
                        'price_unit':price_unit,
                        'name':i.name,
                        'account_id':accounts.get('income') and accounts['income'].id or False,
                        'quantity':i.product_uom_qty,
                        # 'uom_id': i.product_uom.id,
                         }
                    i_line_id.append(line)

                inv_id= invoice_obj.create({
                    'partner_id':obj.partner_id.id,
                    'picking_id': self.id,
                    'invoice_date': obj.date_done,
                    'type':'out_refund',
                    'journal_id':sale_journal_id,
                    'invoice_line_ids':  i_line_id,

                    # 'account_id': obj.partner_id.property_account_receivable_id.id,
                     })


            elif obj.location_dest_id.usage == 'customer':
                i_line_id=[]
                for i in obj.move_lines:
                    accounts = i.product_id.product_tmpl_id.get_product_accounts()
                    price_unit = i.product_id.uom_id._compute_price(i.product_id.lst_price, i.product_uom)
                    line={
                        'product_id':i.product_id.id,
                        'price_unit':price_unit,
                        'name':i.name,
                        'account_id':accounts.get('income') and accounts['income'].id or False,
                        'quantity':i.product_uom_qty,
                        # 'uom_id': i.product_uom.id,
                        }
                    i_line_id.append(line)

                print('lines',i_line_id)
                [print(i) for i in i_line_id]
                inv_id= invoice_obj.create({
                    'partner_id':obj.partner_id.id,
                    'picking_id': self.id,
                    'invoice_date':obj.date_done,
                    'type':'out_invoice',
                    'journal_id':sale_journal_id,
                    'invoice_line_ids':i_line_id,
                    # 'account_id': obj.partner_id.property_account_receivable_id.id,
                     })

            else:
                break

            if inv_id :
                obj.write({'invoice_state':'invoiced'})
            self.invoice_id= inv_id.id

class AccountInvoice(models.Model):
    _inherit='account.move'
    picking_id = fields.Many2one('stock.picking','Picking invoice',readonly=True)

    def unlink(self):
        for invoice in self:
            if invoice.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
            else:
                invoice.picking_id.write({'invoice_state':'2binvoiced'})
        return super(AccountInvoice, self).unlink()
