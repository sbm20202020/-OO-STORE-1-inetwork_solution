# -*- encoding: utf-8 -*-
{
    "name": "Hr leave time out",
    "version": "13",
    'author': "Eman Ahmed",
    "category": "HR",
    'depends': ['base', 'hr','hr_payroll','hr_holidays'],
    "data": [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/hr_leave_next_employee.xml'

    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
