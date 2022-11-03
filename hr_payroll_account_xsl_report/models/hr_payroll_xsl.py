# from odoo.addons.odoo_report_xlsx.report.report_xlsx import ReportXlsxAbstract
from odoo import models
import datetime

class BranchReasonProfitDataXls(models.AbstractModel):

    _name='report.hr_payroll_account_xsl_report.payroll_xsl_bank_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook,data,lines):
        header1_format = workbook.add_format({
            'border': 5,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': '#000000'})
        header1_format.set_text_wrap()
        header1_format.set_font_size(12)

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

        header6_format = workbook.add_format({
            'border': 0,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'white',
            'bold': True,
            'valign': 'vcenter',
        })
        header3_format.set_text_wrap()
        header3_format.set_font_size(10)



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


        total_salary = 0.0

        worksheet.write('A1', 'Currency', header2_format)
        worksheet.write('B1', 'Creditor BIC Code', header2_format)
        worksheet.write('C1', 'Account Number', header2_format)
        worksheet.write('D1', 'Account Name', header2_format)
        worksheet.write('E1', 'Debit Amount', header2_format)
        worksheet.write('F1','Credit Amount' , header2_format)



        row = 2
        col = 0
        number = 0

        for lin in lines:
            net_salary=0.0
            # for line in lin.line_ids:
            #     if line.category_id.code=='NET' or line.code=='NET':
            #         net_salary+=line.amount

            worksheet.set_row(row,30)
            worksheet.write(row, col, ' ', header6_format)
            worksheet.write(row, col+1, 'CIBEEGCXXXX ', header3_format)
            worksheet.write(row, col + 2, lin.employee_id.visa_no, header3_format)
            worksheet.write(row, col + 3, lin.employee_id.name, header3_format)
            worksheet.write(row, col + 4, ' ', header1_format)
            worksheet.write(row, col + 5, lin.net_wage, header4_format)
            total_salary += lin.net_wage

            number += 1
            row += 1
        worksheet.write(row, col + 3, number, header4_format)

        worksheet.write(row, col + 4, total_salary , header3_format)
        worksheet.write(row, col + 5, total_salary, header3_format)





        worksheet.write('A2', 'egp', header3_format)
        worksheet.write('B2', ' ', header1_format)
        worksheet.write('C2', '100037516273', header3_format)
        worksheet.write('D2', 'iNetwork Solutions', header3_format)
        worksheet.write('E2', total_salary, header3_format)
        worksheet.write('F2', ' ', header1_format)



        return



