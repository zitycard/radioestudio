# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class PopupRadioestudio(models.TransientModel):
	_name = 'popup.radioestudio'

	fichero = fields.Binary(string = "Fichero")

	def popup_clientes_radioestudio(self):
		wizard = self.env['popup.radioestudio'].create({})
		return {
			'name': 'Importar cliente',
			'view_mode': 'form',
			'view_id': self.env.ref('modificaciones_radioestudio.radioestudio_importar_clientes_report_wizard').id,
			'res_model': 'popup.radioestudio',
			'type': 'ir.actions.act_window',
			'res_id': wizard.id,
			'target': 'new'
		}

	def generar_fichero_cliente(self):
		_logger.info("Entra")