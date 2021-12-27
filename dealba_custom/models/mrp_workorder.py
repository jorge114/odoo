# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    @api.depends('workcenter_id', 'variacion_ids')
    def _compute_secuencia_dealba(self):
        for record in self:
            secuencia_id = record.workcenter_id.secuencia_id
            if secuencia_id:
                prefijo = secuencia_id.prefix if secuencia_id.prefix else ""
                numero = secuencia_id.number_next_actual
                variacion = ""
                for variacion_id in record.variacion_ids:
                    variacion = "{0}/{1}".format(variacion, variacion_id.codigo)
                sufijo = secuencia_id.suffix
                record.secuencia_dealba = "{0}{1}{2} - {3}".format(prefijo, numero, variacion, sufijo)

    secuencia_dealba = fields.Char(
        string='Secuencia Dealba:',
        compute='_compute_secuencia_dealba',
    )
    variacion_ids = fields.Many2many(
        comodel_name='variacion',
        string='Variaciones:',
    )

    def action_generate_serial(self):
        self.ensure_one()
        self.finished_lot_id = self.env['stock.production.lot'].create({
            'name': self.secuencia_dealba,
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
        })
        self.workcenter_id.secuencia_id.number_next_actual += 1
