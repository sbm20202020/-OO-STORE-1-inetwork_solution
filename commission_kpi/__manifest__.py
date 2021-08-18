# -*- coding: utf-8 -*-
{
    'name': 'Commission KPI Report',
    'version': '13.0.1.0.0',
    'summary': """Commission KPI Report""",
    'description': """Commission KPI Report""",
    'author': "Eman Ahmed",
    'company': 'IT-SYS',
    'category': 'Accounting',
    'depends': ['base', 'account', 'mail', 'percent_field', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/report.xml',
        'data/kpi_data.xml',
        'views/kpi_quarter_view.xml',
        'views/res_users_views.xml',
        'wizard/kpi_wizard_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
