# -*- encoding: utf-8 -*-
{
    'name': "KUH7 - Reporte de incidencias y gestión de generación de periodo nómina",
    'version': '1.0',
    'depends': ['nomina_cfdi_ee'],
    'website': 'https://www.kuh7.mx',
    'author': "JOSÉ MARÍA HERIBERTO ALVARADO SOLÓRZANO",
    'category': 'Report',
    'description': """
    Este módulo servirá para generar reporte de incidencias que se tuvieron los empleados durante el periodo de nómina para incidencias de Faltas, Incapacidades, Vacaciones, Dias festivos, Retardos y Horas Extra, se genera un reporte por incidencia,
    además, adición de parametros para el correcto cálculo de la nómina.
    """,
    'data': [
        'reports/reporte_incidencia_h_e.xml',
        'reports/reporte_incidencias_df.xml',
        'reports/reporte_incidencias_faltas.xml',
        'reports/reporte_incidencias_inc.xml',
        'reports/reporte_incidencias_ret.xml',
        'reports/reporte_incidencias_vac.xml',
        'views/hr_payslip_run_view.xml'
    ],
}