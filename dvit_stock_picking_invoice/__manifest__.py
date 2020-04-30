# -*- coding: utf-8 -*-
{
    'name': "Stock picking invoice",
    'summary': 'Invoice stock pickings as it was in v.8.',
    'description': """
        Allow starting Purchase, Sales and refunds from the warehouse,
        And creating invoices on Warehouse pickings,
        same as it was in v8 .
    """,
    "license": "AGPL-3",
    'author': "dvit.me",
    'website': "https://dvit.me",
    'category': 'Stock',
    'version': '13.0.0.1',
    'depends': ['account','stock',],
    'wbs':'INS-16',
    'data': ['views/stock_picking.xml',],

}
