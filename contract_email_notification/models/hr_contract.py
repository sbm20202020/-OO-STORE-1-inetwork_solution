from odoo import api, fields, models, _, SUPERUSER_ID
import re
import requests
import datetime
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo import http
from odoo.http import Controller, route, request
from dateutil import relativedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def contract_send_email_notification(self):
        ir_model_data = self.env['ir.model.data']
        template_res = self.env['mail.template']

        users = self.env['res.users'].search([])
        contracts = self.search([])
        contract_list = []
        for rec in contracts:
            if rec.date_end:
                lang = self.env.context.get('lang')
                dayes_number = rec.date_end - datetime.timedelta(days=60)
                if dayes_number == datetime.date.today():
                    contract_list.append(rec.name)
        for user in users:
            if contract_list and user.has_group(
                    'contract_email_notification.access_contract_notification_mail'):
                template_id = ir_model_data.get_object_reference('contract_email_notification',
                                                                 'end_date_contract_template')[1]
                template = template_res.browse(template_id)

                email_values = {
                    'email_to': user.email,
                    'email_from': user.company_id.email,
                    'subject': 'Contract End Date',
                }
                template.body_html = '<p>Dear ${(object.name)},''<br/><br/>Kindly be noted that this list of contracts ' + str(
                    contract_list) + ' it''s'' end date will be after 60 days. <br/>' \
                                     'Thanks,<br/>' \
                                     '${(object.company_id.name)}'

                template.send_mail(user.id, force_send=True, email_values=email_values)
