# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError



class MaintenanceStage(models.Model):
    _inherit = 'maintenance.request'

    contact_name=fields.Char(String='Contact')
    symptoms_description = fields.Char(String='Symptoms description ')
    assessment_performed = fields.Char(String='Assessment performed ')
    observations = fields.Char(String='Observations ')
    assessment_results = fields.Char(String='Assessment results and conclusions ')
    recommendations_further= fields.Char(String='Recommendations and Further Actions ')
    quantity=fields.Float(default='1')
    initial_amount= fields.Float(string='Entitled Amount')
    partner_id=fields.Char(string='Customer')
    service = fields.Char("service")

    @api.constrains('initial_amount')
    def not_minus_initial_amount(self):
        for rec in self:
            if rec.initial_amount < 0:
                raise ValidationError('Entitled Amount should not minus. or 0')

    end_user_name = fields.Char(String='End User Name ')
    issue_problem = fields.Char(String='Issue/Problem Description ')
    defective_part_number = fields.Char(String='Defective Part Number')
    defective_serial_number = fields.Char(String='Defective Serial Number ')
    replacement_part_number = fields.Char(String='Replacement Part Number')
    replacement_serial_number = fields.Char(String='Replacement Serial Number ')
    purchase_date=fields.Date('Purchase Date')
    end_user_date=fields.Date('Date End user Obtained Replacement')
    service_request_number=fields.Char('Service Request Number')
    rma_number=fields.Char('RMA Number')
    serial = fields.Char(String='Serial',required=1)

    @api.constrains("purchase_date", "end_user_date", )
    def _check_dates_id(self):
        for rec in self:
            if rec.purchase_date:
                if rec.purchase_date < fields.Date.from_string(fields.Date.today()):
                    raise ValidationError(("You should select date in Purchase Date  Greater than Today Date "))

            if rec.end_user_date:
                if rec.end_user_date < fields.Date.from_string(fields.Date.today()):
                    raise ValidationError(("You should select date in Date End user Obtained Replacement  Greater than Today Date "))


    @api.constrains('quantity')
    def quantity_not_minus(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError('Please enter a positive number in Quantity')

    total_price=fields.Float(compute='calc_total_price')


    @api.depends('product_ids.lst_price')
    def calc_total_price(self):
        total=0.0
        for rec in self:
            for line in rec.product_ids:
                total+=line.lst_price
            rec.total_price=total










