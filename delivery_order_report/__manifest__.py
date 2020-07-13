# -*- coding: utf-8 -*-
{
    'name': "Delivery Order Report",

    'summary': """
        Delivery Order Report """,

    'description': """
        Delivery Order Report
    """,

    'author': "ITsys-Corportion Doaa",
    'website': "http://www.it-syscorp.com",

    'category': 'Purchase',
    'version': '0.1',
    'wbs':'INS-10,INS-11',

    'depends': ['base','base_setup','stock','sale','purchase_sale_order_report'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/delivery_order_view.xml',
        'views/delivery_order_template.xml',
        # 'views/cst_po_number.xml',


    ],
    'wbs':'INS-12',

}
