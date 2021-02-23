# -*- encoding: utf-8 -*-

{
    "name": "Stop Quick Create",
    "version": "1",
    "author": "IT-SYS Corporation --> Marwa Ahmed",
    "category": "",
    'website': 'www.it-syscorp.com',
    'depends': ['base','sale','purchase','account',
                'crm','project','sales_delivery_planning','purchase_request'],

    "wbs":"inv-48",
    "data": [
           'security/security.xml',
             'views/views.xml',

    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,


}
