# -*- coding: utf-8 -*-
from odoo import http


class TraduccionesRadioestudio(http.Controller):
    @http.route('/traducciones_radioestudio/traducciones_radioestudio', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/traducciones_radioestudio/traducciones_radioestudio/objects', auth='public')
    def list(self, **kw):
        return http.request.render('traducciones_radioestudio.listing', {
            'root': '/traducciones_radioestudio/traducciones_radioestudio',
            'objects': http.request.env['traducciones_radioestudio.traducciones_radioestudio'].search([]),
        })

    @http.route('/traducciones_radioestudio/traducciones_radioestudio/objects/<model("traducciones_radioestudio.traducciones_radioestudio"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('traducciones_radioestudio.object', {
            'object': obj
        })
