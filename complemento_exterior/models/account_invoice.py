# -*- coding: utf-8 -*-

import base64
import json
import requests
import datetime
from lxml import etree

from odoo import fields, models, api,_ 
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, Warning
from odoo.tools import float_is_zero, float_compare
from reportlab.graphics.barcode import createBarcodeDrawing, getCodes
from reportlab.lib.units import mm

import logging
_logger = logging.getLogger(__name__)

class InfoSerieMercancias(models.Model):
    _name = 'account.move.mercancias.series'
    _rec_name = "cce_numeroserie"

    cce_numeroserie = fields.Char(string='Número de serie')	
    order_id = fields.Many2one('account.move.mercancias.info', string='Serie', ondelete='cascade', index=True, copy=False)

class InfoMercancias(models.Model):
    _name = 'account.move.mercancias.info'
    _rec_name = "nombre"

    nombre = fields.Char(string='Nombre')
    cce_marca = fields.Char(string='Marca')
    cce_modelo = fields.Char(string='Modelo')
    cce_submodelo = fields.Char(string='SubModelo')
    cce_series = fields.One2many('account.move.mercancias.series', 'order_id', 'Series Mercancias',
        copy=True, readonly=False,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    info_mercancias = fields.Many2one('account.move.mercancias.info', string='Información mercancia')

class AccountMove(models.Model):
    _inherit = 'account.move'

    cce_habilitar_cee = fields.Boolean(string='Habilitar comercio exterior')
    cce_tipooperacion = fields.Selection([('2', '2')], string='Tipo de operación')
    cce_clavedepedimento = fields.Selection([('A1', 'A1')], string='Clave de pedimento')
    cce_certificadoorigen = fields.Selection([('0', '0 - No Funge como certificado de origen'), ('1', '1- Funge como certificado origen')], string='Certificado origen')
    cce_numcertificadoorigen = fields.Char(string=_('Folio del certificado de origen'))
    cce_numeroexportadorconfiable = fields.Char(string=_('Número de exportador confiable'))
    cce_incoterm = fields.Selection(
        selection=[('CFR', 'CFR - Coste y flete (ppuerto de destino convenido)'), 
                   ('CIF', 'CIF - Coste, seguro y flete (puerto de destino convenido)'), 
                   ('CPT', 'CPT - Transporte pagado hasta (el lugar de destino convenido)'),
                   ('CIP', 'CIP - Transporte y seguro pagados hasta (lugar de destino convenido)'), 
                   ('DAF', 'DAF - Entregada en frontera (lugar convenido)'),
                   ('DAP', 'DAP - Entregada en lugar'), 
                   ('DAT', 'DAT - Entregada en terminal'), 
                   ('DES', 'DES - Entregada sobre buque (puerto de destino convenido)'), 
                   ('DEQ', 'DEQ - Entregada en muelle (puerto de destino convenido)'), 
                   ('DDU', 'DDU - Entregada derechos no pagados (lugar de destino convenido)'), 
                   ('DDP', 'DDP - Entregada derechos pagados (lugar de destino convenido)'),				   
                   ('EXW', 'EXW - En fábrica (lugar convenido)'), 
                   ('FCA', 'FCA - Franco transportista (lugar designado)'), 
                   ('FAS', 'FAS - Franco al costado del buque (puerto de carga convenido)'), 
                   ('FOB', 'FOB - Franco a bordo (puerto de carga convenido)'),],
        string=_('INCOTERM'),
    )
    cce_subdivision = fields.Selection([('0', '0')], string='Subdivisión')
#    cce_tipocambiousd = fields.Float(string='Tipo de cambio USD', compute='_compute_total_usd', digits=dp.get_precision('Product Price'))
#    cce_totalusd = fields.Float(string='Total USD', compute='_compute_total_usd', digits=dp.get_precision('Product Price'))
    cce_motivo_traslado = fields.Selection(
        selection=[('01', 'Envío de mercancias facturadas con anterioridad'), 
                   ('02', 'Reubicación de mercancías propias'), 
                   ('03', 'Envío de mercancías objeto de contrato de consignación'),
                   ('04', 'Envío de mercancías para posterior enajenación'), 
                   ('05', 'Envío de mercancías propiedad de terceros'),
                   ('99', 'Otros'),],
        string=_('Motivo de traslado'),
    )
    cee_propietario_id = fields.Many2one('res.partner', string='Propietario')


    @api.model
    def to_json(self):
        res = super(AccountMove,self).to_json()
        mxn = self.env["res.currency"].search([('name', '=', 'MXN')], limit=1)
        usd = self.env["res.currency"].search([('name', '=', 'USD')], limit=1)
        curr_rate = round(usd.with_context(date=self.invoice_date).rate,6) / round(self.currency_id.with_context(date=self.invoice_date).rate,6)

        if self.cce_habilitar_cee:
                res.update({
                     'comercioexterior11': {
                            'TipoOperacion': self.cce_tipooperacion,
                            'ClaveDePedimento': self.cce_clavedepedimento,
                            'CertificadoOrigen': self.cce_certificadoorigen,
                            'NumeroExportador': self.cce_numeroexportadorconfiable,
                            'Incoterm': self.cce_incoterm,
                            'Subdivision': self.cce_subdivision,
                            'TipoCambioUSD': self.set_decimals(1 / (round(usd.with_context(date=self.invoice_date).rate,6)) + 0.000001, self.currency_id.no_decimales_tc),
                            'MotivoTraslado': self.cce_motivo_traslado,
                            'TotalUSD': self.amount_total, 
                            'Emisor': {
                                'Curp': self.company_id.cce_curp,
                                'Domicilio': {
                                   'Calle': self.company_id.cce_calle,
                                   'NumeroExterior': self.company_id.cce_no_exterior,
                                   'NumeroInterior': self.company_id.cce_no_interior,
                                   'Colonia': self.company_id.cce_clave_colonia.c_colonia,
                                   'Localidad': self.company_id.cce_clave_localidad.c_localidad,
                                   'Municipio': self.company_id.cce_clave_municipio.c_municipio,
                                   'Estado': self.company_id.cce_clave_estado.c_estado,
                                   'Pais': self.company_id.cce_clave_pais.c_pais,
                                   'CodigoPostal': self.company_id.zip,
                                   'cce_referencia': self.company_id.cce_referencia,
                                },
                             },
                            'Receptor': {
                                'Domicilio': {
                                   'Calle': self.partner_id.cce_calle,
                                   'NumeroExterior': self.partner_id.cce_no_exterior,
                                   'NumeroInterior': self.partner_id.cce_no_interior,
                                   'Colonia': self.partner_id.cce_clave_colonia.c_colonia,
                                   'Localidad': self.partner_id.cce_clave_localidad.c_localidad,
                                   'Municipio': self.partner_id.cce_clave_municipio.c_municipio,
                                   'Estado': self.partner_id.cce_clave_estado.c_estado,
                                   'Pais': self.partner_id.cce_clave_pais.c_pais,
                                   'CodigoPostal': self.partner_id.zip,
                                },
                             },
                            'Mercancias': '',
                     },
                })
                if self.cee_propietario_id:
                     res.update({'Propietario': {
                                           'NumRegIdTrib': self.cee_propietario_id.registro_tributario,
                                           'ResidenciaFiscal': self.cee_propietario_id.residencia_fiscal,
                                           },
                                        })

                mercancia_cce = []
                series_len = 0
                total_usd = 0.0
                for merc in self.invoice_line_ids:
                   aux_marca = False
                   aux_modelo = False
                   aux_submodelo = False
                   serie_mercancia = []
                   if merc.info_mercancias:
                      for info in merc.info_mercancias:
                          aux_marca = info.cce_marca
                          aux_modelo = info.cce_modelo
                          aux_submodelo = info.cce_submodelo
                          if info.cce_series:
                             for serie in info.cce_series:
                                 serie_mercancia.append({'serie': serie.cce_numeroserie,})
                             series_len =  len(info.cce_series)
                   if series_len > 0:
                      if series_len != merc.cantidadaduana:
                          raise UserError(_('No son iguales el número de series registradas en Información mercancia que la cantidad de productos registrados en aduana'))
                   _logger.info('numero series %s', series_len)
                   price_unit = round(curr_rate * merc.price_unit,2)  #self.currency_id._convert(merc.price_unit, usd, self.company_id, self.invoice_date)
                   mercancia_cce.append({
                            'NoIdentificacion': self.clean_text(merc.product_id.code),
                            'FraccionArancelaria': merc.product_id.fraccionarancelaria.c_fraccionarancelaria,
                            'CantidadAduana': merc.quantity,
                            'ValorUnitarioAduana': price_unit, #self.currency_id._convert(merc.price_unit, usd, self.company_id, self.invoice_date),
                            'ValorDolares': round(price_unit * merc.quantity,2), #(self.currency_id._convert(merc.price_subtotal, usd, self.company_id, self.invoice_date)) ,
                            'UnidadAduana': merc.product_id.unidadAduana.c_unidadmedidaaduana,
                            'Marca': aux_marca,
                            'Modelo': aux_modelo,
                            'SubModelo': aux_submodelo,
                            'NumeroSerie': serie_mercancia,
                            'NumeroSerie2': series_len,
                   })
                   total_usd += round(price_unit * merc.quantity,2) #(self.currency_id._convert(merc.price_subtotal, usd, self.company_id, self.invoice_date) )
                if mercancia_cce:
                    #cce_mercancias = {'numerodepartidas': len(self.invoice_line_ids)}
                    #cce_mercancias.update({'cce_mercancias_lista': mercancia_cce})
                    res['comercioexterior11'].update({'Mercancias': mercancia_cce}) #res.update({'Mercancias': mercancia_cce})
                res['comercioexterior11'].update({'TotalUSD': self.set_decimals(total_usd, 2)})
        return res

