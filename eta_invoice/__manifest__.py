# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'ETA Invoice',
    'version' : '1.0',
    'summary': 'Invoices & Payments',
    'sequence': 10,
    'description': "",
    'category': 'Accounting/Accounting',
    'depends': ['account'],
    'author': 'Capitol Tech',
    'website': '',
    'installable': True,
    'application': True,
    'auto_install': True,
    'data':[
        'security/security.xml',
        'data/data.xml',
        'views/eta_button.xml',
        'views/account_tax.xml',
        'views/product_product.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/uom_uom.xml',
    ]

}
