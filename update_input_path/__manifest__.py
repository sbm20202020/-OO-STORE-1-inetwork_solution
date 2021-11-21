# -*- coding: utf-8 -*-
{
    'name': "Update Input Path",

    'description': """
        Update Input Path
    """,

    'author': "ITsys-Eman Ahmed",
    'website': "http://www.it-syscorp.com",
    'version': '13.0.1',
    'wbs':'MM-1',

    'depends': ['base','hr_payroll','hr_work_entry','portal', 'utm','last_employee_code'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_work_entry_type_view.xml',
        'views/update_input_path_view.xml',
        'views/employee_work_view.xml',
        'wizard/update_input_path_wizard_view.xml',
    ],

}
