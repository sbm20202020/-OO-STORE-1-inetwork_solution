# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Salary & Timesheet Report',
    'version': '13.0.0.0',
    'category': 'payroll',
    'summary': 'Salary & Timesheet Report',
    "description": """
            Salary & Timesheet Report
           """,
    'author': "IT-SYS Eman Ahmed",
    'depends': ['base','report_xlsx','hr_payroll','rm_hr_attendance_sheet','hr_payroll'],
    'data': [
        'views/hr_payslip_views.xml',
        'report/report.xml',
    ],

    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

