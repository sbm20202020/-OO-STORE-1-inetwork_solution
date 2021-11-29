# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta, date
from odoo.http import request
from odoo import api, fields, models, _
from io import BytesIO
from odoo.exceptions import ValidationError, UserError



class PayslipReportDataXls(models.AbstractModel):
    _name = 'report.commission_kpi.commission_kpi_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        wizard_record = request.env['kpi.wizard'].search([])[-1]
        header_title_format = workbook.add_format({
            'border': 2,
            'border_color': 'black',
            'align': 'center',
            'font_color': '#0b034d;',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': '#C0C0C0'})
        header_title_format.set_text_wrap()
        header_title_format.set_font_size(14)
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
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            'fg_color': '#a6e764'})
        header2_format.set_text_wrap()
        header2_format.set_font_size(12)
        header4_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': False,
            'valign': 'vcenter',
            'fg_color': '#a6e764'})
        header4_format.set_text_wrap()
        header4_format.set_font_size(10)

        header3_format = workbook.add_format({
            'border': 1,
            'border_color': 'black',
            'align': 'center',
            'font_color': 'black',
            'bold': False,
            'valign': 'vcenter',
            'fg_color': '#FFFFFF'})
        header3_format.set_text_wrap()
        header3_format.set_font_size(10)
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 50)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 25)
        worksheet.set_column('N:N', 20)
        # worksheet.merge_range('A1:N2', 'KPI Commission Report', header_title_format1)
        worksheet.write('A1', 'Invoice Number', header2_format)
        worksheet.write('B1', 'Invoice Partner Display Name (Customer Name)', header2_format)
        worksheet.write('C1', 'Type', header2_format)
        worksheet.write('D1', 'Invoice/Bill Date', header2_format)
        worksheet.write('E1', 'Quarters', header2_format)
        worksheet.write('F1', 'SO Number', header2_format)
        worksheet.write('G1', 'Salesperson', header2_format)
        worksheet.write('H1', 'Untaxed Amount', header2_format)
        # worksheet.write('I1', 'PO Number', header2_format)
        worksheet.write('I1', 'Cost price', header2_format)
        worksheet.write('J1', 'Net Profit', header2_format)
        worksheet.write('K1', 'Percentage', header2_format)
        worksheet.write('L1', 'Commission Percentage', header2_format)
        worksheet.write('M1', 'Comm Amount', header2_format)
        row = 1
        col = 0
        if len(wizard_record.sales_person) == 0:
            invoices = self.env['account.move'].search(
                [('invoice_date', '>=', wizard_record.date_from), ('type','=', 'out_invoice'),('invoice_date', '<=', wizard_record.date_to)]).sorted(key=lambda r: r.invoice_user_id.id)
            salespersons=[invoice.invoice_user_id for invoice in invoices]
            if invoices:
                for salesperson in set(salespersons):
                    total_amount_untaxed = 0.0
                    total_cost = 0.0
                    total_actual_kpi = 0
                    worksheet.merge_range('A' + str(row + 1) + ':' + 'M' + str(row + 1),salesperson.name or '',header2_format)
                    row +=1

                    total_actual_kpi = (wizard_record.kpi_ref_ids.filtered(lambda s: s.user_id == salesperson)).total_actual/100

                    for invoice in invoices:
                        if invoice.invoice_user_id == salesperson:
                            products = invoice.invoice_line_ids.filtered(lambda self: self.product_id.type == 'product')
                            service = invoice.invoice_line_ids.filtered(lambda self: self.product_id.type != 'product')
                            if products:
                               for product in products:
                                    cost_product = abs(sum(value.value for value in
                                                      self.env['stock.valuation.layer'].search(
                                                          [('stock_move_id.origin', '=', invoice.invoice_origin)]) if value.product_id.type == 'product' and value.product_id == product.product_id))
                                    total_amount_untaxed += product.credit
                                    total_cost += cost_product

                                    worksheet.write(row, col, invoice.name, header3_format)
                                    worksheet.write(row, col + 1, invoice.partner_id.name, header3_format)
                                    worksheet.write(row, col + 2, 'Products', header3_format)
                                    worksheet.write(row, col + 3,
                                                    str(datetime.strptime(str(invoice.invoice_date), '%Y-%m-%d').date()),
                                                    header3_format)
                                    worksheet.write(row, col + 4, wizard_record.quarter_date or '', header3_format)
                                    worksheet.write(row, col + 5, invoice.invoice_origin or '', header3_format)
                                    worksheet.write(row, col + 6, invoice.invoice_user_id.name or '', header3_format)
                                    worksheet.write(row, col + 7, "{:.2f}".format(product.credit), header3_format)
                                    # worksheet.write(row, col + 8, '', header3_format)
                                    worksheet.write(row, col + 8, "{:.2f}".format(cost_product), header3_format)
                                    worksheet.write(row, col + 9, "{:.2f}".format(product.credit- cost_product),
                                                    header3_format)
                                    percentage=((product.credit- cost_product)/cost_product if cost_product !=0.0 else 0.0)*100
                                    worksheet.write(row, col + 10,
                                                    str("{:.2f}".format(
                                                        (percentage))) or '' + '%',
                                                    header3_format)
                                    worksheet.write(row, col + 11, '5.0%', header3_format)
                                    worksheet.write(row, col + 12,
                                                    "{:.2f}".format((product.credit - cost_product) * 5 / 100),
                                                    header3_format)
                                    row += 1
                            if service:
                               for ser in service:
                                # cost_service = sum(value.value / value.quantity for value in
                                #                    self.env['stock.valuation.layer'].search(
                                #                        [(
                                #                         'stock_move_id.origin', '=', invoice.invoice_origin)]) if value.product_id.type != 'product' and value.product_id == ser.product_id)
                                total_amount_untaxed += ser.credit
                                cost_service=ser.credit * 70/100
                                total_cost += cost_service


                                worksheet.write(row, col, invoice.name, header3_format)
                                worksheet.write(row, col + 1, invoice.partner_id.name, header3_format)
                                worksheet.write(row, col + 2, 'Services', header3_format)
                                worksheet.write(row, col + 3,
                                                str(datetime.strptime(str(invoice.invoice_date), '%Y-%m-%d').date()),
                                                header3_format)
                                worksheet.write(row, col + 4, wizard_record.quarter_date or '', header3_format)
                                worksheet.write(row, col + 5, invoice.invoice_origin or '', header3_format)
                                worksheet.write(row, col + 6, invoice.invoice_user_id.name or '', header3_format)
                                worksheet.write(row, col + 7, "{:.2f}".format(ser.credit), header3_format)
                                # worksheet.write(row, col + 8, '', header3_format)
                                worksheet.write(row, col + 8, "{:.2f}".format(cost_service), header3_format)
                                worksheet.write(row, col + 9, "{:.2f}".format(ser.credit - cost_service),
                                                header3_format)
                                percentage = ((ser.credit - cost_service) / cost_service if cost_service != 0.0 else 0.0) * 100

                                worksheet.write(row, col + 10,
                                                str("{:.2f}".format(
                                                    (percentage))) or '' + '%',
                                                header3_format)
                                worksheet.write(row, col + 11, '5.0%', header3_format)
                                worksheet.write(row, col + 12,
                                                "{:.2f}".format((ser.credit - cost_service) * 5 / 100),
                                                header3_format)
                                row += 1
                    total_net_profit = total_amount_untaxed - total_cost
                    # total_percentage = (100 - (total_cost/total_amount_untaxed*100)) if total_amount_untaxed !=0.0 else 0.0
                    total_percentage = ((total_amount_untaxed - total_cost) / total_cost if total_cost != 0.0 else 0.0) * 100
                    total_comm_amount = total_net_profit * 5 / 100
                    after_kpi = total_comm_amount * total_actual_kpi
                    net_after_taxs = after_kpi * 0.9
                    worksheet.write(row, col, '', header4_format)
                    worksheet.write(row, col + 1, '', header4_format)
                    worksheet.write(row, col + 2, '', header4_format)
                    worksheet.write(row, col + 3, '', header4_format)
                    worksheet.write(row, col + 4, '', header4_format)
                    worksheet.write(row, col + 5, '', header4_format)
                    worksheet.write(row, col + 6, '', header4_format)
                    worksheet.write(row, col + 7, "{:.2f}".format(total_amount_untaxed), header4_format)
                    # worksheet.write(row, col + 8, '', header4_format)
                    worksheet.write(row, col + 8, "{:.2f}".format(total_cost), header4_format)
                    worksheet.write(row, col + 9, "{:.2f}".format(total_net_profit), header4_format)
                    worksheet.write(row, col + 10, str("{:.2f}".format(total_percentage)) or '' + '%', header4_format)
                    worksheet.write(row, col + 11, '', header4_format)
                    worksheet.write(row, col + 12, "{:.2f}".format(total_comm_amount), header4_format)

                    row += 1
                    worksheet.write(row, col + 10, (str("{:.2f}".format(total_actual_kpi)) or '')+ '%', header3_format)
                    worksheet.write(row, col + 11, 'After KPI', header3_format)
                    worksheet.write(row, col + 12, "{:.2f}".format(after_kpi), header3_format)

                    row += 1
                    worksheet.write(row, col + 11, 'Net After Taxs', header3_format)
                    worksheet.write(row, col + 12, "{:.2f}".format(net_after_taxs), header3_format)
                    row += 1


        else:
            invoices = self.env['account.move'].search(
                [('invoice_date', '>=', wizard_record.date_from), ('type','=', 'out_invoice'), ('invoice_date', '<=', wizard_record.date_to),
                 ('invoice_user_id', 'in', wizard_record.sales_person.ids)]).sorted(key=lambda r: r.invoice_user_id.id)
            if invoices:
                for salesperson in wizard_record.sales_person:
                    total_amount_untaxed = 0.0
                    total_cost = 0.0
                    total_actual_kpi = 0
                    worksheet.merge_range('A' + str(row + 1) + ':' + 'M' + str(row + 1),salesperson.name or '',header2_format)
                    row +=1
                    total_actual_kpi = (wizard_record.kpi_ref_ids.filtered(lambda s: s.user_id == salesperson)).total_actual/100

                    for invoice in invoices:
                        if invoice.invoice_user_id == salesperson:
                            products = invoice.invoice_line_ids.filtered(lambda self: self.product_id.type == 'product')
                            service = invoice.invoice_line_ids.filtered(lambda self: self.product_id.type != 'product')
                            if products:
                               for product in products:
                                    cost_product = abs(sum(value.value for value in
                                                      self.env['stock.valuation.layer'].search(
                                                          [('stock_move_id.origin', '=', invoice.invoice_origin)]) if value.product_id.type == 'product' and value.product_id == product.product_id))
                                    total_amount_untaxed += product.credit
                                    total_cost += cost_product

                                    worksheet.write(row, col, invoice.name, header3_format)
                                    worksheet.write(row, col + 1, invoice.partner_id.name, header3_format)
                                    worksheet.write(row, col + 2, 'Products', header3_format)
                                    worksheet.write(row, col + 3,
                                                    str(datetime.strptime(str(invoice.invoice_date), '%Y-%m-%d').date()),
                                                    header3_format)
                                    worksheet.write(row, col + 4, wizard_record.quarter_date or '', header3_format)
                                    worksheet.write(row, col + 5, invoice.invoice_origin or '', header3_format)
                                    worksheet.write(row, col + 6, invoice.invoice_user_id.name or '', header3_format)
                                    worksheet.write(row, col + 7, "{:.2f}".format(product.credit), header3_format)
                                    # worksheet.write(row, col + 8, '', header3_format)
                                    worksheet.write(row, col + 8, "{:.2f}".format(cost_product), header3_format)
                                    worksheet.write(row, col + 9, "{:.2f}".format(product.credit- cost_product),
                                                    header3_format)
                                    percentage = ((product.credit - cost_product) / cost_product if cost_product != 0.0 else 0.0) * 100

                                    worksheet.write(row, col + 10,
                                                    (str("{:.2f}".format(
                                                        (percentage))) or '' )+ '%',
                                                    header3_format)
                                    worksheet.write(row, col + 11, '5.0%', header3_format)
                                    worksheet.write(row, col + 12,
                                                    "{:.2f}".format((product.credit - cost_product) * 5 / 100),
                                                    header3_format)
                                    row += 1
                            if service:
                               for ser in service:
                                # cost_service = sum(value.value / value.quantity for value in
                                #                    self.env['stock.valuation.layer'].search(
                                #                        [(
                                #                         'stock_move_id.origin', '=', invoice.invoice_origin)]) if value.product_id.type != 'product' and value.product_id == ser.product_id)
                                total_amount_untaxed += ser.credit
                                cost_service=ser.credit * 70/100
                                total_cost += cost_service


                                worksheet.write(row, col, invoice.name, header3_format)
                                worksheet.write(row, col + 1, invoice.partner_id.name, header3_format)
                                worksheet.write(row, col + 2, 'Services', header3_format)
                                worksheet.write(row, col + 3,
                                                str(datetime.strptime(str(invoice.invoice_date), '%Y-%m-%d').date()),
                                                header3_format)
                                worksheet.write(row, col + 4, wizard_record.quarter_date or '', header3_format)
                                worksheet.write(row, col + 5, invoice.invoice_origin or '', header3_format)
                                worksheet.write(row, col + 6, invoice.invoice_user_id.name or '', header3_format)
                                worksheet.write(row, col + 7, "{:.2f}".format(ser.credit), header3_format)
                                # worksheet.write(row, col + 8, '', header3_format)
                                worksheet.write(row, col + 8, "{:.2f}".format(cost_service), header3_format)
                                worksheet.write(row, col + 9, "{:.2f}".format(ser.credit - cost_service),
                                                header3_format)
                                percentage = ((ser.credit - cost_service) / cost_service if cost_service != 0.0 else 0.0) * 100

                                worksheet.write(row, col + 10,
                                                (str("{:.2f}".format(
                                                    (percentage))) or '') + '%',
                                                header3_format)
                                worksheet.write(row, col + 11, '5.0%', header3_format)
                                worksheet.write(row, col + 12,
                                                "{:.2f}".format((ser.credit - cost_service) * 5 / 100),
                                                header3_format)
                                row += 1
                    total_net_profit = total_amount_untaxed - total_cost
                    # total_percentage = (100 - (total_cost/total_amount_untaxed*100)) if total_amount_untaxed !=0.0 else 0.0
                    total_percentage = ((total_amount_untaxed - total_cost) / total_cost if total_cost != 0.0 else 0.0) * 100

                    total_comm_amount = total_net_profit * 5 / 100
                    after_kpi = total_comm_amount * total_actual_kpi
                    net_after_taxs = after_kpi * 0.9
                    worksheet.write(row, col, '', header4_format)
                    worksheet.write(row, col + 1, '', header4_format)
                    worksheet.write(row, col + 2, '', header4_format)
                    worksheet.write(row, col + 3, '', header4_format)
                    worksheet.write(row, col + 4, '', header4_format)
                    worksheet.write(row, col + 5, '', header4_format)
                    worksheet.write(row, col + 6, '', header4_format)
                    worksheet.write(row, col + 7, "{:.2f}".format(total_amount_untaxed), header4_format)
                    # worksheet.write(row, col + 8, '', header4_format)
                    worksheet.write(row, col + 8, "{:.2f}".format(total_cost), header4_format)
                    worksheet.write(row, col + 9, "{:.2f}".format(total_net_profit), header4_format)
                    worksheet.write(row, col + 10, (str("{:.2f}".format(total_percentage)) or '')+ '%', header4_format)
                    worksheet.write(row, col + 11, '', header4_format)
                    worksheet.write(row, col + 12, "{:.2f}".format(total_comm_amount), header4_format)

                    row += 1
                    worksheet.write(row, col + 10, (str("{:.2f}".format(total_actual_kpi)) or '')+ '%', header3_format)
                    worksheet.write(row, col + 11, 'After KPI', header3_format)
                    worksheet.write(row, col + 12, "{:.2f}".format(after_kpi), header3_format)

                    row += 1
                    worksheet.write(row, col + 11, 'Net After Taxs', header3_format)
                    worksheet.write(row, col + 12, "{:.2f}".format(net_after_taxs), header3_format)
                    row += 1

        return
