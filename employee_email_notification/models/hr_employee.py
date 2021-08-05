from odoo import api, fields, models, _, SUPERUSER_ID
import datetime

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    need_employee_contract = fields.Boolean(compute="_compute_need_employee_contract", store=True,
                                            string='Need Employee Contract', copy=False)
    need_Form1_Social_insurance = fields.Boolean(compute="_compute_need_employee_contract", store=True,
                                                 string='Need Form1_Social_insurance', copy=False)
    need_Form6 = fields.Boolean(compute="_compute_need_employee_contract", store=True,
                                string='Need Form6', copy=False)

    need_medical_card = fields.Boolean(compute="_compute_need_employee_contract", store=True,
                                       string='Need medical_card', copy=False)
    need_card_id = fields.Boolean(compute="_compute_need_employee_contract", store=True,
                                  string='Need card_id', copy=False)
    need_military_certificate = fields.Boolean(compute="_compute_need_employee_contract", store=True,
                                               string='Need military_certificate', copy=False)
    need_driver_license = fields.Boolean(compute="_compute_need_employee_contract", store=True,
                                         string='Need driver_license', copy=False)

    @api.depends('employee_contract', 'Form1_Social_insurance', 'Form6', 'medical_card', 'card_id',
                 'military_certificate', 'driver_license')
    def _compute_need_employee_contract(self):
        for employee in self:
            if employee.employee_contract:
                employee.need_employee_contract = False
            else:
                employee.need_employee_contract = True
            if employee.Form1_Social_insurance:
                employee.need_Form1_Social_insurance = False
            else:
                employee.need_Form1_Social_insurance = True
            if employee.Form6:
                employee.need_Form6 = False
            else:
                employee.need_Form6 = True

            if employee.medical_card:
                employee.need_medical_card = False
            else:
                employee.need_medical_card = True
            if employee.card_id:
                employee.need_card_id = False
            else:
                employee.need_card_id = True
            if employee.driver_license:
                employee.need_driver_license = False
            else:
                employee.need_driver_license = True
            if employee.military_certificate:
                employee.need_military_certificate = False
            else:
                employee.need_military_certificate = True
        return

    def employee_send_email_notification(self):
        ir_model_data = self.env['ir.model.data']
        template_res = self.env['mail.template']
        employee_with_details = self.search([])
        users = self.env['res.users'].search([])
        employee_list_15 = []
        employee_list_30 = []
        employee_list_60 = []
        for emp in employee_with_details:
            for contract in emp.contract_ids:
                dayes_number = datetime.date.today() - contract.date_start
                if dayes_number.days >= 15:
                    if emp.need_employee_contract == True or not emp.mobile_phone or not emp.phone:
                        employee_list_15.append(emp.name)
                if dayes_number.days >= 30:
                    if emp.need_Form1_Social_insurance == True or emp.need_Form6 == True or emp.need_medical_card == True or not emp.bank_account_id:
                        employee_list_30.append(emp.name)
                if dayes_number.days >= 60:
                    if emp.need_card_id == True or emp.need_driver_license == True or emp.need_military_certificate == True:
                        employee_list_60.append(emp.name)
        for user in users:
            if employee_list_15 and user.has_group(
                    'employee_email_notification.access_delay_employee_notification_mail_15'):
                template_id = ir_model_data.get_object_reference('employee_email_notification',
                                                                 'medical_email_15_template')[1]
                template = template_res.browse(template_id)

                email_values = {
                    'email_to': user.email,
                    'email_from': user.company_id.email,
                    'subject': 'Delay in attach Employee Contract or set Work mobile or Phone for 15 days',
                }
                template.body_html = '<p>Dear ${(object.name)},''<br/><br/>Kindly be noted that this list of employees ' + str(
                    employee_list_15) + ' has a delay in attach Employee Contract or set Work mobile or Phone for 15 days from the contract start date. <br/>' \
                                        'Thanks,<br/>' \
                                        '${(object.company_id.name)}'

                template.send_mail(user.id, force_send=True, email_values=email_values)
            if employee_list_30 and user.has_group(
                    'employee_email_notification.access_delay_employee_notification_mail_30'):
                template_id = ir_model_data.get_object_reference('employee_email_notification',
                                                                 'medical_email_30_template')[1]
                template = template_res.browse(template_id)

                email_values = {
                    'email_to': user.email,
                    'email_from': user.company_id.email,
                    'subject': 'Delay in attach Form 1 Social insurance or Form 6 or Medical Card or set Bank Account Number for 30 days',
                }
                template.body_html = '<p>Dear ${(object.name)},''<br/><br/>Kindly be noted that this list of employees ' + str(
                    employee_list_30) + ' has a delay in attach Form 1 Social insurance or Form 6 or Medical Card or set Bank Account Number for 30 days from the contract start date. <br/>' \
                                        'Thanks,<br/>' \
                                        '${(object.company_id.name)}'

                template.send_mail(user.id, force_send=True, email_values=email_values)
            if employee_list_60 and user.has_group(
                    'employee_email_notification.access_delay_employee_notification_mail_60'):
                template_id = ir_model_data.get_object_reference('employee_email_notification',
                                                                 'medical_email_60_template')[1]
                template = template_res.browse(template_id)

                email_values = {
                    'email_to': user.email,
                    'email_from': user.company_id.email,
                    'subject': 'Delay in attach ID or Military Certificate or Driver License for 60 days',
                }
                template.body_html = '<p>Dear ${(object.name)},''<br/><br/>Kindly be noted that this list of employees ' + str(
                    employee_list_60) + ' has a delay in attach ID or Military Certificate or Driver License for 60 days from the contract start date. <br/>' \
                                        'Thanks,<br/>' \
                                        '${(object.company_id.name)}'

                template.send_mail(user.id, force_send=True, email_values=email_values)
