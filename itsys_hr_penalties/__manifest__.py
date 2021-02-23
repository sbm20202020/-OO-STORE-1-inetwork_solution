# -*- coding: utf-8 -*-
{
    'name': " Hr Penalties",

    'author': "Marwa Ahmed & Eman Ahmed",
    'website': "http://www.it-syscorp.com",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','hr','hr_payroll'],

    # always loaded
    'data': [
        'sequences/penalties_sequence.xml',
        'security/ir.model.access.csv',
        'security/penalties_security.xml',
        'views/views.xml',
        'views/salary_rule.xml',
        'views/penalty_details.xml',



    ],

}