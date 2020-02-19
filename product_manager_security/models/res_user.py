from odoo import models, fields, api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
from openerp import SUPERUSER_ID

class ResUsers(models.Model):
    _inherit = 'res.users'
    is_confirm_sale_order_line=fields.Boolean()
    is_confirm_purchase_order_line=fields.Boolean()
