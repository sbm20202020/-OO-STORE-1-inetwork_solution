# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
from odoo.http import request
from odoo import api, fields, models, _
from io import BytesIO
from calendar import monthrange
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.tools.misc import format_date


class SalaryReport(models.AbstractModel):
    _name = 'report.salary_timesheet_report.salary_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def number_of_days_in_month(self, year, month):
        return monthrange(year, month)[1]

    def generate_xlsx_report(self, workbook, data, lines):
        wizard_record = lines
        header_title_format = workbook.add_format({
            'border': 2,
            'border_color': 'black',
            'align': 'center',
            'font_color': '#0b034d;',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': 'white'})
        header_title_format.set_text_wrap()
        header_title_format.set_font_size(18)
        header_title_format1 = workbook.add_format({
            'border': 2,
            'border_color': 'black',
            'align': 'center',
            'font_color': '#0b034d;',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': 'white'})
        header_title_format1.set_text_wrap()
        header_title_format1.set_font_size(25)

        header2_format = workbook.add_format({
            'border': 2,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'white',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': 'gray'})
        header2_format.set_text_wrap()
        header2_format.set_font_size(12)

        header3_format = workbook.add_format({
            'border': 2,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': False,
            'valign': 'vcenter',
            'fg_color': '#FFFFFF'})
        header3_format.set_text_wrap()
        header3_format.set_font_size(12)
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_row(0, 80)
        worksheet.set_row(1, 20)
        worksheet.set_row(2, 20)
        row = 2
        rules=[]
        for line in wizard_record:
            worksheet.merge_range('A1:H1',
                                  'Salary Slip - ' + str(format_date(self.env, line.date_from, date_format="MMMM y")),
                                  header_title_format)

            for rule in line.line_ids.filtered(lambda l: l.can_print == True).sorted(lambda l : l.salary_rule_id.id):
                rules.append(rule.salary_rule_id)
        col = 0
        worksheet.write('A'+str(row), 'Name', header2_format)
        for rec in set(rules):
            worksheet.write(row-1, col+1,rec.name, header2_format)
            col += 1


        for line in wizard_record:
            col = 0
            worksheet.write('A'+str(row+1),line.employee_id.name, header3_format)
            for rec in set(rules):
                worksheet.write(row, col + 1, '', header3_format)
                for payslip_line in line.line_ids.filtered(lambda l:l.can_print == True).sorted(lambda l : l.salary_rule_id.id ):
                    if payslip_line.salary_rule_id == rec:
                        worksheet.write(row, col+1, payslip_line.total or '', header3_format)

                col += 1
            row += 1



        return
