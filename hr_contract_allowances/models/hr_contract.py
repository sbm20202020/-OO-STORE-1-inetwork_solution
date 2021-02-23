# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, ValidationError


class Allowance(models.Model):
    _name = 'hr.allowance'
    _rec_name = 'name'
    _description = 'Allowance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Allowance Name", required=True)
    active = fields.Boolean(string="Active", default=True)

    def unlink(self):
        for line in self:
            contract_ids = self.env['hr.contract'].search([])
            for contract in contract_ids:
                for allowance in contract.allowances_ids:
                    if allowance.allowance_id == line:
                        raise ValidationError(_('You can not delete Allowance used in Contract.'))
        return super(Allowance, self).unlink()


class ContractAllowanceLine(models.Model):
    _name = 'hr.contract.allowance.line'
    _rec_name = 'allowance_id'
    _description = 'Contract Allowance Line'

    allowance_id = fields.Many2one(comodel_name="hr.allowance", string="Allowance")
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract")
    amount = fields.Float(string="Amount")


class Contract(models.Model):
    _name = "hr.contract"
    _inherit = 'hr.contract'

    # @api.multi
    @api.constrains('state')
    def _check_state(self):
        for record in self:
            if record.state == 'open':
                contract_ids = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id), ('state', '=', 'open')])
                if len(contract_ids) > 1:
                    raise exceptions.ValidationError(_('Employee Must Have Only One Running Contract'))

    allowances_ids = fields.One2many(comodel_name="hr.contract.allowance.line", inverse_name="contract_id")

    # @api.multi
    def get_all_allowances(self):
        return sum(self.allowances_ids.mapped('amount'))
