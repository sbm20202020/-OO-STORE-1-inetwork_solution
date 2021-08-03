# -*- coding: utf-8 -*-

{
    'name': 'Employee Asset',
    'category': 'HR',
    'depends': ['base', 'hr', 'hr_contract'],
    'author': 'Doaa',
    'data': [
        'security/ir.model.access.csv',
        'views/hr_asset_view.xml',
        'views/hr_employee_view.xml'
    ],
    'auto_install': True,
}
