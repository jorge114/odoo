# -*- coding:utf-8 -*-

from odoo import api, fields, models


class MachoteContrato(models.Model):
    _inherit = 'hr.contract'

    tipo_contracto = fields.Char(string="", required=False, )
    edad_empleado = fields.Integer(string="", required=False, )
    tiempo_contracto = fields.Char(string="", required=False, )
    testigo1 = fields.Char(string="", required=False, )
    testigo2 = fields.Char(string="", required=False, )

    def _puesto_trabajo(self):
        puesto_trabajo = self.job_id.name
        puesto_trabajo_out = puesto_trabajo.upper()
        return puesto_trabajo_out

    def _nombre_empleado(self):
        empleado = self.name
        empleado_out = empleado.upper()
        return empleado_out
