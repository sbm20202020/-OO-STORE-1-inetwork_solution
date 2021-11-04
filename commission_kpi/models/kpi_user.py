# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import ast
from odoo.exceptions import ValidationError, UserError


class KpiUser(models.Model):
    _name = 'kpi.user'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    user_id=fields.Many2one('res.users',required=True,readonly = True,states = {'draft': [('readonly', False)]})
    date_from = fields.Date(string="Start Date", required=True,readonly = True,states = {'draft': [('readonly', False)]})
    date_to = fields.Date(string="End Date", required=True,readonly = True,states = {'draft': [('readonly', False)]})
    commission_amount=fields.Float(readonly=True,copy=False)
    active = fields.Boolean('Active',default=True)
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,index=True, default=lambda self: _('New'),tracking=1)

    _sql_constraints = [
        ('kpi_uniq', 'unique(date_from, date_to , user_id,active)', 'This KPI found'),
    ]

    @api.model
    def create(self, values):
        if values.get('name','New') == 'New':
           values['name'] = self.env['ir.sequence'].next_by_code('kpi.user')
        return super(KpiUser, self).create(values)




    state=fields.Selection([
        ('draft','Draft'),
        ('validate','Validate'),
        ('cancel','Cancel'),
    ],default='draft')
    user_id_kpi = fields.Many2one('res.users', string='User Created', index=True, tracking=True,
                              default=lambda self: self.env.user)

    sales_volume = fields.One2many('sales.volume', 'kpi_user_id',copy=False,readonly = True,states = {'draft': [('readonly', False)]})
    performance_value = fields.One2many('performance.value', 'kpi_user_id',copy=False,readonly = True,states = {'draft': [('readonly', False)]})
    market_share = fields.One2many('market.share', 'kpi_user_id',copy=False,readonly = True,states = {'draft': [('readonly', False)]})
    purchase_sales_commision = fields.One2many('purchase.sales.commision', 'kpi_user_id',copy=False,readonly = True,states = {'draft': [('readonly', False)]})
    total_basic_sales_volume = fields.Percent(string="Basic", compute="_compute_total_basic")
    total_basic_performance_value = fields.Percent(string="Basic", compute="_compute_total_basic")
    total_basic_market_share = fields.Percent(string="Basic", compute="_compute_total_basic")
    total_basic_purchase_sales_commision = fields.Percent(string="Basic", compute="_compute_total_basic")
    total_actual_sales_volume = fields.Percent(string="Actual", compute="_compute_total_basic")
    total_actual_performance_value = fields.Percent(string="Actual", compute="_compute_total_basic")
    total_actual_market_share = fields.Percent(string="Actual", compute="_compute_total_basic")
    total_actual_purchase_sales_commision = fields.Percent(string="Actual", compute="_compute_total_basic")

    total_basic = fields.Percent(string="Total Basic", compute="_compute_total")
    total_actual = fields.Percent(string="Total Actual", compute="_compute_total")


    def _get_commission_kpi(self):
        for rec in self:
                invoices = self.env['account.move'].search(
                    [('invoice_date', '>=', rec.date_from), ('type', '=', 'out_invoice'),
                     ('invoice_date', '<=', rec.date_to)]).sorted(key=lambda r: r.invoice_user_id.id)
                salesperson=rec.user_id
                if invoices:
                        total_amount_untaxed = 0.0
                        total_cost = 0.0
                        total_actual_kpi = 0
                        total_actual_kpi = rec.total_actual / 100

                        for invoice in invoices:
                            if invoice.invoice_user_id == salesperson:
                                products = invoice.invoice_line_ids.filtered(
                                    lambda self: self.product_id.type == 'product')
                                service = invoice.invoice_line_ids.filtered(
                                    lambda self: self.product_id.type != 'product')
                                if products:
                                    for product in products:
                                        cost_product = sum(value.value / value.quantity for value in
                                                           self.env['stock.valuation.layer'].search(
                                                               [('stock_move_id.origin', '=', invoice.invoice_origin)])
                                                           if
                                                           value.product_id.type == 'product' and value.product_id == product.product_id)
                                        total_amount_untaxed += product.price_subtotal
                                        total_cost += cost_product


                                if service:
                                    for ser in service:
                                        # cost_service = sum(value.value / value.quantity for value in
                                        #                    self.env['stock.valuation.layer'].search(
                                        #                        [(
                                        #                         'stock_move_id.origin', '=', invoice.invoice_origin)]) if value.product_id.type != 'product' and value.product_id == ser.product_id)
                                        total_amount_untaxed += ser.price_subtotal
                                        cost_service = ser.price_subtotal * 70 / 100
                                        total_cost += cost_service


                        total_net_profit = total_amount_untaxed - total_cost
                        total_percentage = (100 - (
                                    total_cost / total_amount_untaxed * 100)) if total_amount_untaxed != 0.0 else 0.0
                        total_comm_amount = total_net_profit * 5 / 100
                        after_kpi = total_comm_amount * total_actual_kpi
                        rec.commission_amount=after_kpi
                else:
                    rec.commission_amount = 0.0

    @api.depends('sales_volume','performance_value','market_share','purchase_sales_commision')
    def _compute_total_basic(self):
        for rec in self:
            rec.total_basic_sales_volume= sum(sales.basic for sales in rec.sales_volume)
            rec.total_basic_performance_value=sum(per.basic for per in rec.performance_value)
            rec.total_basic_market_share=sum(market.basic for market in rec.market_share)
            rec.total_basic_purchase_sales_commision=sum(PSC.basic for PSC in rec.purchase_sales_commision)

            rec.total_actual_sales_volume= sum(sales.actual for sales in rec.sales_volume)
            rec.total_actual_performance_value=sum(per.actual for per in rec.performance_value)
            rec.total_actual_market_share=sum(market.actual for market in rec.market_share)
            rec.total_actual_purchase_sales_commision=sum(PSC.actual for PSC in rec.purchase_sales_commision)

    @api.depends('sales_volume','performance_value','market_share','purchase_sales_commision')
    def _compute_total(self):
        for rec in self:
            # if rec.total_basic_sales_volume+rec.total_basic_performance_value+rec.total_basic_market_share+rec.total_basic_purchase_sales_commision > 100:
            #     raise ValidationError(_("Total Basic should n't bigger than 100%"))
            # else:
            rec.total_basic =rec.total_basic_sales_volume+rec.total_basic_performance_value+rec.total_basic_market_share+rec.total_basic_purchase_sales_commision
            rec.total_actual =rec.total_actual_sales_volume+rec.total_actual_performance_value+rec.total_actual_market_share+rec.total_actual_purchase_sales_commision

    @api.onchange('sales_volume','performance_value','market_share','purchase_sales_commision')
    def _constrains_total_basic(self):
        for rec in self:
            total=sum(sales.basic for sales in rec.sales_volume)+sum(per.basic for per in rec.performance_value)+sum(market.basic for market in rec.market_share)+sum(PSC.basic for PSC in rec.purchase_sales_commision)
            if total > 100:
                raise ValidationError(_('Total Basic should be bigger than 100 %'))


    @api.model
    def default_get(self, fields_default):
        res = super(KpiUser, self).default_get(fields_default)
        sales_volume = [(0, 0, {'name': self.env.ref('commission_kpi.sales_volume_1').name,
                                'basic': self.env.ref('commission_kpi.sales_volume_1').basic, 'actual': 0.0}),
                        (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_2').name,
                                'basic': self.env.ref('commission_kpi.sales_volume_2').basic, 'actual': 0.0}),
                        (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_3').name,
                                'basic': self.env.ref('commission_kpi.sales_volume_3').basic, 'actual': 0.0}),
                        (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_4').name,
                                'basic': self.env.ref('commission_kpi.sales_volume_4').basic, 'actual': 0.0})]
        performance_value = [
            (0, 0, {'name': self.env.ref('commission_kpi.performance_value_1').name,
                    'basic': self.env.ref('commission_kpi.performance_value_1').basic, 'actual': 0.0}),
            (0, 0, {'name': self.env.ref('commission_kpi.performance_value_2').name,
                    'basic': self.env.ref('commission_kpi.performance_value_2').basic, 'actual': 0.0}),
            (0, 0, {'name': self.env.ref('commission_kpi.performance_value_3').name,
                    'basic': self.env.ref('commission_kpi.performance_value_3').basic, 'actual': 0.0}),
            (0, 0, {'name': self.env.ref('commission_kpi.performance_value_4').name,
                    'basic': self.env.ref('commission_kpi.performance_value_4').basic, 'actual': 0.0}),
            (0, 0, {'name': self.env.ref('commission_kpi.performance_value_5').name,
                    'basic': self.env.ref('commission_kpi.performance_value_5').basic, 'actual': 0.0})
        ]
        market_share = [
            (0, 0, {'name': self.env.ref('commission_kpi.market_share_1').name,
                    'basic': self.env.ref('commission_kpi.market_share_1').basic, 'actual': 0.0}),
            (0, 0, {'name': self.env.ref('commission_kpi.market_share_2').name,
                    'basic': self.env.ref('commission_kpi.market_share_2').basic, 'actual': 0.0}),
            (0, 0, {'name': self.env.ref('commission_kpi.market_share_3').name,
                    'basic': self.env.ref('commission_kpi.market_share_3').basic, 'actual': 0.0}),
            (0, 0, {'name': self.env.ref('commission_kpi.market_share_4').name,
                    'basic': self.env.ref('commission_kpi.market_share_4').basic, 'actual': 0.0}),

        ]
        purchase_sales_commision = [
            (0, 0, {'name': self.env.ref('commission_kpi.purchase_sales_commision_1').name,
                    'basic': self.env.ref('commission_kpi.purchase_sales_commision_1').basic, 'actual': 0.0}),
            (0, 0, {'name': self.env.ref('commission_kpi.purchase_sales_commision_2').name,
                    'basic': self.env.ref('commission_kpi.purchase_sales_commision_2').basic, 'actual': 0.0}),
        ]
        res.update({'sales_volume': sales_volume, 'performance_value': performance_value,
                    'market_share': market_share,
                    'purchase_sales_commision': purchase_sales_commision})
        return res




    def validate(self):
        for rec in self:
            rec._get_commission_kpi()
            rec.write({'state':'validate'})


    # def cancel(self):
    #     for rec in self:
    #         rec.write({'state':'cancel'})
    #
    # def set_to_draft(self):
    #     for rec in self:
    #         rec.write({'state':'draft'})

    @api.constrains('date_from','date_to')
    def set_cons_date(self):
        if self.date_from != False and self.date_to != False and self.date_from > self.date_to:
                raise ValidationError(_("Start date should be less than end date"))

    def unlink(self):
        for rec in self:
            if rec.state in ['validate']:
                raise ValidationError(_("you can not delete KPI validate"))
        return super(KpiUser, self).unlink()



