# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fouls_employee_ids = fields.One2many('faltas.nomina', 'employee_id', string='Fouls Payroll', readonly=True)
    vacations_ids = fields.One2many('vacaciones.nomina', 'employee_id', string='Vacation Payroll', readonly=True)
    aditional_hour_ids = fields.One2many('horas.nomina', 'employee_id', string='Aditional Hours Payroll', readonly=True)
    delays_ids = fields.One2many('retardo.nomina', 'employee_id', string='Delays Payroll', readonly=True)
    inability_ids = fields.One2many('incapacidades.nomina', 'employee_id', string='Inability Payroll', readonly=True)
    holidays_days_ids = fields.One2many('dias.feriados', 'employee_id', string='Holiday Days Payroll', readonly=True)