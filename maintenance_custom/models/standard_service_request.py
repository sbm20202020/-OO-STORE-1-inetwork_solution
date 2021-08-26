# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
import threading
_logger = logging.getLogger(__name__)


class MaintenanceStage(models.Model):
    _name = 'maintenance.request'
    _inherit = ['maintenance.request', 'mail.thread', 'mail.activity.mixin']

    type = fields.Selection([('standard', 'standard'), ('shnider', 'Shnider')], 'Type')
    picking_id = fields.Many2one('stock.picking', string='Receipts', copy=False, store=True)
    sales_order_id = fields.Many2one('sale.order', 'Sales Order', copy=False, store=True)
    delivery_order_id = fields.Many2one('stock.picking', string='Delivery Order', copy=False, store=True)
    picking_count = fields.Integer(string='Picking count', default=0, store=True)
    receipt_created = fields.Boolean('Receipt Created')
    stage_name = fields.Char('Stage Name', default='New Request')
    picking_id_stage = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], related='picking_id.state')
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Medium'), ('3', 'High')], string='Priority')
    request_date = fields.Date('Request Date', related='equipment_id.assign_date')
    # @api.onchange('user_id')
    # def onchange_company_id(self):
    #     users = self.env.ref('maintenance_custom.group_maintenance_manager').users.ids
    #     return {'domain': {'user_id': [('id', 'in', users)]}}

    @api.constrains('schedule_date')
    def date_constrains(self):
        for rec in self:
            if rec.schedule_date.date() < datetime.today().date():
                raise ValidationError(_('Sorry, Schedule Date Must be greater Than Current Date...'))

    @api.constrains('duration')
    def duration_constrains(self):
        for rec in self:
            if rec.duration < 0:
                raise ValidationError(_('Sorry, Duration Must be greater Than or Equal 0...'))

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            self.user_id = self.equipment_id.technician_user_id if self.equipment_id.technician_user_id else self.equipment_id.category_id.technician_user_id
            self.category_id = self.equipment_id.category_id
            if self.equipment_id.maintenance_team_id:
                self.maintenance_team_id = self.equipment_id.maintenance_team_id.id
            if self.equipment_id.assign_date:
                self.request_date = self.equipment_id.assign_date

    def action_inspection(self):
        if self.type == 'standard':
            stage_obj = self.env['maintenance.stage'].search([('name', '=', 'Inspection')])
            self.stage_id = stage_obj.id
        else:
            self.shnider_stage_id = 'inspection'
        self.stage_name = 'Inspection'
        # threaded_calculation = threading.Thread(target=self._procure_calculation_orderpoint, args=())
        # threaded_calculation.start()
        # notification_ids = []
        # notification_ids.append((0, 0, {
        #     'res_partner_id': self.user_id.id,
        #     'notification_type': 'inbox'}))
        # self.message_post(
        #     body='the virtual stock of today is below the min of the defined order point!', message_type='notification',
        #     subtype='mail.mt_comment', author_id=self.env.user.partner_id.id,
        #     notification_ids=notification_ids)

    def action_fixable(self):
        if self.type == 'standard':
            stage_obj = self.env['maintenance.stage'].search([('name', '=', 'Fixable')])
            self.stage_id = stage_obj.id
        else:
            self.shnider_stage_id = 'fixable'
            self.fixable = True
        self.stage_name = 'fixable'

    def action_not_fixable(self):
        if self.type == 'standard':
            stage_obj = self.env['maintenance.stage'].search([('name', '=', 'Closed')])
            self.stage_id = stage_obj.id
        else:
            self.shnider_stage_id = 'not_fixable'
        self.stage_name = 'not_fixable'

    def action_tested(self):
        if self.type == 'standard':
            stage_obj = self.env['maintenance.stage'].search([('name', '=', 'Tested')])
            self.stage_id = stage_obj.id
            self.stage_name = 'Tested'

    def action_closed(self):
        if self.type == 'standard':
            stage_obj = self.env['maintenance.stage'].search([('name', '=', 'Closed')])
            self.stage_id = stage_obj.id
            self.stage_name = 'Closed'

    def action_view_picking(self):
        """ This function returns an action that display existing picking orders of given Maintenance ids. When only one found, show the picking immediately.
        """
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        # override the context to get rid of the default filtering on operation type
        result['context'] = {'default_origin': self.name, 'default_id': self.picking_id.id}
        pick_ids = self.mapped('picking_id')
        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = pick_ids.id
        return result

    def action_create_delivery_order(self):
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
        self.delivery_order_id = new_delivery_order.id
        if self.type == 'shnider':
            self.shnider_stage_id = 'created_DO'
            self.stage_name = 'Created DO'
        else:
            stage_obj = self.env['maintenance.stage'].search([('name', '=', 'Created DO')])
            self.stage_id = stage_obj.id
            self.stage_name = 'Created DO'
        return new_delivery_order, picking_type_id

    # def action_inspection(self):
    #     ir_model_data = self.env['ir.model.data']
    #     template_res = self.env['mail.template']
    #     template_id = ir_model_data.get_object_reference('account', 'invoice_form')[1]
    #     template = template_res.browse(template_id)
    #
    #     for rec in self:
    #         # if rec.signature_general_manager == False:
    #         #     raise ValidationError(_("You Should Enter Signature"))
    #
    #         # rec.write({'state': 'confirm'})
    #         # users = self.env['res.users'].search([])
    #         # for user in users:
    #         #     if user.has_group('account.group_account_manager'):
    #         rec.activity_schedule('letter_guarantee.schdule_activity_letter_guarantee_id', rec.date,
    #                               user_id=rec.user_id.id,
    #                               summary='letter gurantee confirmed , you can create Quotation')
    #         email_values = {
    #             'email_to': rec.user_id.email,
    #             'email_from': rec.user_id.company_id.email,
    #             'subject': 'Letter Guarantee',
    #         }
    #         base_url = request.env['ir.config_parameter'].get_param('web.base.url')
    #         base_url += '/web#id=%d&view_type=form&model=%s' % (rec.id, rec._name)
    #
    #         template.body_html = '<p>Dear Sir ${(object.name)},''<br/><br/>Kindly be noted that this letter gurantee ' + str(
    #             rec.name) + ' confirmed , you can create Quotation <br/>' \
    #                         'Thanks,<br/>' \
    #                         '${(object.company_id.name)}<br/><br/>' \
    #                         '<button style="background-color: #e7e7e7;font-size: 12px;border-radius: 12px;padding: 14px 40px;color:white;"><a  href=%s>View Letter Guarantee </a></button>' % (
    #                                  base_url)
    #
    #         template.send_mail(rec.user_id.id, force_send=True, email_values=email_values)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        ir_model_data = self.env['ir.model.data']
        template_res = self.env['mail.template']
        maintenance_obj = self.env['maintenance.request'].search([('sales_order_id', '=', self.id)])

        # users = self.env['res.users'].search([])
        # contracts = self.search([])
        # contract_list = []

        template_id = ir_model_data.get_object_reference('maintenance_custom',
                                                         'sales_order_confirmation_template')[1]
        template = template_res.browse(template_id)

        email_values = {
            'email_to': maintenance_obj.user_id.email,
            'email_from': res.user_id.email,
            'subject': 'Sales Order Confirmed',
        }
        template.body_html = '<p>Dear ${(object.name)},''<br/><br/>Kindly be noted that this sale Order is Confirmed ,<br/>' + str(
            res.name) + 'Thanks,<br/>' \
                         '${(object.company_id.name)}'

        template.send_mail(res.user_id.id, force_send=True, email_values=email_values)
        return res

    # def send_email_notification(self):
    #     ir_model_data = self.env['ir.model.data']
    #     template_res = self.env['mail.template']
    #     maintenance_obj = self.env['maintenance.request'].search([('sales_order_id', '=', self.id)])
    #
    #     # users = self.env['res.users'].search([])
    #     # contracts = self.search([])
    #     # contract_list = []
    #
    #     template_id = ir_model_data.get_object_reference('maintenance_custom',
    #                                                      'sales_order_confirmation_template')[1]
    #     template = template_res.browse(template_id)
    #
    #     email_values = {
    #         'email_to': maintenance_obj.user_id.email,
    #         'email_from': self.user_id.email,
    #         'subject': 'Contract End Date',
    #     }
    #     template.body_html = '<p>Dear ${(object.name)},''<br/><br/>Kindly be noted that this sale Order is Confirmed ' + str(
    #         self.name) +  'Thanks,<br/>' \
    #                          '${(object.company_id.name)}'
    #
    #     template.send_mail(self.user_id.id, force_send=True, email_values=email_values)




