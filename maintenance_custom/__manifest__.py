# -*- coding: utf-8 -*-
{
    'name': "Maintenance Workflow",
    'description': """
     Maintenance Workflow
    """,
    'author': "IT Systems Corportion Ebtsam Saad",
    'website': "http://www.it-syscorp.com",
    'depends': ['base', 'maintenance', 'stock', 'sale', 'sale_management', 'account'],
    'data': [
        'data/maintenance_data.xml',
        'wizard/wizard_inventory_receipt.xml',
        'views/shnider_service_request.xml',
        'views/standard_service_request.xml',


    ],

}
