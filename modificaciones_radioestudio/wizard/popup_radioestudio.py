# -*- coding: utf-8 -*-

from odoo import models, fields
import logging
import base64

_logger = logging.getLogger(__name__)

class PopupRadioestudio(models.TransientModel):
	_name = 'popup.radioestudio'

	fichero = fields.Binary(string = "Fichero")
	fichero_facturas = fields.Binary(string = 'Fichero facturas')
	fichero_descarga = fields.Binary(string = 'Fichero descarga')

	# Métodos para mostrar los diferentes popups
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

	def popup_pgc_radioestudio(self):
		wizard = self.env['popup.radioestudio'].create({})
		return {
			'name': 'Importar Plan General Contable',
			'view_mode': 'form',
			'view_id': self.env.ref('modificaciones_radioestudio.radioestudio_importar_pgc_report_wizard').id,
			'res_model': 'popup.radioestudio',
			'type': 'ir.actions.act_window',
			'res_id': wizard.id,
			'target': 'new'
		}

	def popup_facturas_radioestudio(self):
		wizard = self.env['popup.radioestudio'].create({})
		return {
			'name': 'Importar facturas',
			'view_mode': 'form',
			'view_id': self.env.ref('modificaciones_radioestudio.radioestudio_importar_facturas_report_wizard').id,
			'res_model': 'popup.radioestudio',
			'type': 'ir.actions.act_window',
			'res_id': wizard.id,
			'target': 'new'
		}

	def generar_fichero_cliente(self):
		texto = (base64.decodebytes(self.fichero)).decode('cp437')
		lineas = texto.splitlines()
		datosCliente = []
		for linea in lineas:
			cuenta = linea[0:10]
			nombre = linea[11:51].rstrip()
			direccion = (linea[82:84] + " " + linea[84:109].rstrip() + " " + linea[109:113].strip() + " " + linea[113:115].strip() + " " + linea[115:117].strip() + linea[117:119].strip()).strip()
			telefono = linea[56:66].rstrip()
			cif = linea[66:81].rstrip()
			cp = linea[51:56].lstrip()
			datosCliente.extend('"' + cuenta + '","' + nombre + '","' + direccion + '","' + telefono + '","' + cif + '","' + cp + '","' + cp + '","True"\n')

		datosFichero = "Cuenta a cobrar,Nombre,Calle,Teléfono,Tax ID,zip,Ubicación,Es una compañia\n"
		for dato in datosCliente:
			datosFichero += dato
		# Se guarda el contenido del fichero en una variable codificado en base64
		self.fichero_descarga = base64.b64encode(datosFichero.encode())

		# Abre una nueva pestaña que descarga el fichero recién generado
		return {
			'type': 'ir.actions.act_url',
			'url': '/web/content/popup.radioestudio/%s/fichero_descarga/%s?download=true' % (self.id, "Clientes.csv")
		}

	def generar_fichero_pgc(self):
		texto = (base64.decodebytes(self.fichero)).decode('cp437')
		lineas = texto.splitlines()
		datosPgc = []
		for linea in lineas:
			cuenta = linea[0:10]
			nombre = linea[11:51].rstrip()
			datosPgc.extend('"' + cuenta + '","' + nombre + '",asset_receivable,TRUE\n')

		datosFichero = "Código,Nombre de la cuenta,Tipo,Permitir conciliación\n"
		for dato in datosPgc:
			datosFichero += dato
		self.fichero_descarga = base64.b64encode(datosFichero.encode())

		return {
			'type': 'ir.actions.act_url',
			'url': '/web/content/popup.radioestudio/%s/fichero_descarga/%s?download=true' % (self.id, "PGC.csv")
		}

	empresa = "RADIOESTUDIO, S.A." # Se usa para generar las factura únicamente
	def generar_fichero_factura(self):
		vencimientos = self._get_vencimientos()
		lineasFactura = self._get_lineas_factura(vencimientos)
		datosFichero = "Empresa,Número,Partner,Fecha,Fecha de Factura/Recibo,Fecha de vencimiento,Diario,Apuntes contables/Cuenta,Líneas de factura/Producto,Líneas de factura/Etiqueta,Líneas de factura/Cuenta,Líneas de factura/Cantidad,Líneas de factura/Precio unitario,Líneas de factura/Impuestos\n"
		for dato in lineasFactura.values():
			datosFichero += dato
		self.fichero_descarga = base64.b64encode(datosFichero.encode())

		return {
			'type': 'ir.actions.act_url',
			'url': '/web/content/popup.radioestudio/%s/fichero_descarga/%s?download=true' % (self.id, "Facturas.csv")
		}


	# Devuelve un array con los vencimientos, donde el número de factura es la clave y el vencimiento el valor
	def _get_vencimientos(self):
		ficheroVencimientos = (base64.decodebytes(self.fichero_facturas)).decode('cp437')
		ficheroVencimientos = ficheroVencimientos.splitlines()
		vencimientos = dict()
		for linea in ficheroVencimientos:
			numero = linea[0:10]
			fecha = linea[14:18] + "-" + linea[12:14] + "-" + linea[10:12]
			vencimientos.update({numero: fecha})
		return vencimientos

	# Devuelve la línea con la información referente a la factura 
	def _get_datos_factura(self, linea, vencimientos):
		numero = linea[0:10]
		diario = self._get_diario(numero)
		if (numero[0:2] == '40'):
			numero = linea[0:4] + "/" + linea[4:6] + "/" + linea[6:10]
		partner = linea[84:134].rstrip()
		fechaFactura = linea[153:157] + "-" + linea[151:153] + "-" + linea[149:151] # aaaa-mm-dd | Campo "Fecha de Factura/Recibo" en el excel
		fechaContable = linea[80:84] + "-" + linea[78:80] + "-" + linea[76:78] # aaaa-mm-dd | Campo "Fecha" en el excel
		fechaVencimiento = ''
		# Esta comprobación no se puede hacer contra la variable "numero" porque si empieza por "40" se cambia y ya no coincidiría
		if linea[0:10] in vencimientos:
			fechaVencimiento = vencimientos[linea[0:10]]
		return '"' + self.empresa + '","' + numero + '","' + partner + '","' + fechaFactura + '","' + fechaContable + '","' + fechaVencimiento + '","' + diario + '"'

	def _get_diario(self, numeracion):
		if (numeracion[0:4] == "40MS"):
			return "Facturas 40 Madrid Sur"
		elif (numeracion[0:3] == "DMN"):
			return "Facturas Dial Madrid Norte"
		elif (numeracion[0:3] == "DMS"):
			return "Facturas Dial Madrid Sur"
		elif (numeracion[0:3] == "SMN"):
			return "Facturas Ser Madrid Norte"
		elif (numeracion[0:3] == "SMS"):
			return "Facturas Ser Madrid Sur"
		elif (numeracion[0:3] == "WMN"):
			return "Facturas Web Madrid Norte"
		elif (numeracion[0:3] == "WMS"):
			return "Facturas Web Madrid Sur"
		elif (numeracion[0:4] == "OSMN"):
			return "Facturas Otros Servicios Madrid Norte"
		elif (numeracion[0:4] == "OSMS"):
			return "Facturas Otros Servicios Madrid Sur"
		elif (numeracion[0:3] == "SBA"):
			return "Facturas Servicios Badajoz"
		elif (numeracion[0:3] == "SPL"):
			return "Facturas Servicios Plasencia"
		elif (numeracion[0:4] == "VPIN"):
			return "Facturas Varios Pinto"
		elif (numeracion[0:3] == "COP"):
			self.empresa = "CROMATEL MULTIMEDIA, S.L."
			return "Facturas Coplaco"
		elif (numeracion[0:3] == "IND"):
			self.empresa = "INICIATIVAS PARA EL DESARROLLO DE LA COMUNICACIÓN, S.A."
			return "Facturas Indesco"
		elif (numeracion[0:3] == "MAS"):
			self.empresa = "MÁS RADIO, S.A."
			return "Facturas Mas Radio"

	def _get_lineas_factura(self, vencimientos):
		movimientos = (base64.decodebytes(self.fichero)).decode('cp437')
		movimientos = movimientos.splitlines()
		numeroFactura = ""
		datosFactura = ""
		datosProducto = ""
		datosDevolver = dict()
		productoGuardado = False
		impuestos = {'2': 'IVA 10% (Servicios)', '3': 'IVA 21% (Servicios)', '4': 'IVA 4% (Servicios)', '5': 'IVA Exento Repercutido Sujeto', '7': 'IVA 5%'}
		recargos = {'1': '0.50% Recargo Equivalencia Ventas', '2': '1.4% Recargo Equivalencia Ventas' , '3': '5.2% Recargo Equivalencia ventas'} # No se usan los recargos

		for linea in movimientos:
			
			if numeroFactura == "":
				numeroFactura = linea[0:10]
				datosFactura = self._get_datos_factura(linea, vencimientos)
			elif numeroFactura != linea[0:10]:
				productoGuardado = False
				datosFactura = datosFactura + datosProducto
				# Comprobación necesaria para evitar que haya líneas que no tengan bien cerradas las comillas
				if datosFactura[len(datosFactura)-1] != '"':
					datosFactura = datosFactura + '"\n'
				else:
					datosFactura = datosFactura + '\n'
				datosDevolver.update({numeroFactura: datosFactura})
				numeroFactura = linea[0:10]
				datosFactura = self._get_datos_factura(linea, vencimientos)
				datosProducto = ''

			tipoLinea = linea[10:13]
			if "IET" in tipoLinea:
				cuentaCliente = linea[16:26]
			if "BE" in tipoLinea: # Producto
				if datosProducto != '':
					productoGuardado = True
					datosFactura = datosFactura + datosProducto
					if datosFactura[len(datosFactura)-1] != '"':
						datosFactura = datosFactura + '"\n'
					else:
						datosFactura = datosFactura + '\n'
					datosProducto = ',,,,,,,'
				else:
					datosProducto = ',"' + cuentaCliente + '"'
				nombreProducto = linea[54:75].rstrip()
				etiquetaProducto = linea[28:38].rstrip()
				cuentaProducto = linea[16:26]
				precioProducto = int(linea[38:54].lstrip()) / 100
				datosProducto = datosProducto + ',"' + nombreProducto + '","' + etiquetaProducto + '","' + cuentaProducto + '",1,"' + str(precioProducto) + '"' # La colma al principio se pone porque continua los datos de la factura
				# En caso de que el impuesto sea el "5" no hay línea de impuesto, pero hay que añadirlo porque se trata de un IVA exento
				if linea[12:13] == '5':
					datosProducto = datosProducto + ',"IVA Exento Repercutido Sujeto"'
				cuentaCliente = ''

			elif "CE" in tipoLinea: # IVA
				if datosProducto != '':
					try:
						if datosProducto[len(datosProducto)-1] != '"':
							datosProducto = datosProducto + ',' + impuestos[tipoLinea[2]]
						else:
							datosProducto = datosProducto + ',"' + impuestos[tipoLinea[2]]
					except KeyError as e:
						_logger.info("IVA no encontrado: " + tipoLinea[2])
				else:
					_logger.info("IVA sin producto? " + linea)

				if productoGuardado:
					datosFactura = datosFactura[:-1] + ',"' + impuestos[tipoLinea[2]] + '"\n'

			elif tipoLinea == "RET": # Retención
				if datosProducto != '':
					if linea[13:14] != '-':
						if datosProducto[len(datosProducto)-1] != '"':
							datosProducto = datosProducto + ',Retenciones a cuenta 19% (Arrendamientos)'
						else:
							datosProducto = datosProducto + ',"Retenciones a cuenta 19% (Arrendamientos)'
				else:
					_logger.info('Retención sin producto? ' + linea)

			elif "RE" in tipoLinea: # Recargo de equivalencia. No se usa
				if datosProducto != '':
					try:
						if datosProducto[len(datosProducto)-1] != '"':
							datosProducto = datosProducto + ',' + recargos[tipoLinea[2]]
						else:
							datosProducto = datosProducto + ',"' + recargos[tipoLinea[2]]
					except KeyError as e:
						_logger.info('Recargo no encontrado: ' + tipoLinea[2])
				else:
					_logger.info('Recargo sin producto? ' + linea)

		datosFactura = datosFactura + datosProducto
		if datosFactura[len(datosFactura)-1] != '"':
			datosFactura = datosFactura + '"\n'
		else:
			datosFactura = datosFactura + '\n'
		datosDevolver.update({numeroFactura: datosFactura})
		return datosDevolver