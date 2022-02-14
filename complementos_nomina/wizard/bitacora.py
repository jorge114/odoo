# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Bitacora(models.TransientModel):
    _name = 'bitacora'

    detalle_ids = fields.One2many(
        comodel_name='bitacora.detalles',
        inverse_name='bitacora_id',
        string='Detalles'
    )


class BitacoraDetalles(models.TransientModel):
    _name = 'bitacora.detalles'

    bitacora_id = fields.Many2one(
        comodel_name='bitacora',
        string='Bitacora',
    )
    number = fields.Char(string='Referencia')
    no_empleado = fields.Char(string='No. Empleado')
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='No. Empleado',
    )
    error_bitacora = fields.Char(string='Error')