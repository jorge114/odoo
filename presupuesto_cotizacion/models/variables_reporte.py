# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ReportePresupuesto(models.Model):
    _inherit = 'sale.order'


