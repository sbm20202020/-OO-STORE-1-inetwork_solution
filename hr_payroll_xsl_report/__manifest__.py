# -*- coding: utf-8 -*-
{
    'name': "Hr Payroll xsl report ",

    'summary': """
       Hr Payroll xsl report""",

    'description': """
       Hr Payroll xsl report
    """,

    'author': "Marwa",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.13',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],

}
