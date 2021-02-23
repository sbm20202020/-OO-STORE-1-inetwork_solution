# -*- encoding: utf-8 -*-

{
    "name": " Hr Employee Access right",
    "version": "12",
    "author": "IT-SYS Corporation --> Marwa Ahmed",
    "category": "",
    'website': 'www.it-syscorp.com',
    'depends': ['base','hr','crm'],

    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
             'security/crm_lead.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,


}
