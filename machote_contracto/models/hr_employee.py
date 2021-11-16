# -*- coding:utf-8 -*-

from odoo import api, fields, models


class DatosContrato(models.Model):
    _inherit = 'hr.employee'

    calle = fields.Char(string="", required=False, )
    numero = fields.Char(string="", required=False, )
    colonia = fields.Char(string="", required=False, )
    ciudad = fields.Char(string="", required=False, )
    estado_mx = fields.Char(string="", required=False, )
    codigo_postal = fields.Char(string="", required=False, )