from odoo import fields, models, _, api, exceptions

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # remove this domain from standard

    # partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True,
    #                              domain="['|',('company_id', '=', False),('company_id', '=', company_id)]",
    #                              help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")



    partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True,
                                 domain="[('is_company', '=', True)]",
                                 help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")



