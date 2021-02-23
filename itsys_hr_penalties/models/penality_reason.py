from odoo import fields,models,api

class PenalityReason(models.Model):

    _name = 'penalty.reason'
    _rec_name = 'reason_name'

    seq = fields.Char(string="Name", readonly=True)

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('hr.penality.reason') or '/'
        values['seq'] = seq
        res=super(PenalityReason, self).create(values)
        return res

    reason_name = fields.Text('Reason')

class HrDepartment(models.Model):

    _inherit = 'hr.department'





