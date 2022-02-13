# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class HrLocations(models.Model):

    _name='hr.location'
    _rec_name='name'

    name=fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', size=64,copy=False)


    # override create function to add sequence code
    # remove sequence and make field editable (task mm-10)

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].next_by_code('hr.location.code')
    #     return super(HrLocations, self).create(vals)