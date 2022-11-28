# <?xml version="1.0" encoding="utf-8"?>

from odoo import models, fields, api, _
import datetime
from datetime import datetime


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    basic_salary=fields.Float(compute='get_salarires')
    allownce=fields.Float(compute='get_salarires')
    transportation=fields.Float(compute='get_salarires')
    overtime=fields.Float(compute='get_salarires')
    bouns = fields.Float(compute='get_salarires')
    net_salary=fields.Float(compute='get_salarires')

    social_insurance=fields.Float(compute='get_salarires')
    medical_insurnace=fields.Float(compute='get_salarires')
    phone_allownace=fields.Float(compute='get_salarires')
    martyrs_families=fields.Float(compute='get_salarires')
    payroll_tax = fields.Float(compute='get_salarires')
    loan_pdf = fields.Float(compute='get_salarires')
    installment=fields.Float(compute='get_salarires')
    pn_amount=fields.Float(compute='get_salarires')
    total_amount=fields.Float(compute='get_salarires')

    @api.depends('line_ids')
    def get_salarires(self):

        basic_salary=0.0
        allownce=0.0
        transpot=0.0
        overtime=0.0
        net_salary=0.0
        social_insurance=0.0
        medical_insurnace=0.0
        phone_allownace=0.0
        martyrs_families=0.0

        payroll_tax=0.0
        loan=0.0
        installment=0.0
        pn_amount=0.0
        bouns=0.0
        total_amount=0.


        for rec in self:
            for line in rec.line_ids:
                if line.category_id.code=='BASIC' or line.code=='BASIC':
                    basic_salary+=line.amount

                if line.category_id.code=='ALS' or line.code=='ALS':
                    allownce+=line.amount

                if line.category_id.code == 'TRA' or line.code == 'TRA':
                    transpot += line.amount

                if line.category_id.code == 'OCOVT' or line.code == 'OCOVT' or  line.code == 'COVT' :
                    overtime += line.amount

                if line.category_id.code == 'SIE' or line.code == 'SIE'  :
                    social_insurance += line.amount

                if line.category_id.code == 'MI' or line.code == 'MI' :
                    medical_insurnace += line.amount

                if line.category_id.code == 'PHA' or line.code == 'PHA'  :
                    phone_allownace += line.amount

                if line.category_id.code == 'MFP' or line.code == 'MFP'  :
                    martyrs_families += line.amount

                if line.category_id.code == 'IT' or line.code == 'IT'  :
                    payroll_tax += line.amount

                if line.category_id.code == 'LO' or line.code == 'LO'  or  line.code == 'loan' :
                    loan += line.amount
                if line.category_id.code == 'INS' or line.code == 'INS'  :
                    installment += line.amount

                if line.category_id.code == 'PN' or line.code == 'PN':
                    pn_amount += line.amount


            rec.basic_salary= basic_salary
            rec.allownce=allownce
            rec.transportation=transpot
            rec.overtime=overtime
            rec.bouns = bouns
            rec.net_salary =rec.basic_salary + rec.allownce +  rec.transportation + rec.overtime + rec.bouns
            rec.social_insurance = social_insurance
            rec.medical_insurnace = medical_insurnace
            rec.phone_allownace = phone_allownace
            rec.martyrs_families = martyrs_families
            rec.payroll_tax = payroll_tax
            rec.loan_pdf = loan
            rec.installment = installment
            rec.pn_amount = pn_amount

            rec.total_amount = rec.social_insurance + rec.medical_insurnace + rec.phone_allownace + rec.martyrs_families + rec.payroll_tax + rec.loan_pdf + rec.installment + rec.pn_amount












