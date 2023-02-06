# -*- coding: utf-8 -*-

from odoo import models, fields, api


class traducciones_radioestudio(models.Model):
    _name = 'traducciones_radioestudio.traducciones_radioestudio'
    _description = 'traducciones_radioestudio.traducciones_radioestudio'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100
