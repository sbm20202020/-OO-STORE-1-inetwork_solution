# -*- encoding: utf-8 -*-
{
    'name': 'Hr Recruitment Custom',
    'version': '3.0',
    'category': 'hr',
    'description': """
      Hr Recruitment Custom
    """,
    'summary': 'Hr Recruitment Custom',
    'author': "ITsys-Corportion ----> Eman Ahmed",
    'website': "http://www.it-syscorp.com",
    'depends': [
        'base','hr_recruitment','web','hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/header_footer.xml',
        'views/hr_recruitment_views.xml',
        'views/mail_template_offer.xml',
        'views/hr_employee_views.xml',
        'views/res_country_view.xml',
        'views/cron_job_and_schedule.xml',
        'views/employee_report.xml',


    ],
    'demo': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
