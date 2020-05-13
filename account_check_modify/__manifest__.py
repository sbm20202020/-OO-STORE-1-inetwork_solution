# -*- encoding: utf-8 -*-

{
    "name": "Inetwork Checks Modify",
    "version": "1",
    "author": "IT-SYS Corporation --> Marwa Osama",
    "category": " ",
    'website': 'www.it-syscorp.com',
    'depends': ['base','account_accountant','itsys_account_check'],
    "summary": " ",

    'description': """
    • 
    """,

    "data": [
        'security/checks_security.xml',
        'security/ir.model.access.csv',
        'views/checks_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
    'price': 1,
    'currency': 'EUR',
    'images': ['images/main_screenshot.png'],
    'license': 'AGPL-3',

}
