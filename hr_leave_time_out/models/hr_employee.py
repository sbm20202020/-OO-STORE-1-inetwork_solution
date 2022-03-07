from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.osv import expression


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    from_time_off_ids=fields.Many2many('hr.leave.allocation','emptimeoff_rel','col1','col2')

    def action_validate(self):
        res=super(HrLeaveAllocation, self).action_validate()
        for rec in self:
            for all in rec.from_time_off_ids:
                all.action_refuse()
        return res

class HrLeaveNextEmployee(models.TransientModel):
    _name = 'hr.leave.next.employee'
    name=fields.Char()
    leave_type=fields.Many2one('hr.leave.type')
    employees=fields.Many2many('hr.employee')

    def apply(self):
        for rec in self.employees:
            allocation = []
            for emp in rec._get_leaves():
                allocation.append(emp['al'])

            self.env['hr.leave.allocation'].create({
                'employee_id':rec.id,'holiday_type': 'employee','number_of_days_display':rec.remaining_leaves,'number_of_days':rec.remaining_leaves,
                'from_time_off_ids':[(6,0,allocation)],'holiday_status_id':self.leave_type.id,'name':self.name

            })


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        self._cr.execute("""
            SELECT
                h.id AS al 
            FROM
                (
                    SELECT holiday_status_id, id,
                        state, employee_id
                    FROM hr_leave_allocation
                ) h
                join hr_leave_type s ON (s.id=h.holiday_status_id)
            WHERE
                s.active = true AND h.state='validate' AND
                (s.allocation_type='fixed' OR s.allocation_type='fixed_allocation') AND
                h.employee_id in %s
            GROUP BY al""", (tuple(self.ids),))

        return self._cr.dictfetchall()

    def action_leave_time_out_to_next_year(self):
        view_id = self.env.ref('hr_leave_time_out.hr_leave_allocation_view_form_new_action_server').id
        print(self.browse(self.env.context['active_id'])._get_leaves())
        allocation=[]
        for rec in self.browse(self.env.context['active_id'])._get_leaves():
            allocation.append(rec['al'])

        return {
            'name': _('Leave Time Off To Next Year'),
            'res_model': 'hr.leave.allocation',
            'view_mode': 'form',
            'view_id': view_id,
            'context':{'default_from_time_off_ids':[(6,0,allocation)],'default_employee_id':self.env.context['active_id'], 'default_holiday_type': 'employee','default_number_of_days':self.browse(self.env.context['active_id']).remaining_leaves,'default_number_of_days_display':self.browse(self.env.context['active_id']).remaining_leaves},
            'target': 'new',
            'type': 'ir.actions.act_window',

        }


    def action_leave_time_out_to_next_year_all(self):
        view_id = self.env.ref('hr_leave_time_out.hr_leave_next_employee_wizard_form').id
        return {
            'name': _('Leave Time Off To Next Year'),
            'res_model': 'hr.leave.next.employee',
            'view_mode': 'form',
            'view_id': view_id,
            'context':{'default_employees':self.env.context['active_ids']},
            'target': 'new',
            'type': 'ir.actions.act_window',

        }


