# -*- coding: utf-8 -*-
from odoo import models, api
from datetime import datetime , timedelta , date


class SupplierStatusReportXLSX(models.AbstractModel):
    _name = 'report.oh_appraisal_survey_custom.answer_report_excel'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, lines):
        header_format_score = workbook.add_format({
                    'border': 1,
                    'align': 'left',
                    'font_color': 'black',
                    'bold': False,
            'font': '5',

            'valign': 'vleft',
                    'fg_color':'white'})
        header_format_score.set_text_wrap()
        header_format_blue = workbook.add_format({
                    'border': 1,
                    'align': 'center',
                    'font_color': 'black',
                    'bold': True,
                    'valign': 'vcenter',
                    'fg_color':'#DFE9F2'})
        header_format_blue.set_text_wrap()
        header_format_yellow = workbook.add_format({
                    'border': 1,
                    'align': 'center',
                    'font_color': 'black',
                    'bold': True,
                    'valign': 'vcenter',
                    'fg_color':'yellow'})
        header_format_yellow.set_text_wrap()
        header_format_green = workbook.add_format({
                    'border': 1,
                    'align': 'center',
                    'font_color': 'black',
                    'bold': True,
                    'valign': 'vcenter',
                    'fg_color':'#90ee90'})
        header_format_green.set_text_wrap()
        header_format = workbook.add_format({ #very dark blue
                    'border': 1,
                    'align': 'center',
                    'font_color': 'black',
                    'bold': True,
                    'valign': 'vcenter',
                    'fg_color': 'white'})
        header_format.set_text_wrap()
        header1_format = workbook.add_format({ #very dark blue
                    'border': 1,
                    'align': 'center',
                    'font_color': 'black',
                    'bold': True,
                    'valign': 'vcenter',
                    'fg_color': 'white'})
        header1_format.set_text_wrap()

        header2_format = workbook.add_format({ #very dark blue
                    'border': 1,
                    'align': 'center',
                    'font_color': 'black',
                    'bold': False,
                    'valign': 'vcenter',
                    'fg_color':'white'})
        header2_format.set_text_wrap()
        header1_format.set_font_size(10)
        header_format.set_font_size(10)
        header2_format.set_font_size(10)
        t1 = workbook.add_format({  # light grey
            'border': 0,
            'align': 'right',
            'font_color': 'black',
            'valign': 'vcenter',

            'fg_color': '#D8D8D8'})
        t2 = workbook.add_format({  #light grey
                    'border': 0,
                    'align': 'center',
                    'font_color': 'black',
                    'valign': 'vcenter',

                    'fg_color': '#D8D8D8'})
        t2.set_text_wrap()

        t3 = workbook.add_format({  #white
                    'border': 2,
                    'align': 'center',
                    'font_color': 'black',
            'font': '16',
            'bold': True,
                    'valign': 'vcenter',
                    'fg_color': '#ffffff'})
        t3.set_text_wrap()
        t4 = workbook.add_format({  #white
                    'border':2,
                    'align': 'right',
                    'bold': True,
                    'font_color': 'black',
                    'valign': 'vcenter',
                    'fg_color': '#ffffff'})
        t4.set_text_wrap()
        t5= workbook.add_format({  # white
            'border': 2,
            'align': 'right',
            'bold': True,
            'font_color': 'black',
            'valign': 'vcenter',
            'fg_color': '#ffffff'})
        t5.set_text_wrap()
        t6 = workbook.add_format({  # white
            'border': 2,
            'align': 'right',
            'bold': True,
            'font_color': 'white',
            'valign': 'vcenter',
            'fg_color': '#ffffff'})
        t6.set_text_wrap()



        row=4
        row2=0
        row1=0
        col = 0
        col1 = 3
        col2 = 3
        score_total=0

        for line in lines:
            worksheet = workbook.add_worksheet()
            worksheet.set_column('A:Z', 20)
            worksheet.merge_range('A1:F1', 'Annual Interview', header_format_blue)

            for question in line.survey_id.question_and_page_ids.sorted(key=lambda l: (l.sequence)):
                row1 = row2+question.sequence
                rows = row1+2
                if question.need_header:
                   for label in question.labels_ids:
                        worksheet.write(row1, col + col1, label.value, header_format_green)
                        col1 += 1
                else:
                   if not question.multi_row:
                       col2=3
                       for label in question.labels_ids:
                            worksheet.write(row1, col + col2, label.value, header_format_green)
                            col2 += 1
                score=0


                for input_line in line.user_input_line_ids:
                    if question == input_line.question_id:
                       if question.question_type == 'free_text':

                           if question.color_yellow==True:
                               worksheet.write(row1,col,question.title, header_format_yellow)
                               worksheet.set_row(row1, 70)

                               worksheet.merge_range('B' + str(row1+1) + ':' + 'D' + str(row1+1),input_line.value_free_text if input_line.value_free_text !=False else '', header2_format)
                               row+=1
                           elif question.color_green==True:
                               worksheet.write(row1,col,question.title,header_format_green)
                               worksheet.set_row(row1, 70)

                               worksheet.merge_range('B' + str(row1+1) + ':' + 'D' + str(row1+1),input_line.value_free_text if input_line.value_free_text !=False else '', header2_format)
                               row+=1
                           else:
                               worksheet.write(row1,col,question.title, header_format)
                               worksheet.set_row(row1, 70)

                               worksheet.merge_range('B' + str(row1+1) + ':' + 'D' + str(row1+1),input_line.value_free_text if input_line.value_free_text !=False else '', header2_format)
                               row += 1
                           row2 +=1
                       if question.question_type == 'textbox':
                               worksheet.write(row1,col,question.title, header_format)
                               worksheet.set_row(row1, 50)
                               worksheet.merge_range('B' + str(row1+1) + ':' + 'C' + str(row1+1),input_line.value_text if input_line.value_text !=False else '', header2_format)
                               row += 1
                               row2 += 1

                       if question.question_type == 'numerical_box':
                               worksheet.write(row1,col,question.title, header_format)
                               worksheet.set_row(row1, 50)
                               worksheet.merge_range('B' + str(row1+1) + ':' + 'C' + str(row1+1),input_line.value_number if input_line.value_number !=0 else '', header2_format)
                               row += 1
                               row2 += 1

                       if question.question_type == 'date':
                               worksheet.write(row1,col,question.title, header_format)
                               worksheet.set_row(row1, 50)
                               worksheet.merge_range('B' + str(row1+1) + ':' + 'C' + str(row1+1),str(datetime.strptime(str(input_line.value_date), '%Y-%m-%d').date()) if input_line.value_date != False else '', header2_format)
                               row += 1
                               row2 += 1
                       if question.question_type == 'datetime':
                               worksheet.write(row1,col,question.title, header_format)
                               worksheet.set_row(row1, 50)
                               worksheet.merge_range('B' + str(row1+1) + ':' + 'C' + str(row1+1),str(datetime.strptime(str(input_line.value_datetime), '%Y-%m-%d %H:%M:%S')) if input_line.value_datetime != False else '', header2_format)
                               row += 1
                               row2 += 1
                       if question.question_type == 'matrix':
                           if question.multi_row :

                               if question.need_header:
                                   for header in question.header_labels:
                                       worksheet.write(row1,col,header.value, header_format)
                                       worksheet.write(row1,col+1,header.value2, header_format)
                                       worksheet.write(row1,col+2,header.value3, header_format)

                               worksheet.merge_range('A' + str(row1+3) + ':' + 'A' + str(row1+3+len(question.labels_ids_2)),question.title, header_format_yellow)
                               # for l in question.labels_ids_2:
                               # for rows in range(row1 + 2, row1 + 3 + len(question.labels_ids_2), 1):
                               worksheet.set_row(rows, 35)
                               worksheet.write(rows, col + 1, input_line.value_suggested_row.value2, header_format)
                               worksheet.write(rows, col + 2, input_line.value_suggested_row.value3, header_format)
                               for label in question.labels_ids:
                                   if input_line.value_suggested == label:
                                           score +=input_line.answer_score
                                           score_total += input_line.answer_score
                                           worksheet.write(rows, col +2+label.sequence ,input_line.answer_score if input_line.answer_score !=0 else input_line.value_suggested.value, header_format)
                                   else:
                                           worksheet.write(rows,col +2+label.sequence,'', header_format)

                               worksheet.merge_range('B' + str(row1+3+len(question.labels_ids_2)) + ':' + 'C' + str(row1+3+len(question.labels_ids_2)),'Score', header_format_blue)
                               worksheet.write(row1+2+len(question.labels_ids_2),3,score, header_format_blue)

                               row2 += 2
                               rows+=1


                           else:
                               worksheet.merge_range('A' + str(row1+2) + ':' + 'C' + str(row1+2),question.title, header_format)
                               worksheet.merge_range('A' + str(row1+3) + ':' + 'C' + str(row1+3),input_line.value_suggested_row.value, header_format)

                               for label in question.labels_ids:

                                   if input_line.value_suggested == label:
                                           score +=input_line.answer_score
                                           worksheet.write(rows, col +2+label.sequence ,input_line.answer_score if input_line.answer_score !=0 else input_line.value_suggested.value, header_format)
                                   else:
                                           worksheet.write(rows,col +2+label.sequence,'', header_format)
                               row2 += 2
                               rows+=1
            worksheet.merge_range('A' + str(row1 + 3) + ':' + 'B' + str(row1 +3),'Up to 60% : Not Achieved', header_format_score)
            worksheet.merge_range('A' + str(row1 + 4) + ':' + 'B' + str(row1 +4), 'Up to 75%: Partially Achieved', header_format_score)
            worksheet.merge_range('A' + str(row1 + 5) + ':' + 'B' + str(row1 +5), 'Up to 100%: Achieved', header_format_score)
            worksheet.merge_range('A' + str(row1 + 6) + ':' + 'B' + str(row1 +6), 'Over 100%: Exceeds', header_format_score)
            worksheet.merge_range('C' + str(row1 + 3) + ':' + 'D' + str(row1 +4), 'Score Achieved', header_format_blue)
            worksheet.merge_range('C' + str(row1 + 5) + ':' + 'D' + str(row1 +6), 'Total Score', header_format_blue)
            worksheet.merge_range('E' + str(row1 + 3) + ':' + 'E' + str(row1 +4), score_total, header_format_blue)
            worksheet.merge_range('E' + str(row1 + 5) + ':' + 'E' + str(row1 +6), '100', header_format_blue)
            worksheet.merge_range('F' + str(row1 + 3) + ':' + 'F' + str(row1 +4), '%', header_format_blue)
            worksheet.merge_range('F' + str(row1 + 5) + ':' + 'F' + str(row1 +6),str(score_total/100)*100+' %', header_format_blue)

