# -*- coding: utf-8 -*-
{
    'name': "invoice_reports",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose""",

    'description': """
        Long description of module's purpose
    """,

    'author': 'ITSYS CORPORATION - Marwa Osama',

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/company_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}