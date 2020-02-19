# -*- coding: utf-8 -*-
{
    'name': "Purchase And Sale Order Report",

    'summary': """
        Purchase And Sale Order Report """,

    'description': """
        Purchase And Sale Order Report
    """,

    'author': "ITsys-Corportion Eman Ahmed",
    'website': "http://www.it-syscorp.com",

    'category': 'Purchase',
    'version': '0.1',
    'wbs':'INS-10,INS-11',

    'depends': ['base','sale','purchase','invoice_reports'],

    'data': [
        'views/sale_report_template.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/purchase_report_template.xml'


    ],

}