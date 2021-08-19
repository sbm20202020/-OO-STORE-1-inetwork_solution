# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceStage(models.Model):
    _inherit = 'maintenance.request'

    contact_name=fields.Char(String='Customer Contact Name')
    symptoms_description = fields.Char(String='Symptoms description ')
    assessment_performed = fields.Char(String='Assessment performed ')
    observations = fields.Char(String='Observations ')
    assessment_results = fields.Char(String='Assessment results and conclusions ')
    recommendations_further= fields.Char(String='Recommendations and Further Actions ')
    quantity=fields.Float(default='1')
    initial_amount= fields.Float(string='Entitled Amount')
    partner_id=fields.Many2one('res.partner',string='Customer')
    service = fields.Char("service ")

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


    total_price=fields.Float(compute='calc_total_price')

    @api.depends('product_ids.lst_price')
    def calc_total_price(self):
        total=0.0
        for rec in self:
            for line in rec.product_ids:
                total+=line.lst_price
            rec.total_price=total










