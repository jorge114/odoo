# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('no_empleado')
    def onchange_payroll_number(self):
        self.no_employee = self.no_empleado

    @api.onchange('no_employee')
    def onchange_payroll_number_two(self):
        self.no_empleado = self.no_employee

    @api.model
    def create(self, vals):
        rfc_obj = self.env['hr.employee'].search([('company_id', '=', vals['company_id']), ('rfc', '=', vals['rfc'])])
        if rfc_obj:
            raise UserError(_("El empleado " + rfc_obj.name + " ha sido dado de alta anteriormente con el rfc "
                              + vals['rfc']))

        seq_obj = self.env['ir.sequence'].search([('company_id', '=', self.company_id.id)])
        next_number = seq_obj.next_by_code('sequence.no.employee')
        vals['no_empleado'] = next_number
        vals['no_employee'] = next_number
        return super(HrEmployee, self).create(vals)
