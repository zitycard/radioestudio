# -*- coding: utf-8 -*-
{
	"name": "Modificaciones Radioestudio",
	"summary": "Personaliza el odoo a las necesidades de Radioestudio",
	"description": "Añade las funcionalidades requeridas por Radioestudio.",
	"author": "Zitycard",
	"website": "https://zitycard.com",
	"version": "0.1",
	"depends": ["base", "account_accountant"],
	"data": [
		"views/radioestudio.xml",
		"wizard/popup_radioestudio.xml",
		"security/security.xml",
		"security/ir.model.access.csv"
	]
}