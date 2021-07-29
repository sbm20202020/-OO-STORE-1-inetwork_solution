# -*- coding: utf-8 -*-
{
    'name': 'Employee Sequence Id Cron',
    'summary': 'Generate employee sequence id Cron',
    'version': '13.0.0.1.0',
    'author': 'Eman Ahmed',
    'depends': ['hr','jt_employee_sequence'],
    'data': [
        'views/emp_view.xml', 
    ],
    'application': False,
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
