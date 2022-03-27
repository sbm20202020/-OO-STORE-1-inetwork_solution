# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
from odoo.http import request
from odoo import api, fields, models, _
from io import BytesIO
from calendar import monthrange
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat

class TimesheetReport(models.AbstractModel):
    _name = 'report.salary_timesheet_report.timesheet_report_excel'
    _inherit = 'report.report_xlsx.abstract'

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
        worksheet.set_row(0, 80)
        worksheet.set_row(1, 20)
        worksheet.set_row(2, 20)

        worksheet.merge_range('A1:E1','Attendance Sheets', header_title_format)

        col = 0
        row = 2
        for line in wizard_record:
            worksheet.write('A'+str(row), 'Employee', header2_format)
            worksheet.write('B'+str(row),line.employee_id.name, header3_format)
            worksheet.write('C'+str(row), 'Period', header2_format)
            worksheet.write('D'+str(row),datetime.strptime(str(line.date_from), DEFAULT_SERVER_DATE_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT), header3_format)
            worksheet.write('E'+str(row),datetime.strptime(str(line.date_to), DEFAULT_SERVER_DATE_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT), header3_format)
            worksheet.merge_range('A'+str(row+1)+':B'+str(row+1), 'Over Time', header2_format)
            worksheet.write('A'+str(row+2), 'No of overtimes', header3_format)
            worksheet.write('B'+str(row+2),line.no_overtime, header3_format)
            worksheet.write('A'+str(row+3), 'Total Over Time', header3_format)
            worksheet.write('B'+str(row+3),line.tot_overtime, header3_format)
            worksheet.merge_range('C'+str(row+1)+':D'+str(row+1), 'Late In', header2_format)
            worksheet.write('C'+str(row+2), 'No of Lates', header3_format)
            worksheet.write('D'+str(row+2),line.no_late, header3_format)
            worksheet.write('C'+str(row+3), 'Total Late In', header3_format)
            worksheet.write('D'+str(row+3),line.tot_late, header3_format)
            worksheet.merge_range('A'+str(row+4)+':B'+str(row+4), 'Absence', header2_format)
            worksheet.write('A'+str(row+5), 'No of Absence Days', header3_format)
            worksheet.write('B'+str(row+5),line.no_absence, header3_format)
            worksheet.write('A'+str(row+6), 'Total absence Hours', header3_format)
            worksheet.write('B'+str(row+6),line.tot_absence, header3_format)
            worksheet.merge_range('C'+str(row+4)+':D'+str(row+4), 'Diffrenece Time', header2_format)
            worksheet.write('C' + str(row +5), 'No of Diff Times', header3_format)
            worksheet.write('D' + str(row +5),line.no_difftime, header3_format)
            worksheet.write('C' + str(row +6), 'Total Diff time Hours', header3_format)
            worksheet.write('D' + str(row +6),line.tot_difftime, header3_format)
            row += 9

        return
