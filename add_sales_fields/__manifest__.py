# -*- coding: utf-8 -*-
{
    'name': "Sales Order New Fields",

    'summary': """
         """,

    'description': """

    """,

    'author': "ITsys-Corportion ----> Marwa Ahmed",
    'website': "http://www.it-syscorp.com",

    'category': 'sales',
    'version': '0.1',
    'wbs':'INS-30',

    'depends': ['base','stock','sale',],

    'data': [
        'security/ir.model.access.csv',
        'views/availability.xml',
        'views/views.xml',


    ],


}
