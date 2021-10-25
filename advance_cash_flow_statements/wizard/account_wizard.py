# -*- coding: utf-8 -*-

import json
from datetime import datetime , timedelta , date
import calendar

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import date_utils, io, xlsxwriter


class AccountWizard(models.TransientModel):
    _name = "account.wizard"
    _inherit = "account.common.report"

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", default=fields.Date.today, required=True)
    today = fields.Date("Report Date", default=fields.Date.today)
    levels = fields.Selection([('summary', 'Summary'),
                               ('consolidated', 'Consolidated'),
                               ('detailed', 'Detailed'),
                               ('very', 'Very Detailed')],
                              string='Levels', required=True, default='summary',
                              help='Different levels for cash flow statements \n'
                                   'Summary: Month wise report.\n'
                                   'Consolidated: Based on account types.\n'
                                   'Detailed: Based on accounts.\n'
                                   'Very Detailed: Accounts with their move lines')
    partner_ids=fields.Many2many('res.partner')
    account_ids=fields.Many2many('account.account')

    def generate_pdf_report(self):
        self.ensure_one()
        logged_users = self.env['res.company']._company_default_get('account.account')
        if self.date_from:
            if self.date_from > self.date_to:
                raise UserError("Start date should be less than end date")
        data = {
            'ids': self.ids,
            'model': self._name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'levels': self.levels,
            'target_move': self.target_move,
            'today': self.today,
            'logged_users': logged_users.name,
        }

        return self.env.ref('advance_cash_flow_statements.pdf_report').report_action(self, data=data)

    def generate_xlsx_report(self):
        date_from = datetime.strptime(str(self.date_from), "%Y-%m-%d")
        date_to = datetime.strptime(str(self.date_to), "%Y-%m-%d")
        if date_from:
            if date_from > date_to:
                raise UserError("Start date should be less than end date")
        data = {
            'ids': self.ids,
            'model': self._name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'levels': self.levels,
            'partner_ids': self.partner_ids.ids,
            'account_ids': self.account_ids.ids,
            'target_move': self.target_move,
            'today': self.today,
        }
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'account.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Adv Cash Flow Statement',
                     }
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        fetched_data = []
        previous_balance = []
        account_res = []
        journal_res = []
        fetched = []
        account_type_id = self.env.ref('account.data_account_type_liquidity').id
        # + \
        #     """' AND aat.id='""" + str(account_type_id)
        currency_symbol = self.env.user.company_id.currency_id.symbol

        if data['levels'] == 'summary':
            account= """AND aml.account_id IN %s""" if len(data['account_ids']) > 0 else """"""
            partner = """'AND aml.partner_id IN %s""" if len(data['partner_ids']) > 0 else """'"""
            state = """'AND aml.parent_state ='"""+str('posted') if data['target_move'] == 'posted' else """"""
            query3 = """SELECT aml.move_id as move_id , aml.account_id as account_id ,aa.name as account ,aml.name as name_aml,cc.name as currency,pp.name as partner,aml.partner_id as partner_id,aml.date as date_aml,aml.date_maturity as due_date,
                        aml.debit AS total_debit, aml.credit AS total_credit,aml.balance AS total_balance FROM account_move_line as aml
                                 INNER JOIN account_account aa ON aa.id = aml.account_id and aa.is_cash_flow = True
                                 LEFT JOIN res_currency cc ON cc.id = aa.currency_id
                                 LEFT JOIN res_partner pp ON pp.id = aml.partner_id
                                 WHERE aml.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(data['date_to']) + state +partner+account+\
                     """GROUP BY move_id ,due_date,date_aml,account,partner,currency,total_debit,total_credit,total_balance,name_aml,partner_id,account_id"""
            cr = self._cr
            tuples=()
            if len(data['account_ids']) > 0 and len(data["partner_ids"]) <=0:
                tuples=(tuple(data["account_ids"]),)
            elif len(data['account_ids']) <= 0 and len(data["partner_ids"]) >0:
                tuples=(tuple(data["partner_ids"]),)
            elif len(data['account_ids']) > 0 and len(data["partner_ids"]) >0:
                tuples=(tuple(data["partner_ids"]),tuple(data["account_ids"]))
            cr.execute(query3,tuples)
            fetched_data = cr.dictfetchall()

            query2 = """SELECT aml.move_id as move_id , aml.account_id as account_id ,aa.name as account ,aml.name as name_aml,cc.name as currency,pp.name as partner,aml.partner_id as partner_id,aml.date as date_aml,aml.date_maturity as due_date,
                        sum(aml.debit) AS total_debit, sum(aml.credit) AS total_credit,aml.balance AS total_balance FROM account_move_line as aml
                                 INNER JOIN account_account aa ON aa.id = aml.account_id and aa.is_cash_flow = True
                                 LEFT JOIN res_currency cc ON cc.id = aa.currency_id
                                 LEFT JOIN res_partner pp ON pp.id = aml.partner_id
                                 WHERE aml.date < '""" + str(data['date_from']) +\
                      state +partner+account+\
                     """GROUP BY move_id ,due_date ,date_aml,account,partner,currency,total_balance,name_aml,partner_id,account_id"""
            cr = self._cr
            cr.execute(query2,tuples)
            previous_balance = cr.dictfetchall()


        # elif data['levels'] == 'consolidated':
        #     state = """ WHERE am.state = 'posted' """ if data['target_move'] == 'posted' else ''
        #     query2 = """SELECT aat.name, sum(aml.debit) AS total_debit, sum(aml.credit) AS total_credit,
        #                  sum(aml.balance) AS total_balance FROM (  SELECT am.id, am.state FROM account_move as am
        #                  LEFT JOIN account_move_line aml ON aml.move_id = am.id
        #                  LEFT JOIN account_account aa ON aa.id = aml.account_id and aa.is_cash_flow = True
        #                  LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #                  WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
        #         data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' ) am
        #                              LEFT JOIN account_move_line aml ON aml.move_id = am.id
        #                              LEFT JOIN account_account aa ON aa.id = aml.account_id and aa.is_cash_flow = True
        #                              LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #                              """ + state + """GROUP BY aat.name"""
        #     cr = self._cr
        #     cr.execute(query2)
        #     fetched_data = cr.dictfetchall()
        # elif data['levels'] == 'detailed':
        #     account= """AND aml.account_id IN %s""" if len(data['account_ids']) > 0 else """"""
        #     partner = """'AND aml.partner_id IN %s""" if len(data['partner_ids']) > 0 else """'"""
        #     state = """'AND aml.parent_state ='"""+str('posted') if data['target_move'] == 'posted' else """'"""
        #     query1 = """SELECT aml.account_id as account_id ,aa.name as account , aa.code as code,aml.name as name_aml,cc.name as currency,pp.name as partner,aml.partner_id as partner_id,aml.date as due_date,
        #                 aml.debit AS total_debit, aml.credit AS total_credit,aml.balance AS total_balance FROM account_move_line as aml
        #                          LEFT JOIN account_account aa ON aa.id = aml.account_id and aa.is_cash_flow = True
        #                          LEFT JOIN res_currency cc ON cc.id = aa.currency_id
        #                          LEFT JOIN res_partner pp ON pp.id = aml.partner_id
        #                          LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #                          WHERE aml.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(data['date_to']) +\
        #              """' AND aat.id='""" + str(account_type_id)  + state +partner+account+\
        #              """GROUP BY account,due_date,partner,currency,total_debit,total_credit,total_balance,name_aml,partner_id,account_id,code"""
        #     cr = self._cr
        #     tuples=()
        #     if len(data['account_ids']) > 0 and len(data["partner_ids"]) <=0:
        #         tuples=(tuple(data["account_ids"]),)
        #     elif len(data['account_ids']) <= 0 and len(data["partner_ids"]) >0:
        #         tuples=(tuple(data["partner_ids"]),)
        #     elif len(data['account_ids']) > 0 and len(data["partner_ids"]) >0:
        #         tuples=(tuple(data["partner_ids"]),tuple(data["account_ids"]))
        #     cr.execute(query1,tuples)
        #     fetched_data = cr.dictfetchall()
        #     # for account in self.env['account.account'].search([]):
        #     #     child_lines = self._get_journal_lines(account, data)
        #     #     if child_lines:
        #     #         journal_res.append(child_lines)
        #
        # else:
        #     account_type_id = self.env.ref('account.data_account_type_liquidity').id
        #     state = """AND am.state = 'posted' """ if data['target_move'] == 'posted' else ''
        #     sql = """SELECT DISTINCT aa.name,aa.code, sum(aml.debit) AS total_debit,
        #                              sum(aml.credit) AS total_credit FROM (SELECT am.* FROM account_move as am
        #                              LEFT JOIN account_move_line aml ON aml.move_id = am.id
        #                              LEFT JOIN account_account aa ON aa.id = aml.account_id and aa.is_cash_flow = True
        #                              LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #                              WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
        #         data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' """ + state + """) am
        #                                                  LEFT JOIN account_move_line aml ON aml.move_id = am.id
        #                                                  LEFT JOIN account_account aa ON aa.id = aml.account_id and aa.is_cash_flow = True
        #                                                  LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        #                                                  GROUP BY aa.name, aa.code"""
        #     cr = self._cr
        #     cr.execute(sql)
        #     fetched = cr.dictfetchall()
        #     for account in self.env['account.account'].search([]):
        #         child_lines = self._get_lines(account, data)
        #         if child_lines:
        #             account_res.append(child_lines)

        logged_users = self.env['res.company']._company_default_get('account.account')
        sheet = workbook.add_worksheet()
        bold = workbook.add_format({'align': 'center',
                                    'bold': True,
                                    'font_size': '10px',
                                    'border': 1,
                                    'bg_color': '#D3D3D3',})
        opening_balance = workbook.add_format({'align': 'center',
                                    'bold': True,
                                    'font_size': '10px',
                                    'border': 1,
                                    'bg_color':'yellow',})
        date = workbook.add_format({'font_size': '10px'})
        cell_format = workbook.add_format({'bold': True,
                                           'font_size': '10px'})
        head = workbook.add_format({'align': 'center',
                                    'bold': True,
                                    'bg_color': '#D3D3D3',
                                    'font_size': '15px',})
        txt = workbook.add_format({'align': 'left',
                                   'font_size': '10px'})
        txt_left = workbook.add_format({'align': 'left',
                                        'font_size': '10px',
                                        'border': 1})
        txt_center = workbook.add_format({'align': 'center',
                                          'font_size': '10px',
                                          'border': 1})
        amount = workbook.add_format({'align': 'right',
                                      'font_size': '10px',
                                      'border': 1})
        amount_bold = workbook.add_format({'align': 'right',
                                           'bold': True,
                                           'font_size': '10px',
                                           'border': 1})
        txt_bold = workbook.add_format({'align': 'left',
                                        'bold': True,
                                        'font_size': '10px',
                                        'border': 1})

        sheet.set_column('A:B',25, cell_format)
        sheet.set_column('D:I',25, cell_format)
        sheet.set_column('C:C', 40, cell_format)
        # sheet.set_column('F:F', 20, cell_format)
        sheet.write('F2', "Report Date", txt)
        sheet.write('E2', str(data['today']), txt)
        sheet.write('C2', logged_users.name, txt)
        sheet.merge_range('A3:G5', '')
        sheet.merge_range('A3:G4', 'CASH FLOW STATEMENTS', head)
        sheet.merge_range('A4:G4', '')

        if data['target_move'] == 'posted':
            sheet.write('E6', "Target Moves :", cell_format)
            sheet.write('E7', 'All Posted Entries', date)
        else:
            sheet.write('E6', "Target Moves :", cell_format)
            sheet.write('E7', 'All Entries', date)

        sheet.right_to_left()

        sheet.write('D6', "Date From", cell_format)
        sheet.write('C6', str(data['date_from']), date)
        sheet.write('D7', "Date To", cell_format)
        sheet.write('C7', str(data['date_to']), date)

        sheet.merge_range('A8:G8', '', head)
        sheet.write('A9', 'Date', bold)
        sheet.write('B9', 'Due Date', bold)
        sheet.write('C9', 'Label', bold)
        sheet.write('D9', 'Customers/Suppliers', bold)
        sheet.write('E9', 'Debit', bold)
        sheet.write('F9', 'Credit', bold)
        sheet.write('G9', 'Amount', bold)
        sheet.write('H9','Account Currency', bold)
        sheet.write('I9', 'Account', bold)

        row_num = 9
        col_num = 0
        previous_balance_list = previous_balance.copy()
        fetched_data_list = fetched_data.copy()
        account_res_list = account_res.copy()
        journal_res_list = fetched_data.copy()
        fetched_list = fetched.copy()
        before_balance=sum(i['total_debit']-i['total_credit'] for i in previous_balance_list)
        sheet.write('A10', '', opening_balance)
        sheet.write('B10', '', opening_balance)
        sheet.write('C10', '', opening_balance)
        sheet.write('D10', 'Opening Balance', opening_balance)
        sheet.write('E10', '', opening_balance)
        sheet.write('F10','', opening_balance)
        sheet.write('G10', "{:.2f}".format(before_balance), opening_balance)
        sheet.write('H10', '', opening_balance)
        sheet.write('I10', '', opening_balance)


        for i in fetched_data_list:
            if data['levels'] == 'summary':
                sheet.write(row_num + 1, col_num,str(datetime.strptime(str(i['date_aml']), '%Y-%m-%d').date()) if i['date_aml'] !=None else None, txt_left)
                sheet.write(row_num + 1, col_num+1,str(datetime.strptime(str(i['due_date']), '%Y-%m-%d').date()) if i['due_date'] !=None else None, txt_left)
                sheet.write(row_num + 1, col_num+2,i['name_aml'], txt_left)
                sheet.write(row_num + 1, col_num+3,i['partner'], txt_left)
                sheet.write(row_num + 1, col_num+4,str("{:.2f}".format(i['total_debit'])) , txt_left)
                sheet.write(row_num + 1, col_num+5,str("{:.2f}".format(i['total_credit'])), txt_left)
                sheet.write(row_num + 1, col_num+6,str("{:.2f}".format(before_balance+i['total_debit'] - i['total_credit'])), txt_left)
                sheet.write(row_num + 1, col_num+7,i['currency'], txt_left)
                sheet.write(row_num + 1, col_num+8,i['account'], txt_left)
                row_num = row_num + 1
                before_balance += i['total_debit'] - i['total_credit']
            # elif data['levels'] == 'consolidated':
            #     sheet.write(row_num + 1, col_num, i['name'], txt_left)
            #     sheet.write(row_num + 1, col_num + 1, str(i['total_debit']) + str(currency_symbol), amount)
            #     sheet.write(row_num + 1, col_num + 2, str(i['total_credit']) + str(currency_symbol), amount)
            #     sheet.write(row_num + 1, col_num + 3, str(i['total_debit'] - i['total_credit']) + str(currency_symbol),
            #                 amount)
            #     row_num = row_num + 1

        # accounts=[]
        # if data['levels'] == 'detailed':
        #     for account in self.env['account.account'].search([]):
        #                 total_debit=0
        #                 total_credit=0
        #                 total_balance=0
        #                 in_out_data=0
        #                 for l in fetched_data_list:
        #                     if l['account_id'] == account.id:
        #                         total_debit += l['total_debit']
        #                         total_credit += l['total_credit']
        #                         total_balance += l['total_debit'] - i['total_credit']
        #                         in_out_data +=1
        #
        #                 if in_out_data >= 1:
        #                     value={
        #                             'account_id':account.id,
        #                             'account':str(account.code) + str(account.name),
        #                             'currency':account.currency_id.name or '',
        #                             'debit':total_debit,
        #                             'credit':total_credit,
        #                             'balance':total_balance
        #                         }
        #                     accounts.append(value)
        #
        #     for account in accounts:
        #                 sheet.write(row_num + 1, col_num,'', txt_bold)
        #                 sheet.write(row_num + 1, col_num+1,'', txt_bold)
        #                 sheet.write(row_num + 1, col_num + 2, str(account['debit'])+ str(currency_symbol), amount_bold)
        #                 sheet.write(row_num + 1, col_num + 3, str(account['credit']) + str(currency_symbol), amount_bold)
        #                 sheet.write(row_num + 1, col_num + 4,
        #                             str(account['balance']) + str(currency_symbol), amount_bold)
        #
        #                 sheet.write(row_num + 1, col_num+5,account['currency'], txt_bold)
        #                 sheet.write(row_num + 1, col_num+6, str(account['account']), txt_bold)
        #                 row_num = row_num + 1
        #                 for l in fetched_data_list:
        #                     if l['account_id'] == account['account_id']:
        #                         sheet.write(row_num + 1, col_num,
        #                                     str(datetime.strptime(str(l['due_date']), '%Y-%m-%d').date()) if l[
        #                                                                                                          'due_date'] != None else None,
        #                                     txt_left)
        #                         sheet.write(row_num + 1, col_num + 1, l['partner'], txt_left)
        #                         sheet.write(row_num + 1, col_num + 2, str(l['total_debit']), txt_left)
        #                         sheet.write(row_num + 1, col_num + 3, str(l['total_credit']), txt_left)
        #                         sheet.write(row_num + 1, col_num + 4, str(l['total_debit'] - i['total_credit']), txt_left)
        #                         sheet.write(row_num + 1, col_num + 5, l['currency'], txt_left)
        #                         sheet.write(row_num + 1, col_num + 6, l['account'], txt_left)
        #
        #                         row_num = row_num + 1
        #
        # for j in account_res_list:
        #     for k in fetched_list:
        #         if k['name'] == j['account']:
        #             sheet.write(row_num + 1, col_num, str(k['code']) + str(k['name']), txt_bold)
        #             sheet.write(row_num + 1, col_num + 1, str(k['total_debit']) + str(currency_symbol), amount_bold)
        #             sheet.write(row_num + 1, col_num + 2, str(k['total_credit']) + str(currency_symbol), amount_bold)
        #             sheet.write(row_num + 1, col_num + 3,
        #                         str(k['total_debit'] - k['total_credit']) + str(currency_symbol), amount_bold)
        #             row_num = row_num + 1
        #     for l in j['journal_lines']:
        #         if l['account_name'] == j['account']:
        #             sheet.write(row_num + 1, col_num, l['name'], txt_left)
        #             sheet.write(row_num + 1, col_num + 1, str(l['total_debit']) + str(currency_symbol), amount)
        #             sheet.write(row_num + 1, col_num + 2, str(l['total_credit']) + str(currency_symbol), amount)
        #             sheet.write(row_num + 1, col_num + 3,
        #                         str(l['total_debit'] - l['total_credit']) + str(currency_symbol),
        #                         amount)
        #             row_num = row_num + 1
        #         for m in j['move_lines']:
        #             if m['name'] == l['name']:
        #                 sheet.write(row_num + 1, col_num, m['move_name'], txt_center)
        #                 sheet.write(row_num + 1, col_num + 1, str(m['total_debit']) + str(currency_symbol), amount)
        #                 sheet.write(row_num + 1, col_num + 2, str(m['total_credit']) + str(currency_symbol), amount)
        #                 sheet.write(row_num + 1, col_num + 3,
        #                             str(m['total_debit'] - m['total_credit']) + str(currency_symbol),
        #                             amount)
        #                 row_num = row_num + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()





    def _get_lines(self, account, data):
        account_type_id = self.env.ref('account.data_account_type_liquidity').id
        state = """AND am.state = 'posted' """ if data['target_move'] == 'posted' else ''
        query = """SELECT aml.account_id,aj.name, am.name as move_name, sum(aml.debit) AS total_debit, 
                         sum(aml.credit) AS total_credit FROM (SELECT am.* FROM account_move as am
                         LEFT JOIN account_move_line aml ON aml.move_id = am.id
                         LEFT JOIN account_account aa ON aa.id = aml.account_id
                         LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                         WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
            data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' """ + state + """) am
                                             LEFT JOIN account_move_line aml ON aml.move_id = am.id
                                             LEFT JOIN account_account aa ON aa.id = aml.account_id
                                             LEFT JOIN account_journal aj ON aj.id = am.journal_id
                                             WHERE aa.id = """ + str(account.id) + """
                                             GROUP BY am.name, aml.account_id, aj.name"""

        cr = self._cr
        cr.execute(query)
        fetched_data = cr.dictfetchall()

        sql2 = """SELECT aa.name as account_name, aj.id, aj.name, sum(aml.debit) AS total_debit,
                             sum(aml.credit) AS total_credit FROM (SELECT am.* FROM account_move as am
                                 LEFT JOIN account_move_line aml ON aml.move_id = am.id
                                 LEFT JOIN account_account aa ON aa.id = aml.account_id
                                 LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                                 WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
            data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' """ + state + """) am
                                                     LEFT JOIN account_move_line aml ON aml.move_id = am.id
                                                     LEFT JOIN account_account aa ON aa.id = aml.account_id
                                                     LEFT JOIN account_journal aj ON aj.id = am.journal_id
                                                     WHERE aa.id = """ + str(account.id) + """
                                                     GROUP BY aa.name, aj.name, aj.id"""

        cr = self._cr
        cr.execute(sql2)
        fetch_data = cr.dictfetchall()
        if fetched_data:
            return {
                'account': account.name,
                'code': account.code,
                'move_lines': fetched_data,
                'journal_lines': fetch_data,
            }

    def _get_journal_lines(self, account, data):
        account_type_id = self.env.ref('account.data_account_type_liquidity').id
        state = """AND am.state = 'posted' """ if data['target_move'] == 'posted' else ''
        sql2 = """SELECT aa.name as account_name, aj.id, aj.name, sum(aml.debit) AS total_debit,
             sum(aml.credit) AS total_credit FROM (SELECT am.* FROM account_move as am
                 LEFT JOIN account_move_line aml ON aml.move_id = am.id
                 LEFT JOIN account_account aa ON aa.id = aml.account_id
                 LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
                 WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
            data['date_to']) + """' AND aat.id='""" + str(account_type_id) + """' """ + state + """) am
                                     LEFT JOIN account_move_line aml ON aml.move_id = am.id
                                     LEFT JOIN account_account aa ON aa.id = aml.account_id
                                     LEFT JOIN account_journal aj ON aj.id = am.journal_id
                                     WHERE aa.id = """ + str(account.id) + """
                                     GROUP BY aa.name, aj.name, aj.id"""

        cr = self._cr
        cr.execute(sql2)
        fetched_data = cr.dictfetchall()
        if fetched_data:
            return {
                'account': account.name,
                'journal_lines': fetched_data,
            }

