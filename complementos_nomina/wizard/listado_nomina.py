# -*- coding: utf-8 -*-

import io
import xlsxwriter
import base64
import pytz
import json

from datetime import date
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError


class ListadoNomina(models.TransientModel):
    _name = 'listado.nomina'

    payslip_run_ids = fields.Many2many(
        comodel_name='hr.payslip.run',
        string='Procesamientos de nóminas',
    )
    file_data = fields.Binary(string='Archivo')

    def generar_reporte_listado_nomina(self):
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = wb.add_worksheet('Listado de nómina')
        ws2 = wb.add_worksheet('Listado por departamento')

        text_bold_left_title = wb.add_format({
            'font_size': '15',
            'align': 'left',
            'font_name': 'Arial'
        })
        text_bold_left_subtitle = wb.add_format({
            'font_size': '12.5',
            'align': 'center',
            'font_name': 'Arial'
        })
        total_style = wb.add_format({
            'font_size': '12.5',
            'align': 'right',
            'font_name': 'Arial'
        })
        text_bold_left_paragrah = wb.add_format({
            'font_size': '8',
            'align': 'left',
            'font_name': 'Arial'
        })
        text_bold_center_paragrah = wb.add_format({
            'font_size': '8',
            'align': 'center',
            'font_name': 'Arial'
        })
        money_format = wb.add_format({
            'num_format': '$#,##0.00',
            'font_size': '10',
            'align': 'right',
            'font_name': 'Arial'
        })
        font_format = wb.add_format({
            'font_size': '10',
            'align': 'left',
            'font_name': 'Arial'
        })
        font_format2 = wb.add_format({
            'font_size': '10',
            'align': 'center',
            'font_name': 'Arial'
        })
        font_format_h = wb.add_format({
            'font_size': '10',
            'font_name': 'Arial',
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'pattern': 1,
            'bg_color': '#fcf991',
            'left': 1,
            'right': 1,
            'top': 2,
            'bottom': 2,
            'border_color': 'blue',
        })

        tz_mx = pytz.timezone('America/Mexico_City')
        now = datetime.now(tz_mx)
        today = date.today()
        fch_inicial = sorted(self.payslip_run_ids.mapped('date_start'))[0]
        fch_final = sorted(self.payslip_run_ids.mapped('date_end'), reverse=True)[0]
        period = 'Periodo del {0} al {1}'.format(
            fch_inicial.strftime('%d/%m/%Y'),
            fch_final.strftime('%d/%m/%Y'),
        )
        nombre_companias = ' - '.join(self.payslip_run_ids.mapped('company_id').mapped('name'))
        nombre_nominas = ' - '.join(self.payslip_run_ids.mapped('name'))
        ws.write(0, 0, nombre_companias, text_bold_left_title)
        ws2.write(0, 0, nombre_companias, text_bold_left_title)
        ws.write(1, 2, nombre_nominas, text_bold_left_subtitle)
        ws2.write(1, 2, nombre_nominas, text_bold_left_subtitle)
        ws.write(1, 5, 'Hora :' + now.strftime("%H:%M:%S"), text_bold_left_paragrah)
        ws2.write(1, 5, 'Hora :' + now.strftime("%H:%M:%S"), text_bold_left_paragrah)
        ws.write(2, 2, period, text_bold_center_paragrah)
        ws2.write(2, 2, period, text_bold_center_paragrah)
        ws.write(2, 5, 'Fecha :' + today.strftime("%d/%m/%Y"), text_bold_left_paragrah)
        ws2.write(2, 5, 'Fecha :' + today.strftime("%d/%m/%Y"), text_bold_left_paragrah)
        ws.write(3, 0, 'CODIGO', font_format_h)
        ws2.write(3, 0, 'CODIGO', font_format_h)
        ws.write(3, 1, 'EMPLEADO', font_format_h)
        ws2.write(3, 1, 'EMPLEADO', font_format_h)
        ws.write(3, 2, 'DIAS PAG', font_format_h)
        ws2.write(3, 2, 'DIAS PAG', font_format_h)
        ws2.write(3, 3, 'SD', font_format_h)
        ws2.write(3, 4, 'SDI', font_format_h)
        ws2.write(3, 5, 'SBC', font_format_h)
        slip_ids = self.payslip_run_ids.mapped('slip_ids')

        sql_query = '''
                    select distinct hpl.code, upper(hpl.name), hpl.sequence
                    from hr_payslip_line hpl
                    where hpl.slip_id = any(array{0}::integer[])
                    and hpl.name NOT ILIKE '%EXENT%'
                    and hpl.name NOT ILIKE '%GRAVAD%'
                    order by hpl.sequence
                '''.format(slip_ids.ids)

        self._cr.execute(sql_query)
        tipos = []
        rows = [list(x) for x in self._cr.fetchall()]
        for num, row in enumerate(rows):
            ws.write(3, num + 3, row[1], font_format_h)
            ws2.write(3, num + 6, row[1], font_format_h)
            tipos.append(row[0])

        ws2.write(3, num + 7, 'TOTAL EFECTIVO', font_format_h)
        ws2.write(3, num + 8, 'TOTAL ESPECIE', font_format_h)

        resultado = {}
        sql_query = '''
                    select hre.no_empleado, hre.name
                    from hr_payslip hrp
                    left join hr_employee hre on hre.id = hrp.employee_id
                    where hrp.id = any(array{0}::integer[])
                    order by hre.no_empleado::int
                '''.format(slip_ids.ids)

        self._cr.execute(sql_query)
        rows = [list(x) for x in self._cr.fetchall()]
        for row in rows:
            resultado[row[0]] = {'nombre': row[1]}
        for num, record in enumerate(resultado):
            ws.write(4 + num, 0, record, font_format)
            ws.write(4 + num, 1, resultado[record]['nombre'], font_format)
            empleado_slip_ids = slip_ids.filtered(lambda x: x.no_empleado == record)
            # if len(slip_id) > 1:
            #     raise UserError('El código de empleado {0} se encuentra repetido.'.format(record))
            dias_pag = sum(empleado_slip_ids.mapped('worked_days_line_ids').filtered(lambda x: x.code in ['WORK100', 'FJC', 'SEPT']).mapped(
                'number_of_days'))
            ws.write(4 + num, 2, dias_pag, font_format2)
            resumen = {}
            for empleado_slip_id in empleado_slip_ids:
                if not empleado_slip_id.resumen:
                    empleado_slip_id.generar_resumen()
                data = json.loads(empleado_slip_id.resumen.replace("'", '"'))
                if record in resumen:
                    for tipo in data[record]:
                        if tipo in resumen[record]:
                            resumen[record][tipo] = resumen[record][tipo] + data[record][tipo]
                        else:
                            resumen[record][tipo] = data[record][tipo]
                else:
                    resumen = data
            # resumen = json.loads(slip_id.resumen.replace("'", '"'))
            for num2, tipo in enumerate(tipos):
                valor = 0
                if tipo in resumen[record]:
                    valor = round(resumen[record][tipo], 2)
                ws.write(4 + num, 3 + num2, valor, money_format)

        ws.write(6 + num, 2, 'TOTAL', text_bold_left_subtitle)
        for x in range(0, len(tipos)):
            col = self.num2col(x + 4)
            ws.write_formula('{0}{1}'.format(col, 7 + num), '=SUM({0}5:{0}{1})'.format(col, 5 + num), money_format)

        resultado = {}
        sql_query = '''
                    select hre.no_empleado, hre.name, hrd.name
                    from hr_payslip hrp
                    left join hr_employee hre on hre.id = hrp.employee_id
                    left join hr_department hrd on hrd.id = hre.department_id
                    where hrp.id = any(array{0}::integer[])
                    order by hrd.name, hre.no_empleado::int
                '''.format(slip_ids.ids)

        departamentos = []
        self._cr.execute(sql_query)
        rows = [list(x) for x in self._cr.fetchall()]
        for row in rows:
            resultado[row[0]] = {
                'nombre': row[1],
                'departamento': row[2],
            }
            if row[2] not in departamentos:
                departamentos.append(row[2])

        conteo = 0
        totales = []
        tot_percepciones = tipos.index("TPER") if "TPER" in tipos else 0
        tot_otros_pagos = tipos.index("TOP") if "TOP" in tipos else 0
        tot_deducciones = tipos.index("TDED") if "TDED" in tipos else 0
        if tot_percepciones:
            tot_percepciones = self.num2col(tot_percepciones + 7)
        if tot_otros_pagos:
            tot_otros_pagos = self.num2col(tot_otros_pagos + 7)
        if tot_deducciones:
            tot_deducciones = self.num2col(tot_deducciones + 7)
        for num, dept in enumerate(departamentos):
            ws2.write(4 + num + conteo, 0, dept, font_format)
            filtrado = {k: v['nombre'] for k, v in resultado.items() if v['departamento'] == dept}
            for num2, record in enumerate(filtrado):
                ws2.write(5 + num + num2 + conteo, 0, record, font_format)
                ws2.write(5 + num + num2 + conteo, 1, filtrado[record], font_format)
                empleado_slip_ids = slip_ids.filtered(lambda x: x.no_empleado == record)
                # if len(slip_id) > 1:
                #     raise UserError('El código de empleado {0} se encuentra repetido.'.format(record))
                dias_pag = sum(
                    empleado_slip_ids.mapped('worked_days_line_ids').filtered(lambda x: x.code in ['WORK100', 'FJC', 'SEPT']).mapped(
                        'number_of_days'))
                ws2.write(5 + num + num2 + conteo, 2, dias_pag, font_format2)
                sd = empleado_slip_ids.mapped('employee_id').contract_id.sueldo_diario
                ws2.write(5 + num + num2 + conteo, 3, sd, money_format)
                sdi = empleado_slip_ids.mapped('employee_id').contract_id.sueldo_diario_integrado
                ws2.write(5 + num + num2 + conteo, 4, sdi, money_format)
                sbc = empleado_slip_ids.mapped('employee_id').contract_id.sueldo_base_cotizacion
                ws2.write(5 + num + num2 + conteo, 5, sbc, money_format)

                resumen = {}
                for empleado_slip_id in empleado_slip_ids:
                    if not empleado_slip_id.resumen:
                        empleado_slip_id.generar_resumen()
                    data = json.loads(empleado_slip_id.resumen.replace("'", '"'))
                    if record in resumen:
                        for tipo in data[record]:
                            if tipo in resumen[record]:
                                resumen[record][tipo] = resumen[record][tipo] + data[record][tipo]
                            else:
                                resumen[record][tipo] = data[record][tipo]
                    else:
                        resumen = data

                # resumen = json.loads(slip_id.resumen.replace("'", '"'))
                for num3, tipo in enumerate(tipos):
                    valor = 0
                    if tipo in resumen[record]:
                        valor = round(resumen[record][tipo], 2)
                    ws2.write(5 + num + num2 + conteo, 6 + num3, valor, money_format)
                formula = '=SUM('
                if tot_percepciones:
                    formula = '{0}+{1}{2}'.format(formula, tot_percepciones, 6 + num + num2 + conteo)
                if tot_otros_pagos:
                    formula = '{0}+{1}{2}'.format(formula, tot_otros_pagos, 6 + num + num2 + conteo)
                if tot_deducciones:
                    formula = '{0}-{1}{2}'.format(formula, tot_deducciones, 6 + num + num2 + conteo)
                col = self.num2col(8 + num3)
                ws2.write_formula('{0}{1}'.format(col, 6 + num + num2 + conteo), '{0})'.format(formula), money_format)
                ws2.write(5 + num + num2 + conteo, 8 + num3, 0, money_format)
            ws2.write(6 + num + num2 + conteo, 5, 'TOTAL DEPARTAMENTO', total_style)
            for x in range(0, len(tipos) + 2):
                col = self.num2col(x + 7)
                ws2.write_formula('{0}{1}'.format(col, 7 + num + num2 + conteo),
                                  '=SUM({0}{1}:{0}{2})'.format(col, 6 + num + conteo, 6 + num + num2 + conteo),
                                  money_format)
            totales.append(7 + num + num2 + conteo)
            conteo += len(filtrado) + 1

        ws2.write(6 + num + conteo, 5, 'GRAN TOTAL', total_style)
        for x in range(0, len(tipos) + 2):
            col = self.num2col(x + 7)
            formula = ''
            for tot in totales:
                if formula:
                    formula = '{0} + {1}{2}'.format(formula, col, tot)
                else:
                    formula = '{0}{1}'.format(col, tot)
            ws2.write_formula('{0}{1}'.format(col, 7 + num + conteo), '=SUM({0})'.format(formula), money_format)

        ws.set_column('B:B', 40)
        ws.set_column('D:AZ', 15)
        ws2.set_column('B:B', 40)
        ws2.set_column('D:AZ', 15)
        wb.close()
        output.seek(0)
        data = output.read()

        self.write({'file_data': base64.b64encode(data)})
        return {
            'name': 'Payslips',
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model=" + self._name + "&id=" + str(
                self.id) + "&field=file_data&download=true&filename=listado_nomina.xlsx",
            'target': 'self',
        }

    # Funcion que convierte un número en la letra correspondiente a la columna en Excel
    # Ej. 2 --> "B"
    def num2col(self, n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string