# -*- encoding: utf-8 -*-
from odoo.http import request
from odoo import api, fields, models, _
from  datetime import timedelta
import datetime
import base64
import io


class PheReportDataXls(models.AbstractModel):
    _name = 'report.maintenance_reports.phase_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        wizard_record = request.env['single.phase.wizard'].search([])[-1]

        header_format = workbook.add_format({
            'border': 0,
            'align': 'right',

        })
        header_format.set_text_wrap()
        header1_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
        })

        header1_format.set_font_size(12)


        header3_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': '#FFFFFF'})
        header3_format.set_text_wrap()
        header3_format.set_font_size(15)
        header4_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': '#FFFFFF'})
        header4_format.set_text_wrap()
        header4_format.set_font_size(12)

        t1 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'border_color': 'black',
            'fg_color': '#C0C0C0',
            'font_color': 'black',
            'valign': 'vcenter',
        })
        t1.set_text_wrap()
        t2 = workbook.add_format({
            'border': 2,
            'align': 'center',
            'font_color': 'black',
            'valign': 'vcenter',
        })
        t2.set_text_wrap()

        t3= workbook.add_format({
            'border': 2,
            'align': 'center',
            'border_color': 'black',
            'fg_color': '#C0C0C0',
            'font_color': 'black',
            'valign': 'vcenter',
        })
        t3.set_text_wrap()
        t3.set_font_size(12)

        worksheet = workbook.add_worksheet()

        # worksheet.right_to_left()
        worksheet.set_column('A:A',15)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('G:G',30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('H:H', 25)

        worksheet.set_row(0, 10)
        worksheet.set_row(1, 30)
        worksheet.set_row(2, 30)
        worksheet.set_row(3, 30)
        worksheet.set_row(4, 30)
        worksheet.set_row(5, 30)
        worksheet.set_row(6, 30)
        worksheet.set_row(7, 30)
        worksheet.set_row(8, 30)
        date_from = wizard_record.date_from
        date_to = wizard_record.date_to
        type = wizard_record.type

        worksheet.merge_range(
            'A2:F2', 'Single Phase SERVICE ACTIVITY ',header3_format )
        worksheet.merge_range(
            'A4:B4',str('Submission Date :'), header4_format)
        worksheet.merge_range('A5:B5', str('Service Partner : '), header4_format)
        worksheet.merge_range(
            'A6:B6', str('Activity From :  '), header4_format)
        worksheet.merge_range(
            'A7:B7', str('Activity To : '), header4_format)

        worksheet.write('C4',str(fields.date.today()) , t2)
        worksheet.write('C5','Inetwork Solutions ', t2)
        worksheet.write('C6', str(date_from), t2)
        worksheet.write('C7', str(date_to), t2)

        row = 9
        col = 0
        if date_from and date_to and type:

            maintenance_obj = self.env['maintenance.request'].search([('request_date','>=',date_from),('request_date','<=',date_to),('type', '=', type)])
            worksheet.write('A9', 'Sr. No.', t1)
            worksheet.write('B9', 'Date Approved', t1)
            worksheet.write('C9', 'Client Name',t1)
            worksheet.write('D9', 'UPS', t1)
            worksheet.write('E9', 'UPS Serial Number', t1)
            worksheet.write('F9', 'Service', t1)
            worksheet.write('G9', 'Month ', t1)
            worksheet.write('H9', 'Initial Amount ', t1)


            number = 0
            for rec in maintenance_obj:
                number = number +1
                worksheet.write(row, col, number, header4_format)
                print("reccccccccccccccccccc", rec.partner_id.name)

                if rec.request_date:

                    worksheet.write(row, col + 1, str(rec.request_date),header4_format)
                else:
                    worksheet.write(row, col + 1, str(' '), header4_format)
                if rec.partner_id:
                    worksheet.write(row, col + 2, str(rec.partner_id.name), header4_format)
                else:
                    worksheet.write(row, col + 2, ' ', header4_format)
                if rec.equipment_id:
                    worksheet.write(row, col + 3, rec.equipment_id.product_id.name, header4_format)
                else:
                    worksheet.write(row, col + 3, ' ', header4_format)
                if rec.equipment_id:
                    worksheet.write(row, col + 4, rec.equipment_id.lot_id.name, header4_format)
                else:
                    worksheet.write(row, col + 4, ' ', header4_format)
                if rec.service:
                    worksheet.write(row, col + 5, rec.service, header4_format)
                else:
                    worksheet.write(row, col + 5, ' ', header4_format)
                if rec.request_date:
                    worksheet.write(row, col + 6, str(rec.request_date.strftime('%B')),header4_format)
                else:
                    worksheet.write(row, col + 6, str(' '), header4_format)

                if type=='standard':
                    worksheet.write(row, col + 7, rec.initial_amount, header4_format)
                if type=='shnider':
                    worksheet.write(row, col +7, sum([s.lst_price for s in rec.product_ids]), header4_format)
                row += 1

        if date_from and date_to and not type:

            maintenance_obj = self.env['maintenance.request'].search([('request_date','>=',date_from),('request_date','<=',date_to)])
            worksheet.write('A9', 'Sr. No.', t1)
            worksheet.write('B9', 'Date Approved', t1)
            worksheet.write('C9', 'Client Name',t1)
            worksheet.write('D9', 'UPS', t1)
            worksheet.write('E9', 'UPS Serial Number', t1)
            worksheet.write('F9', 'Service', t1)
            worksheet.write('G9', 'Month ', t1)
            worksheet.write('H9', 'Initial Amount ', t1)

            number = 0
            for rec in maintenance_obj:
                number =number +1
                worksheet.write(row, col, number, header4_format)

                if rec.request_date:
                    worksheet.write(row, col + 1, str(rec.request_date),header4_format)
                else:
                    worksheet.write(row, col + 1, str(' '), header4_format)
                if rec.partner_id:

                    worksheet.write(row, col + 2, rec.partner_id.name, header4_format)
                else:
                    worksheet.write(row, col + 2, ' ', header4_format)
                if rec.equipment_id:
                    worksheet.write(row, col + 3, rec.equipment_id.product_id.name, header4_format)
                else:
                    worksheet.write(row, col + 3, ' ', header4_format)
                if rec.equipment_id:
                    worksheet.write(row, col + 4, rec.equipment_id.lot_id.name, header4_format)
                else:
                    worksheet.write(row, col + 4, ' ', header4_format)
                if rec.service:
                    worksheet.write(row, col + 5, rec.service, header4_format)
                else:
                    worksheet.write(row, col + 5, ' ', header4_format)
                if rec.request_date:
                    worksheet.write(row, col + 6, str(rec.request_date.strftime('%B')),header4_format)
                else:
                    worksheet.write(row, col + 6, str(' '), header4_format)

                if type == 'standard':
                    worksheet.write(row, col + 7, rec.initial_amount, header4_format)
                if type == 'shnider':
                    worksheet.write(row, col + 7,sum([s.lst_price for s in rec.product_ids]), header4_format)

                row += 1

        if date_to and type and not date_from:
            print("ooooooooooooooooooooooooooooo")

            maintenance_obj = self.env['maintenance.request'].search([ ('request_date','<=', date_to),('type', '=', type)])
            print("777777777777777777",maintenance_obj)
            worksheet.write('A9', 'Sr. No.', t1)
            worksheet.write('B9', 'Date Approved', t1)
            worksheet.write('C9', 'Client Name', t1)
            worksheet.write('D9', 'UPS', t1)
            worksheet.write('E9', 'UPS Serial Number', t1)
            worksheet.write('F9', 'Service', t1)
            worksheet.write('G9', 'Month ', t1)
            worksheet.write('H9', 'Initial Amount ', t1)

            number = 0
            for rec in maintenance_obj:
                number = number + 1
                worksheet.write(row, col, number, header4_format)

                if rec.request_date:
                    worksheet.write(row, col + 1, str(rec.request_date), header4_format)
                else:
                    worksheet.write(row, col + 1, str(' '), header4_format)
                if rec.partner_id:
                    worksheet.write(row, col + 2, rec.partner_id.name, header4_format)
                else:
                    worksheet.write(row, col + 2, ' ', header4_format)
                if rec.equipment_id:
                    worksheet.write(row, col + 3, rec.equipment_id.product_id.name, header4_format)
                else:
                    worksheet.write(row, col + 3, ' ', header4_format)
                if rec.equipment_id:
                    worksheet.write(row, col + 4, rec.equipment_id.lot_id.name, header4_format)
                else:
                    worksheet.write(row, col + 4, ' ', header4_format)
                if rec.service:
                    worksheet.write(row, col + 5, rec.service, header4_format)
                else:
                    worksheet.write(row, col + 5, ' ', header4_format)

                if rec.request_date:
                    worksheet.write(row, col + 6, str(rec.request_date.strftime('%B')), header4_format)
                else:
                    worksheet.write(row, col + 6, str(' '), header4_format)
                if type == 'standard':
                    worksheet.write(row, col + 7, rec.initial_amount, header4_format)
                if type == 'shnider':
                    worksheet.write(row, col + 7,sum([s.lst_price for s in rec.product_ids]), header4_format)

                row += 1

        if date_to and  not type and not date_from:

            maintenance_obj = self.env['maintenance.request'].search([('request_date', '<=', date_to)])
            worksheet.write('A9', 'Sr. No.', t1)
            worksheet.write('B9', 'Date Approved', t1)
            worksheet.write('C9', 'Client Name', t1)
            worksheet.write('D9', 'UPS', t1)
            worksheet.write('E9', 'UPS Serial Number', t1)
            worksheet.write('F9', 'Service', t1)
            worksheet.write('G9', 'Month ', t1)
            worksheet.write('H9', 'Initial Amount ', t1)

            number = 0
            for rec in maintenance_obj:
                number = number + 1
                worksheet.write(row, col, number, header4_format)

                if rec.request_date:
                    worksheet.write(row, col + 1, str(rec.request_date), header4_format)
                else:
                    worksheet.write(row, col + 1, str(' '), header4_format)
                if rec.partner_id:
                    worksheet.write(row, col + 2, rec.partner_id.name, header4_format)
                else:
                    worksheet.write(row, col + 2, ' ', header4_format)
                if rec.equipment_id:
                    worksheet.write(row, col + 3, rec.equipment_id.product_id.name, header4_format)
                else:
                    worksheet.write(row, col + 3, ' ', header4_format)
                if rec.equipment_id:
                    worksheet.write(row, col + 4, rec.equipment_id.lot_id.name, header4_format)
                else:
                    worksheet.write(row, col + 4, ' ', header4_format)
                if rec.service:
                    worksheet.write(row, col + 5, rec.service, header4_format)
                else:
                    worksheet.write(row, col + 5, ' ', header4_format)
                if rec.request_date:
                    worksheet.write(row, col + 6, str(rec.request_date.strftime('%B')), header4_format)
                else:
                    worksheet.write(row, col + 6, str(' '), header4_format)
                if type == 'standard':
                    worksheet.write(row, col + 7, rec.initial_amount, header4_format)
                if type == 'shnider':
                    print("reccccccccccccccccccc",rec.total_price)
                    worksheet.write(row, col + 7, sum([s.lst_price for s in rec.product_ids]), header4_format)

                row += 1







