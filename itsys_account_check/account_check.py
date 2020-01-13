from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError

class account_check(models.Model):
    _name= 'account.check'

    @api.model
    def _default_state(self):
        if self._context.get('default_collect_ok'):
            return 'draft_collect'
        else: return 'draft_pay'

    name= fields.Char('Name',readonly=True)
    pay_ok=fields.Boolean('pay_ok')
    collect_ok=fields.Boolean('collect_ok')
    to_check=fields.Boolean('To Review')
    date=fields.Date('Date',required=True)
    due_date=fields.Date('Due Date')
    amount=fields.Float('Amount')
    ref= fields.Char('Reference',required=True)
    comm= fields.Char('Communication')
    journal_id = fields.Many2one('account.journal', string='Journal',required=True,domain=[('type','=','bank')])
    company_id = fields.Many2one('res.company', string='Company')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    state= fields.Selection([('draft_collect', 'New'),
                               ('draft_pay', 'account.checkNew'),
                               ('open', 'Open'),
                               ('receive', 'Paper Receive'),
                               ('deposit', 'Bank Deposit'),
                               ('collect', 'Collect Cheque'),
                               ('return', 'Return Check'),
                               ('cash_payment', 'Cash Payment'),
                               ('return_client', 'Return to Client'),
                               ('cheque_hashed', 'Hash cheque to supplier'),
                               ('return_cheque_hashed', 'Return hashed cheque to supplier'),
                               ('deposit_direct', 'Direct Deposit'),
                               ('generate_supp', 'Generate Cheque - Supplier'),
                               ('bank_payment', 'Bank Payment'),
                               ('cheque_return', 'Cheque Return from bank'),
                               ('confirm', 'Closed')],
                              'Status', required=True, default=_default_state,readonly="1",
                              copy=False, )
    supplier_id=fields.Many2one(comodel_name='res.partner', domain=[('supplier', '=', True)],string='Hashed to Supplier')

    _sql_constraints = [
        ('amount_greater_than_zero', 'CHECK(amount > 0)','Error ! Amount cannot be zero or less')
    ]

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('account.check') or '/'
        return super(account_check, self).create(vals)

    # @api.multi
    def unlink(self):
        if self.state !='draft':
            raise UserError(_('You can not delete a check that is not in draft state'))
        return super(account_check, self).unlink()

    # def check_date(self):
    #     self.env.cr.execute("select max(date) from account_move where name='"+str(self.name)+"'")
    #     res = self.env.cr.fetchone()[0]
    #     if res and self.date < res:
    #         raise UserError(_('Date cannot be earlier than last move date'))

    def check_move_create(self,debit,credit):
        # self.check_date()
        account_move_obj = self.env['account.move']
        if self.journal_id.journal_state=='receive':
            account_move_obj.create({'name': self.name, 'ref': self.ref,
                                     'journal_id': self.journal_id.id,
                                     'line_ids': [(0, 0, {
                                         'name': self.name, 'account_id': self.partner_id.property_account_receivable_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit': credit, 'debit': debit, 'date_maturity': self.due_date,
                                     }), (0, 0, {
                                         'name': self.name, 'account_id': self.journal_id.default_debit_account_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit': debit, 'debit': credit, 'date_maturity': self.due_date,
                                     })],'date': self.date})
            return True
        if self.journal_id.journal_state=='generate_supp':
            account_move_obj.create({'name': self.name, 'ref': self.ref,
                                     'journal_id': self.journal_id.id,
                                     'line_ids': [(0, 0, {
                                         'name': self.name, 'account_id': self.journal_id.default_debit_account_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit': credit, 'debit': debit, 'date_maturity': self.due_date,
                                     }), (0, 0, {
                                         'name': self.name, 'account_id': self.partner_id.property_account_payable_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit': debit, 'debit': credit, 'date_maturity': self.due_date,
                                     })],'date': self.date})
            return True

        if self.journal_id.journal_state == 'cheque_hashed':
            account_move_obj.create({'name': self.name, 'ref': self.ref,
                                     'journal_id': self.journal_id.id,
                                     'line_ids': [(0, 0, {
                                         'name': self.name, 'account_id': self.partner_id.property_account_payable_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit': credit, 'debit': debit, 'date_maturity': self.due_date,
                                     }), (0, 0, {
                                         'name': self.name,
                                         'account_id': self.partner_id.property_account_payable_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit': debit, 'debit': credit, 'date_maturity': self.due_date,
                                     })], 'date': self.date})
            return True

        account_move_obj.create({'name' : self.name,'ref':self.ref,
                                         'journal_id' : self.journal_id.id,
                                         'line_ids':[(0, 0, {
                                                'name': self.name,'account_id': self.journal_id.default_credit_account_id.id,'partner_id': self.partner_id.id,
                                                'credit': credit,'debit': debit, 'date_maturity': self.due_date,
                                            }),(0, 0, {
                                                'name': self.name,'account_id': self.journal_id.default_debit_account_id.id,'partner_id': self.partner_id.id,
                                                'credit': debit,'debit': credit, 'date_maturity': self.due_date,
                                            })],
                                         'date': self.date})

    def close(self):
        self.write({'state':'confirm'})

    def button_receive(self):
        if self.journal_id.journal_state!='receive':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'receive'})

    def button_deposit_check(self):
        if self.journal_id.journal_state!='deposit':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'deposit'})

    def button_collect_check(self):
        if self.journal_id.journal_state!='collect':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'collect'})

    def button_bnk_return_check(self):
        if self.journal_id.journal_state!='cheque_return':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'return'})

    def button_return_client_check(self):
        if self.journal_id.journal_state!='return_client':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'return_client'})

    def button_direct_deposit(self):
        if self.journal_id.journal_state!='deposit_direct':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'deposit_direct'})

    def button_generate_chk_supp(self):
        if self.journal_id.journal_state!='generate_supp':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'generate_supp'})

    def button_bnk_payment(self):
        if self.journal_id.journal_state!='bank_payment':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'bank_payment'})

    def button_pay_bnk_return_check(self):
        if self.journal_id.journal_state!='cheque_return':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'cheque_return'})

    def button_check_hashed(self):
        if self.journal_id.journal_state!='cheque_hashed':
            raise UserError(_('You can not use this Journal for that state'))
        # self.check_move_create(0.0,self.amount)
        self.write({'state':'cheque_hashed'})

        wizard_form = self.env.ref('itsys_account_check.hash_to_supplier_wiz_form', False)
        view_id = self.env['check.hash.supplier']

        # new = view_id.create({})
        return {
            'name': _('Choose Vendor'),
            'type': 'ir.actions.act_window',
            'res_model': 'check.hash.supplier',
            # 'res_id': new.id,
            'view_id': wizard_form.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }

    def button_return_check_hashed(self):
        if self.journal_id.journal_state!='return_cheque_hashed':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(0.0,self.amount)
        self.write({'state':'return_cheque_hashed','supplier_id':False})

    def button_client_return_check(self):
        if self.journal_id.journal_state != 'return_client':
            raise UserError(_('You can not use this Journal for that state'))
        self.check_move_create(self.amount, 0.0)
        self.write({'state': 'return_client'})

class account_journal(models.Model):
    _inherit = 'account.journal'
    journal_state=fields.Selection(
            [('receive', 'Receive')
                ,('deposit','Deposit')
                , ('collect', 'Collect')
                , ('return','Return')
                , ('return_client', 'Return to Client')
                , ('deposit_direct', 'Direct deposit')
                , ('generate_exp','Generate check-Expenses')
                ,('generate_supp','Generate check-Supplier')
                , ('bank_payment','Bank Payment'),
             ('cheque_return','Cheque Return from bank'),
             ('cheque_hashed','Hash chk to supplier'),
             ('return_cheque_hashed','Return hashed chk to supplier'),
            ], 'Check Journal State', help="Select the tybe of journal to deal with bank checks")
    bnk_payable= fields.Boolean('Bank Payable')
