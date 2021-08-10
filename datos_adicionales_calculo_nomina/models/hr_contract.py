# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrContract(models.Model):
    _inherit = 'hr.contract'

    breakdowms = fields.Float(string="Breakdowns ($)", default=0.00)
    viatics = fields.Float(string="Viactics ($)", default=0.00)
    bond = fields.Float(string="Bond ($)", default=0.00)
    info_withholding_refund = fields.Float(string="INFONAVIT withholding refund ($)", default=0.00)
    support = fields.Float(string="Support ($)", default=0.00)
    bail = fields.Float(string="Bail ($)", default=0.00)
    contingency_descount = fields.Float(string="Contingency descount ($)", default=0.00)
    dominical_bonus = fields.Float(string="Dominical bonus ($)", default=0.00)
    vacation_bonus = fields.Float(string="Vacation bonus", default=0.0)
    personal_loan = fields.Float(string="Personal Loan ($)", default=0.00)
    gratification = fields.Float(string="Gratification", default=0.00)