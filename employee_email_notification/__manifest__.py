# -*- encoding: utf-8 -*-
{
    'name': 'Employee Email Notification',
    'version': '1.0',
    'category': 'HR',
    'description': """
     Employee Email Notification
    """,
    'summary': 'Employee Email Notification',
    'author': "ITSYS Doaa khaled",
    'website': "http://www.itsyscorp.com",
    'images': ['static/description/icon.png'],
    'data': [
        'security/security.xml',
        'views/hr_employee_view.xml',
        'views/cron.xml',
        'views/email_data.xml',
    ],
    'depends': ['base', 'hr', 'hr_contract', 'hr_recruitment_custom'],
    'installable': True,
    'auto_install': False,
    'application': True,

}
