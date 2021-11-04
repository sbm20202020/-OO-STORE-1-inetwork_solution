from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

from datetime import datetime


class ResUsers(models.Model):
    _inherit = 'res.users'
    sales_volume = fields.One2many('sales.volume', 'user_id')
    performance_value = fields.One2many('performance.value', 'user_id')
    market_share = fields.One2many('market.share', 'user_id')
    purchase_sales_commision = fields.One2many('purchase.sales.commision', 'user_id')

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






    # @api.model
    # def default_get(self, fields_default):
    #     res = super(ResUsers, self).default_get(fields_default)
    #
    #
    #     sales_volume = [(0, 0, {'name': self.env.ref('commission_kpi.sales_volume_1').name,
    #                             'basic': self.env.ref('commission_kpi.sales_volume_1').basic, 'actual': 0.0}),
    #                     (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_2').name,
    #                             'basic': self.env.ref('commission_kpi.sales_volume_2').basic, 'actual': 0.0}),
    #                     (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_3').name,
    #                             'basic': self.env.ref('commission_kpi.sales_volume_3').basic, 'actual': 0.0}),
    #                     (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_4').name,
    #                             'basic': self.env.ref('commission_kpi.sales_volume_4').basic, 'actual': 0.0})]
    #     performance_value = [
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_1').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_1').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_2').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_2').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_3').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_3').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_4').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_4').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_5').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_5').basic, 'actual': 0.0})
    #     ]
    #     market_share = [
    #         (0, 0, {'name': self.env.ref('commission_kpi.market_share_1').name,
    #                 'basic': self.env.ref('commission_kpi.market_share_1').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.market_share_2').name,
    #                 'basic': self.env.ref('commission_kpi.market_share_2').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.market_share_3').name,
    #                 'basic': self.env.ref('commission_kpi.market_share_3').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.market_share_4').name,
    #                 'basic': self.env.ref('commission_kpi.market_share_4').basic, 'actual': 0.0}),
    #
    #     ]
    #     purchase_sales_commision = [
    #         (0, 0, {'name': self.env.ref('commission_kpi.purchase_sales_commision_1').name,
    #                 'basic': self.env.ref('commission_kpi.purchase_sales_commision_1').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.purchase_sales_commision_2').name,
    #                 'basic': self.env.ref('commission_kpi.purchase_sales_commision_2').basic, 'actual': 0.0}),
    #     ]
    #     res.update({'sales_volume': sales_volume, 'performance_value': performance_value,
    #                 'market_share': market_share,
    #                 'purchase_sales_commision': purchase_sales_commision})
    #     return res
    #
    #
    # def cron_default(self):
    #     res = self.search([])
    #
    #     sales_volume = [(0, 0, {'name': self.env.ref('commission_kpi.sales_volume_1').name,
    #                             'basic': self.env.ref('commission_kpi.sales_volume_1').basic, 'actual': 0.0}),
    #                     (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_2').name,
    #                             'basic': self.env.ref('commission_kpi.sales_volume_2').basic, 'actual': 0.0}),
    #                     (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_3').name,
    #                             'basic': self.env.ref('commission_kpi.sales_volume_3').basic, 'actual': 0.0}),
    #                     (0, 0, {'name': self.env.ref('commission_kpi.sales_volume_4').name,
    #                             'basic': self.env.ref('commission_kpi.sales_volume_4').basic, 'actual': 0.0})]
    #
    #     performance_value = [
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_1').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_1').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_2').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_2').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_3').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_3').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_4').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_4').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.performance_value_5').name,
    #                 'basic': self.env.ref('commission_kpi.performance_value_5').basic, 'actual': 0.0})
    #     ]
    #
    #     market_share = [
    #         (0, 0, {'name': self.env.ref('commission_kpi.market_share_1').name,
    #                 'basic': self.env.ref('commission_kpi.market_share_1').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.market_share_2').name,
    #                 'basic': self.env.ref('commission_kpi.market_share_2').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.market_share_3').name,
    #                 'basic': self.env.ref('commission_kpi.market_share_3').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.market_share_4').name,
    #                 'basic': self.env.ref('commission_kpi.market_share_4').basic, 'actual': 0.0}),
    #
    #     ]
    #
    #     purchase_sales_commision = [
    #         (0, 0, {'name': self.env.ref('commission_kpi.purchase_sales_commision_1').name,
    #                 'basic': self.env.ref('commission_kpi.purchase_sales_commision_1').basic, 'actual': 0.0}),
    #         (0, 0, {'name': self.env.ref('commission_kpi.purchase_sales_commision_2').name,
    #                 'basic': self.env.ref('commission_kpi.purchase_sales_commision_2').basic, 'actual': 0.0}),
    #     ]
    #     for rec in res:
    #         if len(rec.sales_volume) == 0:
    #             rec.sales_volume=sales_volume
    #         if len(rec.performance_value) == 0:
    #             rec.performance_value = performance_value
    #         if len(rec.market_share) == 0:
    #             rec.market_share = market_share
    #         if len(rec.purchase_sales_commision) == 0:
    #             rec.purchase_sales_commision = purchase_sales_commision
    #


    @api.onchange('sales_volume','performance_value','market_share','purchase_sales_commision')
    def _constrains_total_basic(self):
        for rec in self:
            total=sum(sales.basic for sales in rec.sales_volume)+sum(per.basic for per in rec.performance_value)+sum(market.basic for market in rec.market_share)+sum(PSC.basic for PSC in rec.purchase_sales_commision)
            if total > 100:
                raise ValidationError(_('Total Basic should be bigger than 100 %'))
