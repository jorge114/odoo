# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    loan_request = fields.Integer(default=100)

