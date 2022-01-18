# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Etiquetas(models.Model):
    _inherit = "res.partner"

    numero_proveedor = fields.Char(string="Número Proveedor")
    numero_cliente = fields.Char(string="Número Cliente")