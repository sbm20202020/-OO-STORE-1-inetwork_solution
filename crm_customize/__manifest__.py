# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'CRM Customize',
    'version': '1.1',
    'author': 'Itsys : Mostafa Abbas',
    'Upgraded to 13': 'Itsys : Doaa',
    'summary': 'Send Invoices and Track Payments',
    'sequence': 30,
    'description': """
Core mechanisms for the accounting modules. To display the menuitems, install the module account_invoicing.
    """,
    'category': 'CRM',
    'website': 'https://www.odoo.com/',
    'depends': ['base', 'crm', 'account', 'stock', 'sale', 'sale_stock', 'sale_crm'],
    'data': [
        'views/crm_lead_view.xml',
        'views/stock_picking_view.xml',
        'views/sale_order_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
