# -*- coding: utf-8 -*-
# related to task INV-38 to fix Loan Management not calculated correctly
{
    'name': "Request Loan",

    'author': "Marwa Ahmed",
    'website': "http://www.it-syscorp.com",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','ohrms_loan','hr_contract'],

    # always loaded
    'data': [

        'views/views.xml',
        'views/salary_rule.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'wbs':'INV-15,INV-30'
}