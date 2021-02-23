# -*- coding: utf-8 -*-
from odoo import http

# class PoVariant(http.Controller):
#     @http.route('/po_variant/po_variant/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/po_variant/po_variant/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('po_variant.listing', {
#             'root': '/po_variant/po_variant',
#             'objects': http.request.env['po_variant.po_variant'].search([]),
#         })

#     @http.route('/po_variant/po_variant/objects/<model("po_variant.po_variant"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('po_variant.object', {
#             'object': obj
#         })