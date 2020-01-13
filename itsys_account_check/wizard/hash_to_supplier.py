from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class HashToSupplier(models.TransientModel):
    _name = 'check.hash.supplier'

    partner_id = fields.Many2one(comodel_name='res.partner', domain=[('supplier', '=', True)], required=True,string='Hashed to Supplier')

    # @api.multi
    def hash_check_supplier(self):
        active_id = self._context.get('active_id')
        check_id = self.env['account.check'].browse(active_id)
        if check_id.journal_id.journal_state != 'cheque_hashed':
            raise UserError(_('You can not use this Journal for that state'))
        check_id.check_move_create(0.0, check_id.amount)
        check_id.write({'state': 'cheque_hashed', 'supplier_id': self.partner_id.id})


HashToSupplier()
