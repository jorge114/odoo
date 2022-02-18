# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Datos(models.Model):
    _inherit = ["purchase.order"]



    street_id = fields.Many2one(
        comodel_name='res.partner',
        string="Direccion de Entrega",
        domain=[('type', '=', 'delivery')]
    )

    requisicion = fields.Char('Requisición')

    contacto = fields.Many2one(
        comodel_name='res.users',
        string='En atención a:',

    )

    transporte = fields.Char("Tipo de Transporte")

    uso = fields.Selection(selection=[('01','Acabados'),
                   ('02','Planta'),
                   ('03','Almacen Partes'),
                   ('04','Calidad'),
                   ('05','Producto Terminado'),
                   ('06','Mantenimiento'),
                   ('07','Horno'),
        ], string='Uso/Destino'
    )

