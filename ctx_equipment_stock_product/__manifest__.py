# -*- coding: utf-8 -*-
{
    'name': "Equipment Stock Product",

    'summary': """
        This module allow you to link equipment to stock product, and create equipment either from shipments or inventory adjustements.""",

    'description': """
This module allow you to link equipment to stock product, and create equipment either from shipments or inventory adjustements.
Equipment product
Link equipment to stock
Link equipment to product
Odoo Equipment
Odoo Equipment Product
Odoo Link Equipment to Product
Create Equipment from product
    """,

    'author': "CorTex IT Solutions Ltd.",
    'website': "https://cortexsolutions.net",
    'category': 'Employees',
    'version': '1.0.0',
    'depends': ['hr_maintenance','maintenance','stock','product'],
     'license': 'OPL-1',
    'currency': 'EUR',
    'price': 70,

    # always loaded
    'data': [
        'views/product_template_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_inventory_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_production_lot_views.xml',

    ],
    "application": False,
    "installable": True,
    "post_init_hook": "post_init_hook",
    'images': ['static/description/main_screenshot.png'],
}
