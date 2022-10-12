# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError

class HrPayslipEmployees(models.TransientModel):
    _inherit ='hr.payslip.employees'

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        if not self.employee_ids:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = self.employee_ids._get_contracts(payslip_run.date_start, payslip_run.date_end,
                                                     states=['open', 'close'])
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', self.employee_ids.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        validated = work_entries.action_validate()
        if not validated:
            raise UserError(_("Some work entries could not be validated."))

        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in contracts:
            values = dict(default_values, **{
                'employee_id': contract.employee_id.id,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslip = self.env['hr.payslip'].new(values)
            payslip._onchange_employee()
            values = payslip._convert_to_write(payslip._cache)
            payslips += Payslip.create(values)
        # payslips.compute_sheet()
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }


class HrPayslip(models.Model):
    _inherit ='hr.payslip'

    department_id=fields.Many2one('hr.department',related='employee_id.department_id',store=True)
    def _get_new_input_lines(self):
        res=[]
        lines = {}
        other_input = self.env['hr.payslip.input.type'].search([('struct_ids','in',[self.struct_id.id]),('code', '!=', 'LO')])
        for line in other_input:
            lines = {
                'input_type_id': line.id,
                'amount': 0.0,
            }
            res.append(lines)
        if self.struct_id:
            input_line_values =res
            input_lines = self.input_line_ids.browse([])
            for r in input_line_values:
                input_lines |= input_lines.new(r)
            return input_lines
        else:
            return [(5, False, False)]

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        res=super(HrPayslip, self)._onchange_employee()
        self.input_line_ids = self._get_new_input_lines()
        return res

    def _get_worked_day_lines(self):
        res=super(HrPayslip, self)._get_worked_day_lines()
        lines={}
        work_entry=self.env['hr.work.entry.type'].search([('appear_on_payslip','=',True)])
        for line in work_entry:
                if len(res) > 0:
                    if line.id != res[0]['work_entry_type_id']:
                        lines = {
                            'sequence': line.sequence,
                            'work_entry_type_id': line.id,
                            'number_of_days':0.0,
                            'number_of_hours': 0.0,
                            'amount': 0.0,
                        }
                        res.append(lines)
                else:
                    lines = {
                        'sequence': line.sequence,
                        'work_entry_type_id': line.id,
                        'number_of_days':0.0,
                        'number_of_hours': 0.0,
                        'amount': 0.0,
                    }
                    res.append(lines)
        return res

class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'
    appear_on_payslip=fields.Boolean()
    number_of_days=fields.Float()
    
    @api.constrains('number_of_days')
    def not_minus(self):
        for rec in self:
            if rec.number_of_days < 0:
                raise ValidationError(_('Number Of Days Should Not Be Less Than Zero'))

class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'
    input_path=fields.Boolean()
