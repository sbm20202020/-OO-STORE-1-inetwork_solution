from odoo import models


class egytaxcroncalculate(models.TransientModel):
    _name = 'egytax.cron'

    def calculate(self,*args):
        print ('ak')
        # contracts = self.env['hr.contract'].search([])
        # print 'start of calculate'
        # for contract in contracts:
        #     contract.clac_taxedsalary()
        #     print contract.name
        # print 'end of calculate'
