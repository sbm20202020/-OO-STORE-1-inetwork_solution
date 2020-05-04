# -*- coding: utf-8 -*-
{
    'name': "Sales Order Report",

    'summary': """
        sales_order_report """,

    'description': """
        sales_order_report
    """,

    'author': "ITsys-Corportion Doaa",
    'website': "http://www.it-syscorp.com",

    'category': 'Purchase',
    'version': '0.1',
    'wbs':'INS-10,INS-11',

    'depends': ['base','base_setup','sale','sale_stock'],

    'data': [
        'views/sale_order_template.xml',
        'views/sale_order_view.xml',


    ],
    'wbs':'INS-20',

}
