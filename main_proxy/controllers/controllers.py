# -*- coding: utf-8 -*-
# from odoo import http


# class ./apps/walkProxy/mainProxy(http.Controller):
#     @http.route('/./apps/walk_proxy/main_proxy/./apps/walk_proxy/main_proxy/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/./apps/walk_proxy/main_proxy/./apps/walk_proxy/main_proxy/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('./apps/walk_proxy/main_proxy.listing', {
#             'root': '/./apps/walk_proxy/main_proxy/./apps/walk_proxy/main_proxy',
#             'objects': http.request.env['./apps/walk_proxy/main_proxy../apps/walk_proxy/main_proxy'].search([]),
#         })

#     @http.route('/./apps/walk_proxy/main_proxy/./apps/walk_proxy/main_proxy/objects/<model("./apps/walk_proxy/main_proxy../apps/walk_proxy/main_proxy"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('./apps/walk_proxy/main_proxy.object', {
#             'object': obj
#         })
