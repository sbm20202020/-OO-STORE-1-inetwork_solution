# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Checks',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 10,
    'author': 'ITSYS CORPORATION',
    'summary': '',
    'description': "Payment through checks",
    'website': 'https://www.it-syscorp.com',
    'depends': ['account_accountant'],
    'data': [
        'security/account_check_security.xml',
        'security/ir.model.access.csv',
        'wizard/hash_to_supplier_view.xml',
        'account_check_view.xml',
        # 'account_check_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
