# -*- coding: utf-8 -*-
{
    'name': "Maintenance Reports ",

    'summary': """
    Maintenance Reports
      """,
    'author': "IT Systems Corportion Marwa Ahmed",
    'website': "http://www.it-syscorp.com",
    'depends': ['base', 'maintenance', 'stock','ctx_equipment_stock_product','report_xlsx','maintenance_custom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'reports/reports.xml',
        'reports/header_footer.xml',
        'reports/sp_product.xml',
        'reports/visit_report.xml',
        'views/maintenance_view.xml',
        'wizard/single_phase_report.xml',
        'wizard/single_phase_wiz.xml',
        'reports/mr_report.xml',
    ],

}
