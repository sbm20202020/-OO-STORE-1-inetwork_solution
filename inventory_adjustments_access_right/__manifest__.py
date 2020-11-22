# -*- encoding: utf-8 -*-

{
    "name": "Inventory Adjustments Access Right",
    "version": "13",
    "author": "IT-SYS Corporation --> Doaa",
    "category": "Inventory",
    'website': 'www.it-syscorp.com',
    'depends': ['base','stock'],
    "data": [

            'security/security.xml',
            'views/stock_inventory.xml',
            'views/activity_schedule.xml',
            'wizard/missing_item_wizard_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,


}
