# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'hr modification',
    'description': """
hr management
=================


    """,
    'category': 'hr',
    'sequence': 32,
    'depends': ['hr','rm_hr_attendance_sheet'],
    'data': ['security/ir.model.access.csv','views/view.xml','wizards/attendance_wizard.xml'

    ],
    'demo': [

    ],
    'qweb': [

    ],
    'license': 'OEEL-1',
    'auto_install': True,
}
