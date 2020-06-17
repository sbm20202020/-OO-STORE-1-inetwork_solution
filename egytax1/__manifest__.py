# -*- coding: utf-8 -*-
{
    # related to task INS-23
    'name': "eggtax",

   'author': "Eng.Mohamed Mostafa Kamel at IT-Sys Corp",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','hr_contract','hr',
                'hr_holidays',
                'hr_payroll'],


    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr_contract.xml',
        'demo/cron.xml',
        'demo/hr_payroll_data.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}