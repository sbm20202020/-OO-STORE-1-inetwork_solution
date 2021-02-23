# -*- coding: utf-8 -*-
{'name': "Employee Contract Allowances ",
 'summary': """
       Multiple Allowances for employee""",
 'description': """
            Add many allowances to any employee, include in payroll and END of Service Reward calculation
    """,
 'website': "https://ivalue-s.com",
 'email': "info@ivalue-s.com",
 'author': "I VALUE solutions",
 'license': "OPL-1",
 'category': 'HR',
 'version': '0.1',
 'images': ['static/description/Banner.png'],
 'depends': ['base', 'mail', 'hr_contract', 'hr_payroll'],
 'data': [
     'data/data.xml',
     'security/ir.model.access.csv',
     'views/hr_contract_views.xml',
 ],
 'wbs':'INV-20',
 'demo': []
 }
