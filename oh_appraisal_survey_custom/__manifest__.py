# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'OH Appraisal Survey Custom',
    'version': '3.0',
    'category': 'Marketing/Survey',
    'description': """
Create special beautiful surveys and visualize answers
==============================================

It depends on the answers or reviews of some questions by different users. A
survey may have multiple pages. Each page may contain multiple questions and
each question may have multiple answers. Different users may give different
answers of question and according to that survey is done. Partners are also
sent mails with personal token for the invitation of the survey.
    """,
    'summary': 'Create special surveys and analyze answers',
    'author': "ITsys-Corportion ----> Eman Ahmed",
    'website': "http://www.it-syscorp.com",
    'depends': [
        'base','survey','report_xlsx'],
    'data': [
        'views/survey_question_views.xml',
        'views/survey_templates.xml',
        'data/survey_data.xml',
        'report/report.xml',
        # 'report/print_answer.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
