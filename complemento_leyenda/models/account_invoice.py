# -*- coding: utf-8 -*-

from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = 'account.move'
	
    leyenda = fields.Boolean(string='Leyenda', default=False)

    @api.model
    def to_json(self):
        res = super(AccountMove,self).to_json()

        if self.leyenda:
           res.update({
                'leyenda': {
                      'disposicionfiscal': self.company_id.disposicionfiscal,
                      'norma': self.company_id.norma,
                      'textoleyenda': self.company_id.textoleyenda,
                }})
        return res
