# from odoo.addons.odoo_report_xlsx.report.report_xlsx import ReportXlsxAbstract
from odoo import models
import datetime

class BranchReasonProfitDataXls(models.AbstractModel):

    _name='report.hr_payroll_xsl_report.payroll_xsl_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook,data,lines):

        header2_format = workbook.add_format({
            'border': 5,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': '#27ae60'})
        header2_format.set_text_wrap()
        header2_format.set_font_size(12)

        header3_format = workbook.add_format({
            'border': 5,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            })
        header3_format.set_text_wrap()
        header3_format.set_font_size(10)

        header4_format = workbook.add_format({
            'border': 5,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': '#FFC300'})
        header4_format.set_text_wrap()
        header4_format.set_font_size(10)



        worksheet = workbook.add_worksheet()

        # worksheet.right_to_left()

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.set_column('I:I', 30)

        worksheet.set_row(0,40)

        worksheet.write('A1', 'File Date', header2_format)
        worksheet.write('B1', 'Value Date', header2_format)
        worksheet.write('C1', 'Narrative', header2_format)
        worksheet.write('D1', 'Currency', header2_format)
        worksheet.write('E1', 'Account Number', header2_format)
        worksheet.write('F1', 'Account Name', header2_format)
        worksheet.write('G1', 'Credit Amount', header2_format)


        row =1
        col = 0
        number = 1
        total_salary = 0.0
        for lin in lines:
            net_salary=0.0
            # for line in lin.line_ids:
            #     if line.category_id.code=='NET' or line.code=='NET':
            #         net_salary+=line.amount

            worksheet.set_row(row,30)
            worksheet.write(row, col, str(lin.date_from), header3_format)
            worksheet.write(row, col+1, str(lin.date_to), header3_format)
            worksheet.write(row, col + 2, 'Salary', header3_format)
            worksheet.write(row, col + 3, 'EGY', header3_format)
            worksheet.write(row, col + 4, lin.employee_id.visa_no, header3_format)
            worksheet.write(row, col + 5, lin.employee_id.name, header3_format)
            worksheet.write(row, col + 6, lin.net_wage, header4_format)
            total_salary += lin.net_wage

            number += 1
            row += 1
        worksheet.write(row, col + 6, total_salary , header4_format)

        return



