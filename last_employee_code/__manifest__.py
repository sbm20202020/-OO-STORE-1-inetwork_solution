# -*- encoding: utf-8 -*-
{
    'name': 'Last Employee Code',
    'category': 'HR',
    'description': """
     Last  Employee Code
    """,
    'summary': ' Last Employee Code',
    'author': "ITSYS ----> Marwa Ahmed",
    'website': "http://www.itsyscorp.com",
    'data': [
        'security/ir.model.access.csv',
        'views/hr_locations.xml',
        'views/department.xml',
        'views/hr_employee.xml',

    ],
    'depends': ['base', 'hr','hr_contract'],
    'installable': True,
    'application': True,
    'WBS': 'MM-9',

}
