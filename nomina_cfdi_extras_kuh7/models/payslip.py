# -*- coding: utf-8 -*-

import xlwt
import io
from xlwt import easyxf

from odoo import api, fields, models

    
class PayslipBatches(models.Model):
    _inherit = 'hr.payslip.run'

    def export_report_xlsx(self):
        import base64
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Listado de nomina')
        header_style = easyxf('font:height 200; align: horiz center; font:bold True;' "borders: top thin,left thin,right thin,bottom thin")
        text_bold_left = easyxf('font:height 200; font:bold True; align: horiz left;' "borders: top thin,bottom thin")
        text_left = easyxf('font:height 200; align: horiz left;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin")
        text_bold_right = easyxf('font:height 200;font:bold True; align: horiz right;' "borders: top thin,bottom thin")
        worksheet.write(0, 0, 'Cod', header_style)
        worksheet.write(0, 1, 'Empleado', header_style)
        worksheet.write(0, 2, 'Dias Pag', header_style)
        worksheet.write(0, 3, 'SD', header_style)
        worksheet.write(0, 4, 'SDI', header_style)
        worksheet.write(0, 5, 'SBC', header_style)
        # inicio cambios
        leave_ids = self.env['hr.leave.type'].search([])
        contador = 0
        leave_types = {}
        for leave_id in leave_ids:
            worksheet.write(0, 6 + contador, leave_id.name, header_style)
            leave_types[leave_id.name] = 6 + contador
            contador += 1
        # fin cambios
        col_nm = 6 + contador
        all_column = self.get_all_columns()
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        for col in all_col_list:
            worksheet.write(0, col_nm, all_col_dict[col], header_style)
            col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            worksheet.write(0, col_nm, t, header_style)
            col_nm += 1
        
        payslip_group_by_department = self.get_payslip_group_by_department()
        row = 1
        grand_total = {}
        for dept in self.env['hr.department'].browse(payslip_group_by_department.keys()).sorted(lambda x: x.name):
            row += 1
            worksheet.write_merge(row, row, 0, 5, dept.name, text_bold_left)
            total = {}
            row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_department[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.no_empleado or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]  
                hr_payslips.append(self.env['hr.payslip'].browse(slip))
            # inicio cambios
            x = {}
            for num, record in enumerate(hr_payslips):
                x[str(num)] = record.employee_id.name
            ordenado = {k: v for k, v in sorted(x.items(), key=lambda item: item[1])}
            x = []
            for record in ordenado.keys():
                x.append(hr_payslips[int(record)])
            hr_payslips = x
            # fin cambios
            for slip in hr_payslips:
                if slip.state == "cancel":
                    continue
                if slip.employee_id.no_empleado:
                    worksheet.write(row, 0, slip.employee_id.no_empleado, text_left)
                worksheet.write(row, 1, slip.employee_id.name, text_left)
                work_day = slip.get_total_work_days()
                worksheet.write(row, 2, work_day, text_right)
                worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, text_right)
                worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, text_right)
                worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, text_right)
                code_col = 6 + contador
                # inicio cambios
                coincidencias = []
                for line in slip.worked_days_line_ids:
                    if line.code in leave_types:
                        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                        coincidencias.append(line.code)
                pendientes = list(leave_types.keys() - coincidencias)
                for pendiente in pendientes:
                    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    amt = 0
                    if code in total.keys():
                        amt = slip.get_amount_from_rule_code(code)
                        if amt:
                            grand_total[code] = grand_total.get(code) + amt
                            total[code] = total.get(code) + amt
                    else:
                        amt = slip.get_amount_from_rule_code(code)
                        total[code] = amt or 0
                        if code in grand_total.keys():
                            grand_total[code] = amt + grand_total.get(code) or 0.0
                        else:
                            grand_total[code] = amt or 0
                    worksheet.write(row, code_col, amt, text_right)
                    code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('001'), text_right)
                code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('002'), text_right)
                row += 1
            worksheet.write_merge(row, row, 0, 5, 'Total Departamento', text_bold_left)
            code_col = 6 + contador
            for code in all_col_list:
                worksheet.write(row, code_col, total.get(code), text_bold_right)
                code_col += 1
        row += 1
        worksheet.write_merge(row, row, 0, 5, 'Gran Total', text_bold_left)
        code_col = 6 + contador
        for code in all_col_list:
            worksheet.write(row, code_col, grand_total.get(code), text_bold_right)
            code_col += 1

        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        self.write({'file_data': base64.b64encode(data)})
        action = {
            'name': 'Journal Entries',
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model=hr.payslip.run&id=" + str(self.id) + "&field=file_data&download=true&filename=Listado_de_nomina.xls",
            'target': 'self',
            }
        return action
