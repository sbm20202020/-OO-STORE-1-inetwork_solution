# -*- coding: utf-8 -*-
{
    'name': "Hr Payroll account xsl report ",

    'summary': """
       Hr Payroll xsl  account report""",

    'author': "Marwa",
    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx','hr','hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],

}
