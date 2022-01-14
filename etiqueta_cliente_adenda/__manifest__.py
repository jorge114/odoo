# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - Etiqueta para adenda',
    'summary': 'KUH7 - Dealba Custom',
    'description': '''
        En el rubro de Contactos de clientes y proveedores se requiere 
        dentro de la informacion general una etiqueta donde pueda colocarse 
        Numero de proveedor otra para Numero de cliente, este numero tendra 
        que verse reflejado en los datos de la factura, adicional desarrollar 
        el rubro de adenda.
    ''',
    "website": "https://www.kuh7.mx/",
    'author': 'KUH7 SOLUCIONES S.A. de C.V.',
    'version': '1.0',
    'category': 'Dealba',
    'depends': [
        'account_accountant',
    ],
    'data': [
        'views/etiquetas_cliente.xml',
    ],
}
