import base64
import io
from odoo import models,fields
from PIL import Image
import xlwt
from io import BytesIO

class BranchRefundtDataXls(models.AbstractModel):
    _name = 'report.maintenance_reports.refund_warranty_xsl'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

            header_format = workbook.add_format({
                'border': 1,
                'border_color': 'black',
                'align': 'center',
                'font_color': 'white',
                'bold': True,
                'valign': 'vcenter',
                'fg_color': '#339933'})
            header_format.set_text_wrap()
            header_format.set_font_size(11)

            header_format2= workbook.add_format({
                'border': 1,
                'border_color': 'black',
                'align': 'left',
                'font_color': 'white',
                # 'bold': True,
                'valign': 'vcenter',
                'fg_color': '#339933'})
            header_format2.set_text_wrap()
            header_format2.set_font_size(11)

            header1_format = workbook.add_format({
                # 'border': 1,
                'border_color': 'black',
                'align': 'center',
                'font_color': 'white',
                'bold': False,
                'valign': 'vcenter',
                'fg_color': '#339933'})
            header1_format.set_text_wrap()
            header1_format.set_font_size(12)

            header3_format = workbook.add_format({
                'border': 1,
                'border_color': 'black',
                'align': 'center',
                'font_color': 'black',
                # 'bold': True,
                'valign': 'vcenter',
                'fg_color': '#FFFFFF'})
            header3_format.set_text_wrap()
            header3_format.set_font_size(11)

            header4_format = workbook.add_format({
                'border': 1,
                'border_color': 'black',
                'align': 'center',
                'font_color': 'black',
                # 'bold': True,
                'valign': 'vcenter',
                'fg_color': '#FFFFFF'})
            header4_format.set_text_wrap()
            header4_format.set_font_size(12)

            t = workbook.add_format({
                # 'border': 1,
                'align': 'left',
                'border_color': 'black',
                'font_color': 'black',
                'valign': 'vcenter',
            })
            t.set_text_wrap()
            t.set_font_size(7)

            t4 = workbook.add_format({
                # 'border': 1,
                'align': 'left',
                'border_color': 'black',
                'font_color': '#0000FF',
                'valign': 'vcenter',
            })
            t4.set_text_wrap()
            t4.set_font_size(7)

            t1 = workbook.add_format({
                'border': 1,
                'align': 'left',
                'border_color': 'black',
                'font_color': 'black',
                'valign': 'vcenter',
            })
            t1.set_text_wrap()

            t2 = workbook.add_format({
                'border': 1,
                'align': 'center',
                'font_color': 'black',
                'fg_color': '#FFD700',
                'valign': 'vcenter',
            })
            t2.set_text_wrap()
            t2.set_font_size(11)

            t3 = workbook.add_format({
                'border': 1,
                'align': 'center',
                'border_color': 'black',
                'fg_color': '#808080',
                'font_color': 'white',
                'valign': 'vcenter',
            })
            t3.set_text_wrap()
            t3.set_font_size(12)



            worksheet = workbook.add_worksheet()

            # worksheet.right_to_left()
            worksheet.set_column('A:A',3)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 25)
            worksheet.set_column('E:E', 25)
            worksheet.set_column('G:G', 35)
            worksheet.set_column('F:F', 25)
            worksheet.set_column('H:H', 25)
            worksheet.set_column('I:I', 35)
            worksheet.set_column('J:J', 25)
            worksheet.set_column('K:K', 25)
            worksheet.set_column('L:L', 30)


            worksheet.set_row(0, 10)
            worksheet.set_row(0, 30)
            worksheet.set_row(2, 10)
            worksheet.set_row(3, 25)

            worksheet.set_row(11, 25)

            # cell_width = 64.0
            # cell_height = 20.0
            #
            # image_width = 460.0
            # image_height = 182.0
            #
            # x_scale = cell_width / image_width
            # y_scale = cell_height / image_height
            #
            # product_image = self.env.company.logo
            # imgdata = base64.b64decode(product_image)
            # image = io.BytesIO(imgdata)
            #
            # worksheet.insert_image('C1', 'logo.png',
            #                        {'image_data': image, 'x_scale': x_scale, 'y_scale': y_scale, 'x_offset': 8,
            #                         'y_offset': 8})

            worksheet.insert_image('C1', 'logo.png')



            worksheet.merge_range(
                'D1:G1', 'REIMBURSEMENT REQUEST  FORM - FOR ISSUING REPLACEMENT UNITS ', header_format)
            worksheet.write('G2', 'Help', header1_format)
            worksheet.write('B2', '*Send this document to the follow contacts*', t)
            worksheet.write('C2', 'esupport.middleeast@schneider-electric.com', t4)



            worksheet.merge_range( 'B4:C4', str(' Date '),header1_format)
            worksheet.merge_range('B5:C5',' ' , header1_format)
            worksheet.write('D5', 'Day',  header1_format)
            worksheet.write('D4', str(fields.Date.today().day), header4_format)
            worksheet.write('E5', 'Month',  header1_format)
            worksheet.write('E4', str(fields.Date.today().month), header4_format)
            worksheet.write('F5', 'Year', header1_format)
            worksheet.write('F4', str(fields.Date.today().year), header4_format)


            worksheet.merge_range(
                'B7:G7', 'COMPANY REQUESTING REIMBURSEMENT INFORMATION ', header_format)
            worksheet.merge_range(
                'G7:I7', '  ', header_format)
            worksheet.merge_range('B8:C8', str('*Company: '),header_format2)
            worksheet.merge_range('B9:C9', str(' *Address :'), header_format2)
            worksheet.merge_range('B10:C10', str(' *City :'), header_format2)
            worksheet.merge_range('B11:C11', str(' * STATE/PROVINCE:'), header_format2)
            worksheet.merge_range('B12:C12', str(' * COUNTRY:'), header_format2)
            worksheet.merge_range('B13:C13', str(' * CONTACT:'), header_format2)
            worksheet.merge_range('B14:C14', str(' * PHONE:'), header_format2)
            worksheet.merge_range('B15:C15', str(' * MAIL:'), header_format2)

            worksheet.merge_range('D8:F8', self.env.company.name, header3_format)
            worksheet.merge_range('F8:I8', '', header3_format)
            worksheet.merge_range('D9:F9', self.env.company.street, header3_format)
            worksheet.merge_range('F9:I9', ' ', header3_format)
            worksheet.merge_range('D10:F10', self.env.company.city, header3_format)
            worksheet.merge_range('F10:I10', ' ', header3_format)
            worksheet.merge_range('D11:F11', self.env.company.state_id.name, header3_format)
            worksheet.merge_range('F11:I11', ' ', header3_format)
            worksheet.merge_range('D12:F12', self.env.company.country_id.name, header3_format)
            worksheet.merge_range('F12:I12', ' ', header3_format)
            worksheet.merge_range('D13:F13', self.env.company.partner_id.name, header3_format)
            worksheet.merge_range('F13:I13', ' ', header3_format)
            worksheet.merge_range('D14:F14', self.env.company.phone, header3_format)
            worksheet.merge_range('F14:I14',' ', header3_format)
            worksheet.merge_range('D15:F15', self.env.company.email, header3_format)
            worksheet.merge_range('F15:I15',' ', header3_format)




            worksheet.merge_range('B17:G17', 'Product INFO ', header_format)
            worksheet.merge_range('G17:L17', '  ', header_format)

            worksheet.write('B18', 'End User Name ', t3)
            worksheet.write('C18', 'Issue/Problem Description ', t3)
            worksheet.write('D18', 'Defective Part Number ', t3)
            worksheet.write('E18', 'Defective Serial Number ', t3)
            worksheet.write('F18', 'Replacement Part Number', t3)
            worksheet.write('G18', 'Replacement Serial  Number ', t3)
            worksheet.write('H18', 'Purchase Date ', t3)
            worksheet.write('I18', 'Date End user Obtained Replacement ',  header_format2)
            worksheet.write('J18', 'Service Request Number ', t3)
            worksheet.write('K18', 'RMA Number ', t3)
            worksheet.write('L18', 'Model/unit replacement cost ', header_format2)

            row = 19
            col = 1
            total=0.0
            for line in lines:

                if line.end_user_name:
                      worksheet.write(row, col, line.end_user_name, header4_format)
                else:
                      worksheet.write(row, col, ' ', header4_format)
                if line.issue_problem:
                      worksheet.write(row, col+1, line.issue_problem, header4_format)
                else:
                    worksheet.write(row, col + 1, ' ', header4_format)

                if line.defective_part_number:
                      worksheet.write(row, col+2, line.defective_part_number, header4_format)
                else:
                    worksheet.write(row, col + 2, ' ', header4_format)

                if line.defective_serial_number:
                      worksheet.write(row, col+3, line.defective_serial_number, header4_format)
                else:
                    worksheet.write(row, col + 3, ' ', header4_format)

                if line.replacement_part_number:
                      worksheet.write(row, col+4, line.replacement_part_number, header4_format)
                else:
                    worksheet.write(row, col + 4, ' ', header4_format)
                if line.replacement_serial_number:
                      worksheet.write(row, col+5, line.replacement_serial_number, header4_format)
                else:
                    worksheet.write(row, col + 5, ' ', header4_format)

                if line.purchase_date:
                      worksheet.write(row, col+6, str(line.purchase_date), header4_format)
                else:
                    worksheet.write(row, col + 6, ' ', header4_format)

                if line.end_user_date:
                      worksheet.write(row, col+7, str(line.end_user_date), header4_format)
                else:
                    worksheet.write(row, col + 7, ' ', header4_format)

                if line.service_request_number:
                      worksheet.write(row, col+8, line.service_request_number, header4_format)
                else:
                    worksheet.write(row, col + 8, ' ', header4_format)

                if line.rma_number:
                    worksheet.write(row, col+9, line.rma_number, header4_format)
                else:
                    worksheet.write(row, col + 9, ' ', header4_format)

                if line.total_price:
                    worksheet.write(row, col + 10, sum([rec.lst_price for rec in line.product_ids]), header4_format)
                else:
                    worksheet.write(row, col + 10, ' ', header4_format)

                for rec in line.product_ids:
                    total+=rec.lst_price

                row += 1

            worksheet.write(row, col + 9, 'Total Invoices ', t2)
            worksheet.write(row, col + 10, total, t2)


            worksheet.merge_range(row + 5,1, row + 5, 11, 'Comments', t1)
            worksheet.merge_range(row + 6, 1, row + 6, 11, ' ', t1)
            worksheet.merge_range(row + 7, 1, row + 7, 11, ' ', t1)
            worksheet.merge_range(row + 8, 1, row + 8, 11, ' ', t1)
            worksheet.merge_range(row +9, 1, row + 9, 11, ' ', t1)












