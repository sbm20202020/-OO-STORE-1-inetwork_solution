# -*- coding: utf-8 -*-
import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


from odoo.tools import float_compare

_logger = logging.getLogger(__name__)




class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = self._search(['|',('default_code', '=', name),('model','ilike',name)] + args, limit=limit, access_rights_uid=name_get_uid)
                if not product_ids:
                    product_ids = self._search(['|',('barcode', '=', name),('model','ilike',name)] + args, limit=limit, access_rights_uid=name_get_uid)
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = self._search(args + [('default_code', operator, name)], limit=limit)
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, access_rights_uid=name_get_uid)
                    product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                product_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = self._search([('default_code', '=', res.group(2))] + args, limit=limit, access_rights_uid=name_get_uid)
            # still no results, partner in context: search on supplier info as last hope to find something
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)], access_rights_uid=name_get_uid)
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit, access_rights_uid=name_get_uid)
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_equipment = fields.Boolean(string="Is equipment?")
    default_equipment_category_id = fields.Many2one('maintenance.equipment.category', string="Default Equipment Category")
    equipment_assign_to	 = fields.Selection( [('department', 'Department'), ('employee', 'Employee'), ('other', 'Other')],
        string='Used By', default='employee')
    maintenance_team_id = fields.Many2one('maintenance.team', string="Maintenance Team")
    technician_user_id =fields.Many2one('res.users', string="Technician")
    model = fields.Char(string="Model")
    equipment_ids = fields.One2many('maintenance.equipment', 'product_tmpl_id', help="The Equipments of this product")
    equipment_count = fields.Integer(string='Equipments', compute='_compute_equipment_count')

    @api.depends("equipment_ids")
    def _compute_equipment_count(self):
        """
        Calculate the number of equipment linked for each product
        :return:
        """
        for product in self:
            product.equipment_count = len(product.equipment_ids)


    def action_view_equipment(self):
        '''
        This function returns an action that display equipments linked with this product,
         It can either be a in a list or in a form view, if there is only one equipment to show
        '''
        action = self.env.ref('maintenance.hr_equipment_action').read()[0]
        equipments = self.mapped('equipment_ids')
        if len(equipments) > 1:
            action['domain'] = [('id', 'in', equipments.ids)]
        elif equipments:
            action['views'] = [(self.env.ref('maintenance.hr_equipment_view_form').id, 'form')]
            action['res_id'] = equipments.id
        return action


    @api.onchange('is_equipment')
    def _onchange_is_equipment(self):
        """
        Set product tracking to serial if the Is equipment is changed and equal True, if it changed to False
        then set tracking to none
        :return:
        """
        if self.is_equipment:
            self.tracking = 'serial'
        else:
            self.tracking = 'none'

    @api.onchange('default_equipment_category_id')
    def _onchange_default_equipment_category_id(self):
        """
        Set technician to the equipment category responsible
        :return:
        """
        if self.default_equipment_category_id.technician_user_id:
            self.technician_user_id = self.default_equipment_category_id.technician_user_id.id
