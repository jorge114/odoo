# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - Datos utilizados cálculo de nómina',
    'summary': 'Agregar tres campos que complementen las percepciones  y deducciones actuales de la empresa',
    'description': '''
    * Agregar campo de apoyo, bono, viáticos y devolución de retención de INFONAVIT como percepción en contratos
    * Agregar campo de averias, fianza y descuento por contingencia como deducción
    * Agregar campo de gratificación en contratos
    ''',
    "website": "https://www.kuh7.mx/",
    'author': 'KUH7 SOLUCIONES S.A. de C.V.',
    'version': '1.1',
    'category': 'adicional_data',
    'depends': [
        'hr_contract',
        'nomina_cfdi_ee'],
    'data': [
        'views/hr_contract_view.xml',
    ],
    'installable': True,
    'application': False
}