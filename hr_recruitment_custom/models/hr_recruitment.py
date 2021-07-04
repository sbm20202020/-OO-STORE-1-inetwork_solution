# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError



class HrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'
    send_email=fields.Boolean()


class HrRecruitment(models.Model):
    _inherit = 'hr.applicant'
    stage_send_email=fields.Boolean(related="stage_id.send_email",store=True)
    is_send=fields.Boolean(copy=False)

    def send_offer(self):
        template = self.env.ref('hr_recruitment_custom.send_offer_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email_from|safe}',
            'email_cc': '${object.email_cc|safe}',
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for rec in self:
            if not rec.email_from:
                raise UserError(_("Cannot send email: Application %s has no email address.") % rec.name)
            with self.env.cr.savepoint():
                force_send = not(self.env.context.get('import_file', False))
                template.with_context(lang=self.env.user.lang).send_mail(rec.id, force_send=force_send, raise_exception=True)
            _logger.info("Job Offer email sent  to <%s>",rec.email_from)
            rec.is_send=True



    signature_hr = fields.Binary(string='Signature', help="Field for adding the signature of HR operation Manager ",copy=False)
    signature_ceo = fields.Binary(string='Signature', help="Field for adding the signature of CEO",copy=False)
    signature_name_hr=fields.Char(copy=False)
    signature_date_hr=fields.Date(copy=False)
    signature_name_ceo=fields.Char(copy=False)
    signature_date_ceo=fields.Date(copy=False)
    @api.onchange('signature_hr','signature_ceo')
    def _compute_check_signature_date(self):
        if self.signature_hr :
            self.signature_date_hr =datetime.now().date()
        if self.signature_ceo :
            self.signature_date_ceo =datetime.now().date()






