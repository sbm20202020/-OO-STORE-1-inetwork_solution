from odoo import fields, models, api



class HrDeparture(models.Model):
    _name = 'hr.departure'
    _rec_name = 'name'

    name = fields.Char(required=True)


class Employee(models.Model):

        _inherit = 'hr.employee'
        archive_reason=fields.Char(track_visibility='onchange')

        departure_reason_id=fields.Many2one("hr.departure",string='Archiving Reason',track_visibility='onchange')





class Employeepublic(models.Model):

        _inherit = 'hr.employee.public'


class HrDepartureWizard(models.TransientModel):
        _inherit = 'hr.departure.wizard'

 # remove default from departure_reason field in standard and invisible field and replace it new many2one field with the same name

        departure_reason = fields.Selection([
                ('fired', 'Fired'),
                ('resigned', 'Resigned'),
                ('retired', 'Retired')
        ], string="Departure Reason", default=False)

        archive_reason=fields.Char()
        departure_reason_id=fields.Many2one("hr.departure",string='Archiving Reason')

        def action_register_departure(self):
                employee = self.employee_id
                employee.archive_reason = self.archive_reason
                employee.departure_reason = self.departure_reason
                employee.departure_reason_id = self.departure_reason_id.id

                employee.departure_description = self.departure_description

                if not employee.user_id.partner_id:
                        return

                for activity_type in self.plan_id.plan_activity_type_ids:
                        self.env['mail.activity'].create({
                                'res_id': employee.user_id.partner_id.id,
                                'res_model_id': self.env['ir.model']._get('res.partner').id,
                                'activity_type_id': activity_type.activity_type_id.id,
                                'summary': activity_type.summary,
                                'user_id': activity_type.get_responsible_id(employee).id,
                        })
