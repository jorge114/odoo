# -*- coding: utf-8 -*-
##############################################################################
#                 @author IT Admin
#
##############################################################################

{
    'name': 'Complemento Leyenda CFDI 3.3',
    'version': '14.1',
    'description': ''' Agrega información de Leyendas al CFDI 3.3
    ''',
    'category': 'Accounting', 'Sales'
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'base', 'account', 'cdfi_invoice'
    ],
    'data': [
        'views/res_company_view.xml',
        'views/account_invoice_view.xml',
        'report/invoice_report.xml',
    ],
    'application': False,
    'installable': True,
}
