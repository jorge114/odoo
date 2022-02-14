# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from num2words import num2words


class ReportePersonalizado(models.Model):
    _inherit = 'account.move'

    def _companyLetraMayuscula(self):
        company = self.company_id.name
        MAY_company = company.upper()
        return MAY_company

    def _direccion_company(self):
        direccion = self.company_id.street_name
        MAY_direccion = direccion.upper()
        return MAY_direccion

    def _direccion_company2(self):
        direccion3 = self.company_id.street_number + self.company_id.street2
        MAY_direccion3 = direccion3.upper()
        return MAY_direccion3

    def _direccion2_company(self):
        direccion2 = 'C.P. ' + self.company_id.zip + ' ' + self.company_id.city + ', ' + self.company_id.state_id.name
        MAY_direccion2 = direccion2.upper()
        return MAY_direccion2

    def _RFC_company(self):
        rfc = 'R.F.C. ' + self.company_id.vat
        MAY_rfc = rfc.upper()
        return MAY_rfc

    def _telefono_company(self):
        telefono = '+52 ' + self.company_id.phone
        MAY_telefono = telefono.upper()
        return MAY_telefono

    def _correo_company(self):
        correo = self.company_id.email + '    '
        return correo

    def _website_company(self):
        website = self.company_id.website
        return website

    def _company_register(self):
        register = self.company_id.company_registry
        return register
