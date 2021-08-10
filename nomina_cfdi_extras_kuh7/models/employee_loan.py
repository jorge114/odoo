# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class employee_loan(models.Model):
    _inherit = 'employee.loan'

    @api.depends('start_date', 'term')
    def _get_end_date(self):
        for loan in self:
            if loan.start_date and loan.loan_type_id:
                periodo_de_pago = self.loan_type_id.periodo_de_pago or ''
                start_date = self.start_date

                if periodo_de_pago == 'Semanal':
                    end_date = start_date + relativedelta(weeks=self.term) - relativedelta(days=1)
                elif periodo_de_pago == 'Quincenal':
                    end_date = self.get_quincenal_end_date(start_date, loan.term)
                else:
                    end_date = start_date + relativedelta(months=self.term)

                loan.end_date = end_date.strftime("%Y-%m-%d")
            else:
                loan.end_date = datetime.today().strftime("%Y-%m-%d")
