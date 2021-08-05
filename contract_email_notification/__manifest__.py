# -*- encoding: utf-8 -*-
{
    'name': 'Contract Email Notification',
    'version': '1.0',
    'category': 'HR',
    'description': """
     Contract Email Notification
    """,
    'summary': 'Contract Email Notification',
    'author': "ITSYS Doaa khaled",
    'website': "http://www.itsyscorp.com",
    'images': ['static/description/icon.png'],
    'data': [
        'security/security.xml',
        'views/cron.xml',
        'views/email_data.xml',
    ],
    'depends': ['base', 'hr', 'hr_contract'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 106,
}
