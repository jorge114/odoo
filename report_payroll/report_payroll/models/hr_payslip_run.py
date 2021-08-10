# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    first_payslip_month = fields.Boolean(string="First payslip of month")