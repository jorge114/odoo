# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Contract(models.Model):
    _inherit = "hr.contract"
    
    tipo_semana = fields.Selection(
        selection=[('01', '6D trabajo / 1D descanso'), 
                   ('02', '5D trabajo / 2D descanso'),
                   ('03', '4D trabajo / 3D descanso'),],
        string=_('Tipo de semana'),
        default = '01'
    )
