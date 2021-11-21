# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError,UserError
import difflib
import calendar


class UpdateInputPathWizard(models.Model):
    _name = 'update.input.path.wizard'
    employee_ids =fields.Many2many('hr.employee','hr_employee_update_relation','employee_update_column1','employee_update_column2',)
    position_ids=fields.Many2many('hr.job','hr_job_update_relation','job_update_column1','job_update_column2')
    depart_ids=fields.Many2many('hr.department','hr_department_update_relation','depart_update_column1','depart_update_column2')
    contract_state=fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Contract State')
    company_id=fields.Many2one('res.company','Company')


    @api.onchange('position_ids','depart_ids')
    def emp_depart_position(self):
        #this method add automated fields to retrive values in worked days and input in payslip based on fields filter in wizard
        res={}
        domain=[]
        if self.position_ids and len(self.depart_ids.ids) == 0:
            domain=[('job_id','in',self.position_ids.ids)]

        if self.depart_ids and len(self.position_ids.ids) == 0:
            domain=[('department_id','in',self.depart_ids.ids)]
        if self.depart_ids and self.position_ids:
            domain=[('department_id','in',self.depart_ids.ids),('job_id','in',self.position_ids.ids)]
        res['domain'] ={'employee_ids':domain}
        return res


    date_from=fields.Date(required=True)
    date_to=fields.Date(required=True)

    @api.constrains('date_from','date_to')
    def _date_constrians(self):
        for l in self:
            if l.date_from != False and l.date_to != False and l.date_from > l.date_to :
                raise ValidationError("Date from is n't greater than Date to")

    def action_create_update_input(self):
        payslip=[]
        if self.company_id.id == False and self.contract_state == False and len(self.employee_ids.ids) == 0 and len(self.position_ids.ids) == 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),])
        elif self.company_id.id != False and self.contract_state != False and len(self.employee_ids.ids) > 0  and len(self.position_ids.ids) > 0 and len(self.depart_ids.ids)>0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('contract_id.state','=',self.contract_state),('employee_id','in',self.employee_ids._ids),
                ('employee_id.job_id','in',self.position_ids._ids),('employee_id.department_id','in',self.depart_ids._ids),('employee_id.company_id','=',self.company_id.id)])
        elif self.company_id.id == False and self.contract_state !=False and len(self.employee_ids.ids) > 0 and len(self.position_ids.ids) > 0 and len(self.depart_ids.ids)>0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('contract_id.state','=',self.contract_state),('employee_id','in',self.employee_ids._ids),
                ('employee_id.job_id','in',self.position_ids._ids),('employee_id.department_id','in',self.depart_ids._ids)])
        elif self.company_id.id == False and self.contract_state == False and len(self.employee_ids.ids) > 0 and len(self.position_ids.ids) > 0 and len(self.depart_ids.ids)>0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('employee_id','in',self.employee_ids._ids),('employee_id.job_id','in',self.position_ids._ids),('employee_id.department_id','in',self.depart_ids._ids)])
        elif self.company_id.id == False and self.contract_state == False and len(self.employee_ids.ids) == 0 and len(self.position_ids.ids) > 0 and len(self.depart_ids.ids)>0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('employee_id.job_id','in',self.position_ids._ids),('employee_id.department_id','in',self.depart_ids._ids)])
        elif self.company_id.id == False and self.contract_state == False and len(self.employee_ids.ids) == 0 and len(self.position_ids.ids) == 0 and len(self.depart_ids.ids)>0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),('employee_id.department_id','in',self.depart_ids._ids)])
        elif self.company_id.id ==False and self.contract_state==False and len(self.employee_ids.ids) == 0 and len(self.position_ids.ids) > 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('employee_id.job_id','in',self.position_ids._ids)])
        elif self.company_id.id==False and self.contract_state==False and len(self.employee_ids.ids) > 0 and len(self.position_ids.ids) == 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
               ('employee_id','in',self.employee_ids._ids),])
        elif self.company_id.id==False and self.contract_state!=False and len(self.employee_ids.ids) == 0 and len(self.position_ids.ids) == 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('contract_id.state','=',self.contract_state)])
        elif self.company_id.id != False and self.contract_state==False and len(self.employee_ids.ids) == 0 and len(self.position_ids.ids) == 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                        ('employee_id.company_id','=',self.company_id.id)])
        elif self.company_id.id != False and self.contract_state != False and len(self.employee_ids.ids) == 0  and len(self.position_ids.ids) == 0 and len(self.depart_ids.ids) == 0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('contract_id.state','=',self.contract_state),('employee_id.company_id','=',self.company_id.id)])
        elif self.company_id.id != False and self.contract_state == False and len(self.employee_ids.ids) == 0  and len(self.position_ids.ids) > 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('employee_id.job_id','in',self.position_ids._ids),('employee_id.company_id','=',self.company_id.id)])
        elif self.company_id.id != False and self.contract_state == False and len(self.employee_ids.ids) == 0 and len(
                self.position_ids.ids) == 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('employee_id.department_id', 'in', self.depart_ids._ids), ('employee_id.company_id', '=', self.company_id.id)])
        elif self.company_id.id != False and self.contract_state == False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) == 0 and len(self.depart_ids.ids) == 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                ('employee_id', 'in', self.employee_ids._ids),('employee_id.company_id', '=', self.company_id.id)])
        elif self.company_id.id == False and self.contract_state != False and len(self.employee_ids.ids) == 0  and len(self.position_ids.ids) > 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('contract_id.state','=',self.contract_state),('employee_id.job_id','in',self.position_ids._ids)])
        elif self.company_id.id == False and self.contract_state != False and len(self.employee_ids.ids) == 0  and len(self.position_ids.ids) == 0 and len(self.depart_ids.ids)>0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('contract_id.state','=',self.contract_state),('employee_id.department_id','in',self.depart_ids._ids)])
        elif self.company_id.id == False and self.contract_state != False and len(self.employee_ids.ids) > 0  and len(self.position_ids.ids) == 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                ('contract_id.state','=',self.contract_state),('employee_id','in',self.employee_ids._ids),])

        elif self.company_id.id == False and self.contract_state == False and len(self.employee_ids.ids) > 0  and len(self.position_ids.ids) > 0 and len(self.depart_ids.ids)==0 :
              payslip=self.env['hr.payslip'].search([('state','=','draft'),('date_from','>=',self.date_from),('date_to','<=',self.date_to),
                    ('employee_id','in',self.employee_ids._ids),('employee_id.job_id','in',self.position_ids._ids)])

        elif self.company_id.id == False and self.contract_state == False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) == 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                ('employee_id', 'in', self.employee_ids._ids),('employee_id.department_id', 'in', self.depart_ids._ids),])
        elif self.company_id.id != False and self.contract_state != False and len(self.employee_ids.ids) == 0 and len(
                self.position_ids.ids) > 0 and len(self.depart_ids.ids) == 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state),
                 ('employee_id.job_id', 'in', self.position_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        elif self.company_id.id != False and self.contract_state != False and len(self.employee_ids.ids) == 0 and len(
                self.position_ids.ids) == 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state),
                 ('employee_id.department_id', 'in', self.depart_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        elif self.company_id.id != False and self.contract_state != False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) == 0 and len(self.depart_ids.ids) ==0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state), ('employee_id', 'in', self.employee_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        elif self.company_id.id != False and self.contract_state == False and len(self.employee_ids.ids) == 0 and len(
                self.position_ids.ids) > 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('employee_id.job_id', 'in', self.position_ids._ids),
                 ('employee_id.department_id', 'in', self.depart_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        elif self.company_id.id != False and self.contract_state == False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) > 0 and len(self.depart_ids.ids) == 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('employee_id', 'in', self.employee_ids._ids),
                 ('employee_id.job_id', 'in', self.position_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        elif self.company_id.id != False and self.contract_state == False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) == 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                ('employee_id', 'in', self.employee_ids._ids),
                 ('employee_id.department_id', 'in', self.depart_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        elif self.company_id.id == False and self.contract_state != False and len(self.employee_ids.ids) == 0 and len(
                self.position_ids.ids) > 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state),
                 ('employee_id.job_id', 'in', self.position_ids._ids),
                 ('employee_id.department_id', 'in', self.depart_ids._ids),])

        elif self.company_id.id == False and self.contract_state != False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) > 0 and len(self.depart_ids.ids) == 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state), ('employee_id', 'in', self.employee_ids._ids),
                 ('employee_id.job_id', 'in', self.position_ids._ids),])

        elif self.company_id.id == False and self.contract_state != False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids)== 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state), ('employee_id', 'in', self.employee_ids._ids),
                 ('employee_id.department_id', 'in', self.depart_ids._ids),])

        elif self.company_id.id != False and self.contract_state != False and len(self.employee_ids.ids) == 0 and len(
                self.position_ids.ids) > 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state),
                 ('employee_id.job_id', 'in', self.position_ids._ids),
                 ('employee_id.department_id', 'in', self.depart_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        elif self.company_id.id != False and self.contract_state != False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) > 0 and len(self.depart_ids.ids) == 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state), ('employee_id', 'in', self.employee_ids._ids),
                 ('employee_id.job_id', 'in', self.position_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        elif self.company_id.id != False and self.contract_state != False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) == 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('contract_id.state', '=', self.contract_state), ('employee_id', 'in', self.employee_ids._ids),
                 ('employee_id.department_id', 'in', self.depart_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])
        elif self.company_id.id != False and self.contract_state == False and len(self.employee_ids.ids) > 0 and len(
                self.position_ids.ids) > 0 and len(self.depart_ids.ids) > 0:
            payslip = self.env['hr.payslip'].search(
                [('state','=','draft'),('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                 ('employee_id', 'in', self.employee_ids._ids),
                 ('employee_id.job_id', 'in', self.position_ids._ids),
                 ('employee_id.department_id', 'in', self.depart_ids._ids),
                 ('employee_id.company_id', '=', self.company_id.id)])

        all_update_create=[]

        fields_all = {}
        other_input = self.env['hr.payslip.input.type'].search([('input_path','=',True)])
        for input in other_input:
            f_name='x_'+str(input.id)
            fields_exit = self.env['ir.model.fields'].sudo().search([('name','=',f_name),('model_id','=',self.env['ir.model'].search([('name','=','update.input.path')]).id,)])
            if fields_exit.id == False :
                    fielda=self.env['ir.model.fields'].sudo().create({'name':'x_'+str(input.id),
                                                               'field_description':input.name,
                                                               'model_id':self.env['ir.model'].search([('name','=','update.input.path')]).id,
                                                               'ttype':'float',
                                                               'relation': False,
                                                               'required': False,
                                                               'store': True,
                                                               'index':True,
                                                               'copied':False,

                                                                      })

                    inherit_id = self.env.ref('update_input_path.update_input_path_view_tree_new')
                    arch_base = _('<?xml version="1.0"?>'
                                  '<data>'
                                  '<field name="%s" position="%s" >'
                                  '<field name="%s" attrs="%s" width="%s" optional="%s"/>'
                                  '</field>'
                                  '</data>') % ('employee_id','after','x_'+str(input.id),{"readonly":[("state","=","confirm")]},"300px","show")
                    fielda=self.env['ir.ui.view'].sudo().create({'name': 'update.input.path',
                                                          'type': 'tree',
                                                          'model': 'update.input.path',
                                                          'mode': 'extension',
                                                          'inherit_id': inherit_id.id,
                                                          'arch_base': arch_base,
                                                          'active': True,
                                                          })


        work_entry = self.env['hr.work.entry.type'].search([('appear_on_payslip', '=', True)])
        for work_days in work_entry:
            f_name_days='x_'+str(work_days.id)+'_days'
            fields_exit_days= self.env['ir.model.fields'].sudo().search([('name','=',f_name_days),('model_id','=',self.env['ir.model'].search([('name','=','update.input.path')]).id,)])
            f_name_hours='x_'+str(work_days.id)+'_hours'
            fields_exit_hours= self.env['ir.model.fields'].sudo().search([('name','=',f_name_hours),('model_id','=',self.env['ir.model'].search([('name','=','update.input.path')]).id,)])
            inherit_id = self.env.ref('update_input_path.update_input_path_view_tree_new')
            if fields_exit_days.id == False :
                    self.env['ir.model.fields'].sudo().create({'name':'x_'+str(work_days.id)+'_days',
                                                               'field_description':work_days.name+'-days',
                                                               'model_id':self.env['ir.model'].search([('name','=','update.input.path')]).id,
                                                               'ttype':'float',
                                                               'relation': False,
                                                               'required': False,
                                                               'store': True,
                                                               'index':True,
                                                               'copied':False,

                                                               })
                    arch_base2 = _('<?xml version="1.0"?>'
                                   '<data>'
                                   '<field name="%s" position="%s">'
                                   '<field name="%s" attrs="%s" width="%s" optional="%s"/>'
                                   '</field>'
                                   '</data>') % (
                                 'employee_id', 'after', 'x_' + str(work_days.id) + '_days',{"readonly":[("state","=","confirm")]},"300px","show")
                    self.env['ir.ui.view'].sudo().create({'name': 'worked_days',
                                                          'type': 'tree',
                                                          'model': 'update.input.path',
                                                          'mode': 'extension',
                                                          'inherit_id': inherit_id.id,
                                                          'arch_base': arch_base2,
                                                          'active': True})
            if fields_exit_hours.id == False:
                    self.env['ir.model.fields'].sudo().create(
                        {'name': 'x_' +str(work_days.id)+'_hours',
                         'field_description':work_days.name +'-hours',
                         'model_id': self.env['ir.model'].search([('name', '=', 'update.input.path')]).id,
                         'ttype': 'float',
                         'relation': False,
                         'required': False,
                         'store': True,
                         'index': True,
                         'copied': False,
                         })
                    arch_base = _('<?xml version="1.0"?>'
                                  '<data>'
                                  '<field name="%s" position="%s">'
                                  '<field name="%s" attrs="%s" width="%s" optional="%s"/>'
                                  '</field>'
                                  '</data>') % ('employee_id','after','x_'+str(work_days.id)+'_hours',{"readonly":[("state","=","confirm")]},"300px","show")
                    self.env['ir.ui.view'].sudo().create({'name': 'worked_hours',
                                                          'type': 'tree',
                                                          'model': 'update.input.path',
                                                          'mode': 'extension',
                                                          'inherit_id': inherit_id.id,
                                                          'arch_base': arch_base,
                                                          'active': True})

        for pay in payslip:
            month=pay.date_to.strftime('%m')
            for work_days in pay.worked_days_line_ids:
               employee_work_entry=self.env['employee.work'].search([('employee_id','=',pay.employee_id.id)
                        ,('state','=','confirm'),('work_entry_type_id','=',work_days.work_entry_type_id.id)
                        ,('date', '>=', pay.date_from), ('date', '<=', pay.date_to),('type','=','work_entry_type')])
               num_hours=0
               num_days=0
               if employee_work_entry:
                   for entry in employee_work_entry:
                       num_days +=entry.number_of_days
                       num_hours +=entry.number_of_hours
                   fields_all.update({
                       'x_' + str(work_days.work_entry_type_id.id) + '_hours': num_hours,
                       'x_' + str(work_days.work_entry_type_id.id) + '_days':num_days,
                   })
               else:
                   if work_days.work_entry_type_id.code == 'WORK100':
                       fields_all.update({
                           'x_' + str(work_days.work_entry_type_id.id) + '_days': 30
                       })
                   else:
                       fields_all.update({
                           'x_' + str(work_days.work_entry_type_id.id) + '_hours': work_days.number_of_hours,
                           'x_' + str(work_days.work_entry_type_id.id) + '_days': work_days.number_of_days,
                       })
            for input in pay.input_line_ids:
                employee_work_input = self.env['employee.work'].search([('employee_id', '=', pay.employee_id.id)
                                 , ('state', '=', 'confirm'), ('input_type_id', '=',input.input_type_id.id)
                                     , ('date', '>=', pay.date_from), ('date', '<=', pay.date_to),
                                            ('type', '=', 'input_type')])
                amount=0
                if employee_work_input:
                    for input in employee_work_input:
                        amount += input.amount
                    fields_all.update({
                        'x_' + str(input.input_type_id.id): amount,
                    })

                else:
                    fields_all.update({
                        'x_' + str(input.input_type_id.id): input.amount,
                    })

            update=[]
            search_path=self.env['update.input.path'].search([('payslip','=',pay.id)])
            if search_path:
                search_path.write(fields_all)
                update=search_path
            else:
                fields_all.update({
                    'employee_id': pay.employee_id.id,
                    'payslip': pay.id,
                    'date': pay.date_to,
                    'state': 'draft',
                    'month': month,
                })
                update=self.env['update.input.path'].create(fields_all)
            for i in update:
                all_update_create.append(i.id)

        return {
            'domain':[('id','in',all_update_create)],
            'name': _("Update Input Path"),
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': False,
            'views': [(self.env.ref('update_input_path.update_input_path_view_tree_new').id, 'tree'),
                      (self.env.ref('update_input_path.update_input_path_view_search_new').id, 'search'), ],
            'res_model': 'update.input.path',
            'type': 'ir.actions.act_window',
            'target': 'line',
            'nodestroy': True,
            'context':{'search_default_state':'draft'}
        }




