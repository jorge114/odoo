# -*- coding: utf-8 -*-

import json
import base64

from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def to_json(self):
        res = super(HrPayslip, self).to_json()

        # ******** NUEVO XML ********
        # emisor_rfc = str(base64.b64encode(bytes(res['emisor']['rfc'], 'utf-8')))
        # emisor_nombre = str(base64.b64encode(bytes(res['emisor']['nombre_fiscal'], 'utf-8')))
        # receptor_rfc = str(base64.b64encode(bytes(res['receptor']['rfc'], 'utf-8')))
        # receptor_nombre = str(base64.b64encode(bytes(res['receptor']['nombre'], 'utf-8')))
        # concepto_dsc = str(base64.b64encode(bytes(res['conceptos']['descripcion'], 'utf-8')))
        # percepciones = res['percepciones']['lineas_de_percepcion_excentas']
        # percepciones.extend(res['percepciones']['lineas_de_percepcion_grabadas'])
        #
        # nuevo_xml = {'localizacion-mx': {
        #     'Login': {
        #         'rfc': self.company_id.vat,
        #         'clave': self.company_id.contrasena,
        #     },
        #     'Documento': {
        #         'Operacion': 'TIMBRAR',
        #         'TipoDocumento': 'NOMINA',
        #         'Comprobante': {
        #             'Version': '3.3',
        #             'Folio': res['factura']['folio'],
        #             'Fecha': res['factura']['fecha_factura'].replace(' ', 'T'),
        #             'Sello': '',  # que valor pongo aqui??
        #             'FormaPago': res['factura']['forma_pago'],
        #             'NoCertificado': '',  # que valor pongo aqui??
        #             'Certificado': '',  # que valor pongo aqui??
        #             'CfdiRelacionados': {
        #                 'CfdiRelacionado': {
        #                     'UUID': '',  # que valor pongo aqui??
        #                 },
        #                 'TipoRelacion': '04',  # que valor pongo aqui??
        #             },
        #             'Moneda': res['factura']['moneda'],
        #             'TipoDeComprobante': res['factura']['tipocomprobante'],
        #             'MetodoPago': res['factura']['metodo_pago'],
        #             'LugarExpedicion': res['factura']['LugarExpedicion'],
        #             'SubTotal': res['factura']['subtotal'],
        #             'Descuento': res['factura']['descuento'],
        #             'Total': res['factura']['total'],
        #             'Emisor': {
        #                 'Rfc': emisor_rfc[2:len(emisor_rfc)-1],
        #                 'Nombre': emisor_nombre[2:len(emisor_nombre)-1],
        #                 'RegimenFiscal': res['factura']['RegimenFiscal'],
        #             },
        #             'Receptor': {
        #                 'Rfc': receptor_rfc[2:len(receptor_rfc)-1],
        #                 'Nombre': receptor_nombre[2:len(receptor_nombre)-1],
        #                 'UsoCFDI': res['receptor']['uso_cfdi'],
        #             },
        #             'Complemento': {
        #                 'TimbreFiscaldigital': {
        #                     'TimbreFiscaldigital': '',  # que valor pongo aqui??
        #                     'FechaTimbrado': '',  # que valor pongo aqui??
        #                     'NoCertificadoSAT': '',  # que valor pongo aqui??
        #                     'RfcProvCertif': '',  # que valor pongo aqui??
        #                     'SelloCFD': '',  # que valor pongo aqui??
        #                     'SelloSAT': '',  # que valor pongo aqui??
        #                     'UUID': '',  # que valor pongo aqui??
        #                     'Version': '',  # que valor pongo aqui??
        #                 },
        #                 'Pagos': {
        #                     'Version': '',  # que valor pongo aqui??
        #                 },
        #             },
        #             'Conceptos': {
        #                 'Concepto': {
        #                     'ClaveProdServ': res['conceptos']['ClaveProdServ'],
        #                     'NoIdentificacion': '',  # que valor pongo aqui??
        #                     'Cantidad': res['conceptos']['cantidad'],
        #                     'ClaveUnidad': res['conceptos']['cantidad'],
        #                     'Descripcion': concepto_dsc[2:len(concepto_dsc)-1],
        #                     'ValorUnitario': res['conceptos']['valorunitario'],
        #                     'Importe': res['conceptos']['importe'],
        #                     'Descuento': res['conceptos']['descuento'],
        #                 },
        #             },
        #             'Complementos': {
        #                 'Nomina12': {
        #                     'Version': '1.2',  # que valor pongo aqui??
        #                     'TipoNomina': res['nomina12']['TipoNomina'],
        #                     'FechaPago': res['nomina12']['FechaPago'],
        #                     'FechaInicialPago': res['nomina12']['FechaInicialPago'],
        #                     'FechaFinalPago': res['nomina12']['FechaFinalPago'],
        #                     'NumDiasPagados': res['nomina12']['NumDiasPagados'],
        #                     'PeriodicidadPago': res['nomina12Receptor']['PeriodicidadPago'],
        #                     'TotalPercepciones': res['nomina12']['TotalPercepciones'],
        #                     'TotalDeducciones': res['nomina12']['TotalDeducciones'],
        #                     'TotalOtrosPagos': res['nomina12']['TotalOtrosPagos'],
        #                     'Receptor': {
        #                         'Curp': res['nomina12Receptor']['Curp'],
        #                         'NumSeguridadSocial': res['nomina12Receptor']['NumSeguridadSocial'],
        #                         'FechaInicioRelLaboral': res['nomina12Receptor']['FechaInicioRelLaboral'],
        #                         'Antiguedad': res['nomina12Receptor']['Antiguedad'],
        #                         'TipoContrato': res['nomina12Receptor']['TipoContrato'],
        #                         'Sindicalizado': 'No',  # que valor pongo aqui??
        #                         'TipoJornada': res['nomina12Receptor']['TipoJornada'],
        #                         'TipoRegimen': res['nomina12Receptor']['TipoRegimen'],
        #                         'NumEmpleado': res['nomina12Receptor']['NumEmpleado'],
        #                         'Departamento': res['nomina12Receptor']['Departamento'],
        #                         'Puesto': res['nomina12Receptor']['Puesto'],
        #                         'SalarioBaseCotApor': res['nomina12Receptor']['SalarioBaseCotApor'],
        #                         'SalarioDiarioIntegrado': res['nomina12Receptor']['SalarioDiarioIntegrado'],
        #                         'ClaveEntFed': res['nomina12Receptor']['ClaveEntFed'],
        #                     },
        #                     'Percepciones': {
        #                         'TotalSueldos': res['percepciones']['Totalpercepcion']['TotalSueldos'],
        #                         'TotalGravado': res['percepciones']['Totalpercepcion']['TotalGravado'],
        #                         'TotalExento': res['percepciones']['Totalpercepcion']['TotalExento'],
        #                         'Percepcion': percepciones,
        #                     },
        #                     'Deducciones': {
        #                         'Deduccion': res['deducciones']['lineas_de_deduccion'],
        #                         'TotalImpuestosRetenidos': res['deducciones']['TotalDeduccion']['TotalImpuestosRetenidos'],
        #                         'TotalOtrasDeducciones': res['deducciones']['TotalDeduccion']['TotalOtrasDeducciones'],
        #                     },
        #                 },
        #             },
        #         },
        #     }
        # }}
        #
        # if int(res['otros_pagos']['no_otros_pagos']) > 0:
        #     nuevo_xml.update({
        #         'OtrosPagos': {  # si no tiene otros pagos, que valor pongo aqui??
        #             'OtroPago': {
        #                 'TipoOtroPago': res['otros_pagos']['otros_pagos'][0]['TipoOtrosPagos'],
        #                 'Clave': res['otros_pagos']['otros_pagos'][0]['TipoOtrosPagos'],
        #                 'Concepto': res['otros_pagos']['otros_pagos'][0]['Concepto'],
        #                 'Importe': res['otros_pagos']['otros_pagos'][0]['ImporteGravado'],
        #                 'SubsidioAlEmpleo': {
        #                     'SubsidioCausado': res['otros_pagos']['otros_pagos'][0]['SubsidioCausado'],
        #                 }
        #             }
        #         },
        #     })
        # else:
        #     nuevo_xml.update({
        #         'OtrosPagos': {  # si no tiene otros pagos, que valor pongo aqui??
        #             'OtroPago': {
        #                 'TipoOtroPago': '',
        #                 'Clave': '',
        #                 'Concepto': '',
        #                 'Importe': '',
        #                 'SubsidioAlEmpleo': {
        #                     'SubsidioCausado': '',
        #                 }
        #             }
        #         },
        #     })
        #
        # print('******** INICIO NUEVO XML ********')
        # print(json.dumps(nuevo_xml, indent=4, sort_keys=True))
        # print('******** FIN NUEVO XML ********')

        # ******** FIN NUEVO XML ********

        return res