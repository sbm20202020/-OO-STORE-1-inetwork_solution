# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Payslip Pdf Report',
    'version': '13.0',
    'author': "Marwa Ahmed",
    'depends': ['base','hr','hr_payroll','last_employee_code' ],
    'data': [
             'report/reports.xml',
        'views/hr_payslip.xml',
        'views/payslip_template.xml',

             ],
    'installable': True,
    'application': True,
}
