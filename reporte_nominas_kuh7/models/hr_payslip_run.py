# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from datetime import date
from datetime import datetime
import xlwt
import io
from xlwt import easyxf
import base64

import xlsxwriter
from odoo import api, fields, models, _


def _csv_row(data, delimiter=',', quote='"'):
    return quote + (quote + delimiter + quote).join([str(x).replace(quote, '\\' + quote) for x in data]) + quote + '\n'


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    l10n_id_attachment_id = fields.Many2one('ir.attachment', readonly=True, copy=False)

    def get_department(self):
        result = {}
        department = self.env['hr.department'].search([])
        for dept in department:
            result[dept.id] = dept.name
        return result

    def get_dept_total(self, dept_id):
        result = {}
        for rule in self.env['hr.salary.rule'].search([]):
            result[rule.code] = 0
        for payslip in self.slip_ids:
            if payslip.employee_id.department_id.id == dept_id and payslip.state != "cancel":
                for line in payslip.line_ids:
                    if line.code in result.keys():
                        result[line.code] = round(line.total + result.get(line.code), 2)
                    else:
                        result[line.code] = round(line.total, 2)
        return result

    def get_grand_total(self):
        result = {}
        for rule in self.env['hr.salary.rule'].search([]):
            result[rule.code] = 0
        for payslip in self.slip_ids:
            if payslip.state != "cancel":
                for line in payslip.line_ids:
                    if line.code in result.keys():
                        result[line.code] = round(line.total + result.get(line.code), 2)
                    else:
                        result[line.code] = round(line.total, 2)
        return result

    def get_payslip_group_by_department(self):
        result = {}
        for line in self.slip_ids:
            if line.employee_id.department_id.id in result.keys():
                result[line.employee_id.department_id.id].append(line)
            else:
                result[line.employee_id.department_id.id] = [line]
        return result

    def get_payslip_group_by_payslip_number(self):
        result = {}
        for line in self.slip_ids:
            if line.employee_id.id in result.keys():
                result[line.employee_id.id].append(line)
            else:
                result[line.employee_id.id] = [line]
        return result

    def get_all_columns(self):
        result = {}
        all_col_list_seq = []
        if self.slip_ids:
            for line in self.env['hr.payslip.line'].search([('slip_id', 'in', self.slip_ids.ids)], order="sequence"):
                if line.code not in all_col_list_seq:
                    all_col_list_seq.append(line.code)
                if line.code not in result.keys():
                    result[line.code] = line.name
        #         for payslip in self.slip_ids:
        #             for line in payslip.line_ids:
        #                 if line.code not in result.keys():
        #                     result[line.code] = line.name
        return [result, all_col_list_seq]

    def export_report_xlsx_2(self):
        #import base64
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Listado de nómina')

        text_bold_left_title = easyxf('font:height 300; align: horiz center; font:bold True;')
        text_bold_left_subtitle = easyxf('font:height 250; align: horiz center;')
        text_bold_left_paragrah = easyxf('font:height 160; align: horiz left;')
        text_bold_center_paragrah = easyxf('font:height 160; align: horiz center;')

        tz_mx = pytz.timezone('America/Mexico_City')
        now = datetime.now(tz_mx)
        today = date.today()

        money_format = xlwt.XFStyle()
        money_format.num_format_str = '#,##0.00'
        money_format.font.height = 180
        money_format.alignment.HORZ_RIGHT = True

        money_format_b = xlwt.XFStyle()
        money_format_b.num_format_str = '#,##0.00'
        money_format_b.font.height = 180
        money_format_b.font.bold = True
        money_format_b.alignment.HORZ_RIGHT = True

        money_format_n = xlwt.XFStyle()
        money_format_n.num_format_str = '#,##0.00'
        money_format_n.font.height = 180
        money_format_n.alignment.HORZ_RIGHT = True

        font_format = xlwt.XFStyle()
        font_format.font.height = 180
        font_format.alignment.HORZ_LEFT = True

        font_format_r = xlwt.XFStyle()
        font_format_r.font.height = 180
        font_format_r.alignment.HORZ_RIGHT = True

        font_format_r_b = xlwt.XFStyle()
        font_format_r_b.font.height = 180
        font_format_r_b.font.bold = True
        font_format_r_b.alignment.HORZ_RIGHT = True

        font_format_l_b = xlwt.XFStyle()
        font_format_l_b.font.height = 180
        font_format_l_b.font.bold = True
        font_format_l_b.alignment.HORZ_LEFT = True

        font_format_h = xlwt.XFStyle()
        font_format_h.font.height = 200
        font_format_h.font.bold = True
        font_format_h.alignment.wrap = True
        font_format_h.alignment.HORZ_CENTER = True

        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['lavender']
        font_format_h.pattern = pattern

        border = xlwt.Borders()
        border.left = 1
        border.right = 1
        border.top = 2
        border.bottom = 2
        border.right_colour = xlwt.Style.colour_map['plum']
        border.left_colour = xlwt.Style.colour_map['plum']
        border.top_colour = xlwt.Style.colour_map['plum']
        border.bottom_colour = xlwt.Style.colour_map['plum']
        font_format_h.borders = border

        worksheet.write(3, 0, 'Código', font_format_h)
        worksheet.write(3, 1, 'Empleado', font_format_h)
        worksheet.write(3, 2, 'Dias Pag', font_format_h)
        worksheet.write(3, 3, 'SD', font_format_h)
        worksheet.write(3, 4, 'SDI', font_format_h)
        worksheet.write(3, 5, 'SBC', font_format_h)
        # inicio cambios
        # leave_ids = self.env['hr.leave.type'].search([])
        # contador = 0
        # leave_types = {}
        # for leave_id in leave_ids:
        #    worksheet.write(0, 6 + contador, leave_id.name, header_style)
        #    leave_types[leave_id.name] = 6 + contador
        #    contador += 1
        # col_nm = 6 + contador
        # fin cambios
        col_nm = 6
        all_column = self.get_all_columns()
        # print("All_columns", all_column)
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        # print("All_col_dict", all_col_dict)
        # print("All_col_list", all_col_list)
        for col in all_col_list:
            cadena = all_col_dict[col].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                # print("name right:", all_col_dict[col])
                worksheet.write(3, col_nm, all_col_dict[col], font_format_h)
                col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            # print("monto", t)
            worksheet.write(3, col_nm, t, font_format_h)
            col_nm += 1

        payslip_group_by_payslip_number = self.get_payslip_group_by_payslip_number()
        row = 4
        grand_total = {}
        company_name = ""
        for dept in self.env['hr.employee'].browse(payslip_group_by_payslip_number.keys()).sorted(lambda x: x.name):
            #company_name = 'OKAWA MEXICANA SA. DE CV'
            company_name = dept.company_id.name
            # row += 1
            # worksheet.write_merge(row, row, 0, 5, dept.name, text_bold_left)
            total = {}
            # row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_payslip_number[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.no_empleado or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                # print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                # print("value slip", slip)
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
                    worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                worksheet.write(row, 1, slip.employee_id.name, font_format)
                work_day = slip.get_total_work_days()
                worksheet.write(row, 2, work_day, money_format_n)
                worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                # code_col = 6 + contador
                code_col = 6
                # inicio cambios
                # coincidencias = []
                # for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                # pendientes = list(leave_types.keys() - coincidencias)
                # for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    # print("Name col", all_col_dict[code])
                    # print("codigo_f1", code)
                    cadena = all_col_dict[code].upper()
                    find_exent = cadena.find("EXENTO")
                    find_exent_1 = cadena.find("EXENTA")
                    find_gravado = cadena.find("GRAVADO")
                    find_gravado_1 = cadena.find("GRAVADA")
                    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                        worksheet.write(row, code_col, round(amt, 2), money_format)
                        code_col += 1
                worksheet.write(row, code_col, round(slip.get_total_code_value('001'), 2), money_format)
                code_col += 1
                worksheet.write(row, code_col, round(slip.get_total_code_value('002'), 2), money_format)
                row += 1
            # worksheet.write_merge(row, row, 0, 5, 'Total Departamento', text_bold_left)
            # code_col = 6 + contador
            # code_col = 6
            # for code in all_col_list:
            #    cadena = all_col_dict[code].upper()
            #    find_exent = cadena.find("EXENTO")
            #    find_exent_1 = cadena.find("EXENTA")
            #    find_gravado = cadena.find("GRAVADO")
            #    find_gravado_1 = cadena.find("GRAVADA")
            #    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            #        worksheet.write(row, code_col, total.get(code), text_bold_right)
            #        code_col += 1
        row += 1
        worksheet.write_merge(row, row, 0, 5, 'Gran Total', font_format_l_b)
        # code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            cadena = all_col_dict[code].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                worksheet.write(row, code_col, round(grand_total.get(code), 2), money_format_b)
                code_col += 1

        name_payslip = self.name
        period = 'Periodo del ' + self.date_start.strftime('%d/%m/%Y') + ' al ' + self.date_end.strftime('%d/%m/%Y')
        worksheet.write_merge(0, 0, 1, 4, company_name, text_bold_left_title)
        worksheet.write_merge(1, 1, 1, 4, name_payslip, text_bold_left_subtitle)
        worksheet.write_merge(1, 1, 5, 6, 'Hora :' + now.strftime("%H:%M:%S"), text_bold_left_paragrah)
        worksheet.write_merge(2, 2, 1, 4, period, text_bold_center_paragrah)
        worksheet.write_merge(2, 2, 5, 6, 'Fecha :' + today.strftime("%d/%m/%Y"), text_bold_left_paragrah)

        #
        #Hoja 2
        #
        worksheet = workbook.add_sheet('Listado de nómina por departamento')
        worksheet.write(3, 0, 'Cod', font_format_h)
        worksheet.write(3, 1, 'Empleado', font_format_h)
        worksheet.write(3, 2, 'Dias Pag', font_format_h)
        worksheet.write(3, 3, 'SD', font_format_h)
        worksheet.write(3, 4, 'SDI', font_format_h)
        worksheet.write(3, 5, 'SBC', font_format_h)
        # inicio cambios
        #leave_ids = self.env['hr.leave.type'].search([])
        #contador = 0
        #leave_types = {}
        #for leave_id in leave_ids:
        #    worksheet.write(0, 6 + contador, leave_id.name, header_style)
        #    leave_types[leave_id.name] = 6 + contador
        #    contador += 1
        #col_nm = 6 + contador
        # fin cambios
        col_nm = 6
        all_column = self.get_all_columns()
        #print("All_columns", all_column)
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        #print("All_col_dict", all_col_dict)
        #print("All_col_list", all_col_list)
        for col in all_col_list:
            cadena = all_col_dict[col].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                #print("name right:", all_col_dict[col])
                worksheet.write(3, col_nm, all_col_dict[col], font_format_h)
                col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            #print("monto", t)
            worksheet.write(3, col_nm, t, font_format_h)
            col_nm += 1

        payslip_group_by_department = self.get_payslip_group_by_department()
        row = 4
        grand_total = {}
        company_name = ''
        for dept in self.env['hr.department'].browse(payslip_group_by_department.keys()).sorted(lambda x: x.name):
            #company_name = 'OKAWA MEXICANA SA. DE CV'
            company_name = dept.company_id.name
            row += 1
            worksheet.write_merge(row, row, 0, 5, dept.name, font_format_l_b)
            total = {}
            row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_department[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.id or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                #print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                #print("value slip", slip)
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
                    worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                worksheet.write(row, 1, slip.employee_id.name, font_format)
                work_day = slip.get_total_work_days()
                worksheet.write(row, 2, work_day, money_format_n)
                worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                #code_col = 6 + contador
                code_col = 6
                # inicio cambios
                #coincidencias = []
                #for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                #pendientes = list(leave_types.keys() - coincidencias)
                #for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    #print("Name col", all_col_dict[code])
                    #print("codigo_f1", code)
                    cadena = all_col_dict[code].upper()
                    find_exent = cadena.find("EXENTO")
                    find_exent_1 = cadena.find("EXENTA")
                    find_gravado = cadena.find("GRAVADO")
                    find_gravado_1 = cadena.find("GRAVADA")
                    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                        worksheet.write(row, code_col, amt, money_format)
                        code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('001'), money_format)
                code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('002'), money_format)
                row += 1
            worksheet.write_merge(row, row, 0, 5, 'Total Departamento', font_format_l_b)
            #code_col = 6 + contador
            code_col = 6
            for code in all_col_list:
                cadena = all_col_dict[code].upper()
                find_exent = cadena.find("EXENTO")
                find_exent_1 = cadena.find("EXENTA")
                find_gravado = cadena.find("GRAVADO")
                find_gravado_1 = cadena.find("GRAVADA")
                if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                    worksheet.write(row, code_col, total.get(code), money_format_b)
                    code_col += 1
        row += 1
        worksheet.write_merge(row, row, 0, 5, 'Gran Total', font_format_l_b)
        #code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            cadena = all_col_dict[code].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                worksheet.write(row, code_col, grand_total.get(code), money_format_b)
                code_col += 1

        name_payslip = self.name
        period = 'Periodo del ' + self.date_start.strftime('%d/%m/%Y') + ' al ' + self.date_end.strftime('%d/%m/%Y')
        worksheet.write_merge(0, 0, 1, 4, company_name, text_bold_left_title)
        worksheet.write_merge(1, 1, 1, 4, name_payslip, text_bold_left_subtitle)
        worksheet.write_merge(1, 1, 5, 6, 'Hora :' + now.strftime("%H:%M:%S"), text_bold_left_paragrah)
        worksheet.write_merge(2, 2, 1, 4, period, text_bold_center_paragrah)
        worksheet.write_merge(2, 2, 5, 6, 'Fecha :' + today.strftime("%d/%m/%Y"), text_bold_left_paragrah)

        #
        # Hoja 3
        #
        worksheet = workbook.add_sheet('Exentos y gravados')

        worksheet.write(3, 0, 'Código', font_format_h)
        worksheet.write(3, 1, 'Empleado', font_format_h)
        worksheet.write(3, 2, 'Dias Pag', font_format_h)
        worksheet.write(3, 3, 'SD', font_format_h)
        worksheet.write(3, 4, 'SDI', font_format_h)
        worksheet.write(3, 5, 'SBC', font_format_h)
        # inicio cambios
        #leave_ids = self.env['hr.leave.type'].search([])
        #contador = 0
        #leave_types = {}
        #for leave_id in leave_ids:
        #    worksheet.write(0, 6 + contador, leave_id.name, font_format_h)
        #    leave_types[leave_id.name] = 6 + contador
        #    contador += 1
        #col_nm = 6 + contador
        #fin cambios

        col_nm = 6
        all_column = self.get_all_columns()
        # print("All_columns", all_column)
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        # print("All_col_dict", all_col_dict)
        # print("All_col_list", all_col_list)
        for col in all_col_list:
            #cadena = all_col_dict[col].upper()
            #find_exent = cadena.find("EXENTO")
            #find_exent_1 = cadena.find("EXENTA")
            #find_gravado = cadena.find("GRAVADO")
            #find_gravado_1 = cadena.find("GRAVADA")
            #if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                # print("name right:", all_col_dict[col])
            worksheet.write(3, col_nm, all_col_dict[col], font_format_h)
            col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            # print("monto", t)
            worksheet.write(3, col_nm, t, font_format_h)
            col_nm += 1

        payslip_group_by_payslip_number = self.get_payslip_group_by_payslip_number()
        row = 4
        grand_total = {}
        company_name = ""
        for dept in self.env['hr.employee'].browse(payslip_group_by_payslip_number.keys()).sorted(lambda x: x.name):
            # company_name = 'OKAWA MEXICANA SA. DE CV'
            company_name = dept.company_id.name
            # row += 1
            # worksheet.write_merge(row, row, 0, 5, dept.name, text_bold_left)
            total = {}
            # row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_payslip_number[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.no_empleado or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                # print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                # print("value slip", slip)
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
                    worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                worksheet.write(row, 1, slip.employee_id.name, font_format)
                work_day = slip.get_total_work_days()
                worksheet.write(row, 2, work_day, money_format_n)
                worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                #code_col = 6 + contador
                code_col = 6
                # inicio cambios
                # coincidencias = []
                # for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                # pendientes = list(leave_types.keys() - coincidencias)
                # for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    # print("Name col", all_col_dict[code])
                    # print("codigo_f1", code)
                    #cadena = all_col_dict[code].upper()
                    #find_exent = cadena.find("EXENTO")
                    #find_exent_1 = cadena.find("EXENTA")
                    #find_gravado = cadena.find("GRAVADO")
                    #find_gravado_1 = cadena.find("GRAVADA")
                    #if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                    worksheet.write(row, code_col, round(amt, 2), money_format)
                    code_col += 1
                worksheet.write(row, code_col, round(slip.get_total_code_value('001'), 2), money_format)
                code_col += 1
                worksheet.write(row, code_col, round(slip.get_total_code_value('002'), 2), money_format)
                row += 1
            # worksheet.write_merge(row, row, 0, 5, 'Total Departamento', text_bold_left)
            # code_col = 6 + contador
            #code_col = 6
            # for code in all_col_list:
            #    cadena = all_col_dict[code].upper()
            #    find_exent = cadena.find("EXENTO")
            #    find_exent_1 = cadena.find("EXENTA")
            #    find_gravado = cadena.find("GRAVADO")
            #    find_gravado_1 = cadena.find("GRAVADA")
            #    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            #        worksheet.write(row, code_col, total.get(code), text_bold_right)
            #        code_col += 1
        row += 1
        worksheet.write_merge(row, row, 0, 5, 'Gran Total', font_format_l_b)
        #code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            #cadena = all_col_dict[code].upper()
            #find_exent = cadena.find("EXENTO")
            #find_exent_1 = cadena.find("EXENTA")
            #find_gravado = cadena.find("GRAVADO")
            #find_gravado_1 = cadena.find("GRAVADA")
            #if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            worksheet.write(row, code_col, round(grand_total.get(code), 2), money_format_b)
            code_col += 1

        name_payslip = self.name
        period = 'Periodo del ' + self.date_start.strftime('%d/%m/%Y') + ' al ' + self.date_end.strftime('%d/%m/%Y')
        worksheet.write_merge(0, 0, 1, 4, company_name, text_bold_left_title)
        worksheet.write_merge(1, 1, 1, 4, name_payslip, text_bold_left_subtitle)
        worksheet.write_merge(1, 1, 5, 6, 'Hora :' + now.strftime("%H:%M:%S"), text_bold_left_paragrah)
        worksheet.write_merge(2, 2, 1, 4, period, text_bold_center_paragrah)
        worksheet.write_merge(2, 2, 5, 6, 'Fecha :' + today.strftime("%d/%m/%Y"), text_bold_left_paragrah)

        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        self.write({'file_data': base64.b64encode(data)})
        action = {
            'name': 'Journal Entries',
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model=hr.payslip.run&id=" + str(
                self.id) + "&field=file_data&download=true&filename=Listado_de_nomina.xlsx",
            'target': 'self',
        }
        return action

    def export_report_xlsx_1(self):
        # import base64
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Listado de nómina')

        # workbook = xlwt.Workbook()
        # worksheet = workbook.add_sheet('Listado de nómina')

        # text_bold_left_title = easyxf('font:height 300; align: horiz center; font:bold True;')
        text_bold_left_title = workbook.add_format({'font_size': '15', 'align': 'center', 'font_name': 'Arial'})
        # text_bold_left_subtitle = easyxf('font:height 250; align: horiz center;')
        text_bold_left_subtitle = workbook.add_format({'font_size': '12.5', 'align': 'center', 'font_name': 'Arial'})
        # text_bold_left_subtitle_b = easyxf('font:height 230; align: horiz center; font:bold True;')
        # text_bold_left_paragrah = easyxf('font:height 160; align: horiz left;')
        text_bold_left_paragrah = workbook.add_format({'font_size': '8', 'align': 'left', 'font_name': 'Arial'})
        # text_bold_center_paragrah = easyxf('font:height 160; align: horiz center;')
        text_bold_center_paragrah = workbook.add_format({'font_size': '8', 'align': 'center', 'font_name': 'Arial'})

        tz_mx = pytz.timezone('America/Mexico_City')
        now = datetime.now(tz_mx)
        today = date.today()

        # money_format = xlwt.XFStyle()
        # money_format.num_format_str = '$#,##0.00'
        # money_format.font.height = 200
        # money_format.alignment.HORZ_RIGHT = True
        money_format = workbook.add_format(
            {'num_format': '$#,##0.00', 'font_size': '10', 'align': 'right', 'font_name': 'Arial'})

        # money_format_b = xlwt.XFStyle()
        # money_format_b.num_format_str = '$#,##0.00'
        # money_format_b.font.height = 200
        # money_format_b.font.bold = True
        # money_format_b.alignment.HORZ_RIGHT = True
        money_format_b = workbook.add_format(
            {'num_format': '$#,##0.00', 'font_size': '10', 'align': 'right', 'bold': True, 'font_name': 'Arial'})

        # money_format_n = xlwt.XFStyle()
        # money_format_n.num_format_str = '#,##0.00'
        # money_format_n.font.height = 200
        # money_format_n.alignment.HORZ_RIGHT = True
        money_format_n = workbook.add_format(
            {'num_format': '#,##0.00', 'font_size': '10', 'align': 'right', 'font_name': 'Arial'})

        # font_format = xlwt.XFStyle()
        # font_format.font.height = 200
        # font_format.alignment.HORZ_LEFT = True
        font_format = workbook.add_format({'font_size': '10', 'align': 'left', 'font_name': 'Arial'})

        # font_format_red = xlwt.XFStyle()
        # font_format_red.font.height = 200
        # font_format_red.font.colour_index = xlwt.Style.colour_map['red']
        # font_format_red.font.bold = True
        # font_format_red.alignment.HORZ_LEFT = True
        font_format_red = workbook.add_format(
            {'font_size': '10', 'align': 'left', 'bold': True, 'font_color': 'red', 'font_name': 'Arial'})

        # font_format_r = xlwt.XFStyle()
        # font_format_r.font.height = 200
        # font_format_r.alignment.HORZ_RIGHT = True
        font_format_r = workbook.add_format({'font_size': '10', 'align': 'right', 'font_name': 'Arial'})

        # font_format_r_b = xlwt.XFStyle()
        # font_format_r_b.font.height = 200
        # font_format_r_b.font.bold = True
        # font_format_r_b.alignment.HORZ_RIGHT = True
        font_format_r_b = workbook.add_format({'font_size': '10', 'align': 'right', 'bold': True, 'font_name': 'Arial'})

        # font_format_l_b = xlwt.XFStyle()
        # font_format_l_b.font.height = 200
        # font_format_l_b.font.bold = True
        # font_format_l_b.alignment.HORZ_LEFT = True
        font_format_l_b = workbook.add_format({'font_size': '10', 'align': 'left', 'bold': True, 'font_name': 'Arial'})

        # font_format_h = xlwt.XFStyle()
        font_format_h = workbook.add_format()
        font_format_h.set_font_size(10)
        font_format_h.set_font_name('Arial')
        # font_format_h.font.height = 200
        font_format_h.set_bold()
        # font_format_h.font.bold = True
        # font_format_h.alignment.wrap = True
        font_format_h.set_text_wrap()
        # font_format_h.alignment.HORZ_CENTER = True
        font_format_h.set_align('center')

        font_format_h.set_pattern(1)
        font_format_h.set_bg_color('fcf991')
        # pattern.pattern_fore_colour = xlwt.Style.colour_map['light_yellow']
        # font_format_h.pattern = pattern

        # border = xlwt.Borders()
        font_format_h.set_border(1)
        # border.left = 1
        font_format_h.set_left(1)
        # border.right = 1
        font_format_h.set_right(1)
        # border.top = 2
        font_format_h.set_top(2)
        # border.bottom = 2
        font_format_h.set_bottom(2)
        font_format_h.set_border_color('blue')
        # border.right_colour = xlwt.Style.colour_map['blue']
        # border.left_colour = xlwt.Style.colour_map['blue']
        # border.top_colour = xlwt.Style.colour_map['blue']
        # border.bottom_colour = xlwt.Style.colour_map['blue']
        # font_format_h.borders = border
        # font_format_h = workbook.add_format({'height': '200', 'alignment': 'center', 'bold': True})

        worksheet.write(3, 0, 'Código', font_format_h)
        worksheet.write(3, 1, 'Empleado', font_format_h)
        worksheet.write(3, 2, 'Dias Pag', font_format_h)
        worksheet.write(3, 3, 'SD', font_format_h)
        worksheet.write(3, 4, 'SDI', font_format_h)
        worksheet.write(3, 5, 'SBC', font_format_h)
        # inicio cambios
        # leave_ids = self.env['hr.leave.type'].search([])
        # contador = 0
        # leave_types = {}
        # for leave_id in leave_ids:
        #    worksheet.write(0, 6 + contador, leave_id.name, header_style)
        #    leave_types[leave_id.name] = 6 + contador
        #    contador += 1
        # col_nm = 6 + contador
        # fin cambios
        col_nm = 6
        all_column = self.get_all_columns()
        # print("All_columns", all_column)
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        # print("All_col_dict", all_col_dict)
        # print("All_col_list", all_col_list)
        for col in all_col_list:
            cadena = all_col_dict[col].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                # print("name right:", all_col_dict[col])
                worksheet.write(3, col_nm, all_col_dict[col], font_format_h)
                col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            # print("monto", t)
            worksheet.write(3, col_nm, t, font_format_h)
            col_nm += 1

        payslip_group_by_payslip_number = self.get_payslip_group_by_payslip_number()
        row = 4
        grand_total = {}
        company_name = ""
        for dept in self.env['hr.employee'].browse(payslip_group_by_payslip_number.keys()).sorted(lambda x: x.name):
            # company_name = 'OKAWA MEXICANA SA. DE CV'
            company_name = dept.company_id.name
            # row += 1
            # worksheet.write_merge(row, row, 0, 5, dept.name, text_bold_left)
            total = {}
            # row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_payslip_number[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.no_empleado or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                # print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                # print("value slip", slip)
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
                    worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                worksheet.write(row, 1, slip.employee_id.name, font_format)
                work_day = slip.get_total_work_days()
                worksheet.write(row, 2, work_day, money_format_n)
                worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                # code_col = 6 + contador
                code_col = 6
                # inicio cambios
                # coincidencias = []
                # for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                # pendientes = list(leave_types.keys() - coincidencias)
                # for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    # print("Name col", all_col_dict[code])
                    # print("codigo_f1", code)
                    cadena = all_col_dict[code].upper()
                    find_exent = cadena.find("EXENTO")
                    find_exent_1 = cadena.find("EXENTA")
                    find_gravado = cadena.find("GRAVADO")
                    find_gravado_1 = cadena.find("GRAVADA")
                    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                        worksheet.write(row, code_col, round(amt, 2), money_format)
                        code_col += 1
                worksheet.write(row, code_col, round(slip.get_total_code_value('001'), 2), money_format)
                code_col += 1
                worksheet.write(row, code_col, round(slip.get_total_code_value('002'), 2), money_format)
                row += 1
            # worksheet.write_merge(row, row, 0, 5, 'Total Departamento', text_bold_left)
            # code_col = 6 + contador
            # code_col = 6
            # for code in all_col_list:
            #    cadena = all_col_dict[code].upper()
            #    find_exent = cadena.find("EXENTO")
            #    find_exent_1 = cadena.find("EXENTA")
            #    find_gravado = cadena.find("GRAVADO")
            #    find_gravado_1 = cadena.find("GRAVADA")
            #    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            #        worksheet.write(row, code_col, total.get(code), text_bold_right)
            #        code_col += 1
        row += 1
        worksheet.write(row, 0, 'Gran Total', font_format_l_b)
        # code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            cadena = all_col_dict[code].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                worksheet.write(row, code_col, round(grand_total.get(code), 2), money_format_b)
                code_col += 1

        name_payslip = self.name
        period = 'Periodo del ' + self.date_start.strftime('%d/%m/%Y') + ' al ' + self.date_end.strftime('%d/%m/%Y')
        worksheet.write(0, 2, company_name, text_bold_left_title)
        worksheet.write(1, 2, name_payslip, text_bold_left_subtitle)
        worksheet.write(1, 5, 'Hora :' + now.strftime("%H:%M:%S"), text_bold_left_paragrah)
        worksheet.write(2, 2, period, text_bold_center_paragrah)
        worksheet.write(2, 5, 'Fecha :' + today.strftime("%d/%m/%Y"), text_bold_left_paragrah)

        #
        # Hoja 2
        #
        #worksheet = workbook.add_sheet('Listado de nómina por departamento')
        worksheet = workbook.add_worksheet('Listado de nómina por departamento')

        worksheet.write(3, 0, 'Cod', font_format_h)
        worksheet.write(3, 1, 'Empleado', font_format_h)
        worksheet.write(3, 2, 'Dias Pag', font_format_h)
        worksheet.write(3, 3, 'SD', font_format_h)
        worksheet.write(3, 4, 'SDI', font_format_h)
        worksheet.write(3, 5, 'SBC', font_format_h)
        # inicio cambios
        # leave_ids = self.env['hr.leave.type'].search([])
        # contador = 0
        # leave_types = {}
        # for leave_id in leave_ids:
        #    worksheet.write(0, 6 + contador, leave_id.name, header_style)
        #    leave_types[leave_id.name] = 6 + contador
        #    contador += 1
        # col_nm = 6 + contador
        # fin cambios
        col_nm = 6
        all_column = self.get_all_columns()
        # print("All_columns", all_column)
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        # print("All_col_dict", all_col_dict)
        # print("All_col_list", all_col_list)
        for col in all_col_list:
            cadena = all_col_dict[col].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                # print("name right:", all_col_dict[col])
                worksheet.write(3, col_nm, all_col_dict[col], font_format_h)
                col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            # print("monto", t)
            worksheet.write(3, col_nm, t, font_format_h)
            col_nm += 1

        payslip_group_by_department = self.get_payslip_group_by_department()
        row = 4
        grand_total = {}
        company_name = ''
        for dept in self.env['hr.department'].browse(payslip_group_by_department.keys()).sorted(lambda x: x.name):
            # company_name = 'OKAWA MEXICANA SA. DE CV'
            company_name = dept.company_id.name
            row += 1
            worksheet.write(row, 2, dept.name, font_format_l_b)
            total = {}
            row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_department[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.id or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                # print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                # print("value slip", slip)
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
                    worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                worksheet.write(row, 1, slip.employee_id.name, font_format)
                work_day = slip.get_total_work_days()
                worksheet.write(row, 2, work_day, money_format_n)
                worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                # code_col = 6 + contador
                code_col = 6
                # inicio cambios
                # coincidencias = []
                # for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                # pendientes = list(leave_types.keys() - coincidencias)
                # for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    # print("Name col", all_col_dict[code])
                    # print("codigo_f1", code)
                    cadena = all_col_dict[code].upper()
                    find_exent = cadena.find("EXENTO")
                    find_exent_1 = cadena.find("EXENTA")
                    find_gravado = cadena.find("GRAVADO")
                    find_gravado_1 = cadena.find("GRAVADA")
                    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                        worksheet.write(row, code_col, amt, money_format)
                        code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('001'), money_format)
                code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('002'), money_format)
                row += 1
            worksheet.write(row, 2, 'Total Departamento', font_format_l_b)
            # code_col = 6 + contador
            code_col = 6
            for code in all_col_list:
                cadena = all_col_dict[code].upper()
                find_exent = cadena.find("EXENTO")
                find_exent_1 = cadena.find("EXENTA")
                find_gravado = cadena.find("GRAVADO")
                find_gravado_1 = cadena.find("GRAVADA")
                if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                    worksheet.write(row, code_col, total.get(code), money_format_b)
                    code_col += 1
        row += 1
        worksheet.write(row, 2, 'Gran Total', font_format_l_b)
        # code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            cadena = all_col_dict[code].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                worksheet.write(row, code_col, grand_total.get(code), money_format_b)
                code_col += 1

        name_payslip = self.name
        period = 'Periodo del ' + self.date_start.strftime('%d/%m/%Y') + ' al ' + self.date_end.strftime('%d/%m/%Y')
        worksheet.write(0, 2, company_name, text_bold_left_title)
        worksheet.write(1, 2, name_payslip, text_bold_left_subtitle)
        worksheet.write(1, 5, 'Hora :' + now.strftime("%H:%M:%S"), text_bold_left_paragrah)
        worksheet.write(2, 2, period, text_bold_center_paragrah)
        worksheet.write(2, 5, 'Fecha :' + today.strftime("%d/%m/%Y"), text_bold_left_paragrah)

        #
        # Hoja 3
        #
        #worksheet = workbook.add_sheet('Exentos y gravados')
        worksheet = workbook.add_worksheet('Exentos y gravados')

        worksheet.write(3, 0, 'Código', font_format_h)
        worksheet.write(3, 1, 'Empleado', font_format_h)
        worksheet.write(3, 2, 'Dias Pag', font_format_h)
        worksheet.write(3, 3, 'SD', font_format_h)
        worksheet.write(3, 4, 'SDI', font_format_h)
        worksheet.write(3, 5, 'SBC', font_format_h)
        # inicio cambios
        # leave_ids = self.env['hr.leave.type'].search([])
        # contador = 0
        # leave_types = {}
        # for leave_id in leave_ids:
        #    worksheet.write(0, 6 + contador, leave_id.name, font_format_h)
        #    leave_types[leave_id.name] = 6 + contador
        #    contador += 1
        # col_nm = 6 + contador
        # fin cambios

        col_nm = 6
        all_column = self.get_all_columns()
        # print("All_columns", all_column)
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        # print("All_col_dict", all_col_dict)
        # print("All_col_list", all_col_list)
        for col in all_col_list:
            # cadena = all_col_dict[col].upper()
            # find_exent = cadena.find("EXENTO")
            # find_exent_1 = cadena.find("EXENTA")
            # find_gravado = cadena.find("GRAVADO")
            # find_gravado_1 = cadena.find("GRAVADA")
            # if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            # print("name right:", all_col_dict[col])
            worksheet.write(3, col_nm, all_col_dict[col], font_format_h)
            col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            # print("monto", t)
            worksheet.write(3, col_nm, t, font_format_h)
            col_nm += 1

        payslip_group_by_payslip_number = self.get_payslip_group_by_payslip_number()
        row = 4
        grand_total = {}
        company_name = ""
        for dept in self.env['hr.employee'].browse(payslip_group_by_payslip_number.keys()).sorted(lambda x: x.name):
            # company_name = 'OKAWA MEXICANA SA. DE CV'
            company_name = dept.company_id.name
            # row += 1
            # worksheet.write_merge(row, row, 0, 5, dept.name, text_bold_left)
            total = {}
            # row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_payslip_number[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.no_empleado or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                # print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                # print("value slip", slip)
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
                    worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                worksheet.write(row, 1, slip.employee_id.name, font_format)
                work_day = slip.get_total_work_days()
                worksheet.write(row, 2, work_day, money_format_n)
                worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                # code_col = 6 + contador
                code_col = 6
                # inicio cambios
                # coincidencias = []
                # for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                # pendientes = list(leave_types.keys() - coincidencias)
                # for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    # print("Name col", all_col_dict[code])
                    # print("codigo_f1", code)
                    # cadena = all_col_dict[code].upper()
                    # find_exent = cadena.find("EXENTO")
                    # find_exent_1 = cadena.find("EXENTA")
                    # find_gravado = cadena.find("GRAVADO")
                    # find_gravado_1 = cadena.find("GRAVADA")
                    # if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                    worksheet.write(row, code_col, round(amt, 2), money_format)
                    code_col += 1
                worksheet.write(row, code_col, round(slip.get_total_code_value('001'), 2), money_format)
                code_col += 1
                worksheet.write(row, code_col, round(slip.get_total_code_value('002'), 2), money_format)
                row += 1
            # worksheet.write_merge(row, row, 0, 5, 'Total Departamento', text_bold_left)
            # code_col = 6 + contador
            # code_col = 6
            # for code in all_col_list:
            #    cadena = all_col_dict[code].upper()
            #    find_exent = cadena.find("EXENTO")
            #    find_exent_1 = cadena.find("EXENTA")
            #    find_gravado = cadena.find("GRAVADO")
            #    find_gravado_1 = cadena.find("GRAVADA")
            #    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            #        worksheet.write(row, code_col, total.get(code), text_bold_right)
            #        code_col += 1
        row += 1
        worksheet.write(row, 5, 'Gran Total', font_format_l_b)
        # code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            # cadena = all_col_dict[code].upper()
            # find_exent = cadena.find("EXENTO")
            # find_exent_1 = cadena.find("EXENTA")
            # find_gravado = cadena.find("GRAVADO")
            # find_gravado_1 = cadena.find("GRAVADA")
            # if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            worksheet.write(row, code_col, round(grand_total.get(code), 2), money_format_b)
            code_col += 1

        name_payslip = self.name
        period = 'Periodo del ' + self.date_start.strftime('%d/%m/%Y') + ' al ' + self.date_end.strftime('%d/%m/%Y')
        worksheet.write(0, 2, company_name, text_bold_left_title)
        worksheet.write(1, 2, name_payslip, text_bold_left_subtitle)
        worksheet.write(1, 5, 'Hora :' + now.strftime("%H:%M:%S"), text_bold_left_paragrah)
        worksheet.write(2, 2, period, text_bold_center_paragrah)
        worksheet.write(2, 5, 'Fecha :' + today.strftime("%d/%m/%Y"), text_bold_left_paragrah)

        #fp = io.BytesIO()
        #workbook.save(fp)
        #fp.seek(0)
        #data = fp.read()
        #fp.close()

        workbook.close()
        output.seek(0)
        data = output.read()

        self.write({'file_data': base64.b64encode(data)})
        action = {
            'name': 'Payslips',
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model=" + self._name + "&id=" + str(
                self.id) + "&field=file_data&download=true&filename=listado_nomina.xlsx",
            'target': 'self',
        }
        return action
        #self.write({'file_data': base64.b64encode(data)})
        #action = {
        #    'name': 'Journal Entries',
        #    'type': 'ir.actions.act_url',
        #    'url': "/web/content/?model=hr.payslip.run&id=" + str(
        #        self.id) + "&field=file_data&download=true&filename=Listado_de_nomina.csv",
        #    'target': 'self',
        #}
        #return action

    def download_csv(self):
        action = {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.attachment&id=" + str(self.l10n_id_attachment_id.id) + "&filename_field=name&field=datas&download=true&name=" + self.l10n_id_attachment_id.name,
            'target': 'self'
        }
        return action

    def download_list_payslip_1(self):
        self._generate_efaktur(',')
        return self.download_csv()

    def download_list_payslip_by_depto(self):
        self._generate_listado_nomina_depto(',')
        return self.download_csv()

    def download_list_payslip_exentos_gravados(self):
        self._generate_listado_exentos_gravados(',')
        return self.download_csv()

    def _generate_efaktur(self, delimiter):
        output_head = self.export_data_list_payslip(delimiter)
        my_utf8 = output_head.encode('iso-8859-3')
        out = base64.b64encode(my_utf8)

        attachment = self.env['ir.attachment'].create({
            'datas': out,
            'name': 'listado_nomina_%s.csv' % (fields.Datetime.to_string(fields.Datetime.now()).replace(" ", "_")),
            'type': 'binary',
        })

        #for record in self:
        #    record.message_post(attachment_ids=[attachment.id])
        self.l10n_id_attachment_id = attachment.id
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _generate_listado_exentos_gravados(self, delimiter):
        output_head = self.export_data_list_payslip_exents_grav(delimiter)
        my_utf8 = output_head.encode('iso-8859-3')
        out = base64.b64encode(my_utf8)

        attachment = self.env['ir.attachment'].create({
            'datas': out,
            'name': 'listado_nomina_exentos_gravados_%s.csv' % (fields.Datetime.to_string(fields.Datetime.now()).replace(" ", "_")),
            'type': 'binary',
        })

        #for record in self:
        #    record.message_post(attachment_ids=[attachment.id])
        self.l10n_id_attachment_id = attachment.id
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def export_data_list_payslip_exents_grav(self, delimiter):
        fk_head = ["Codigo", "Empleado", "Dias Pag", "SD", "SDI", "SBC"]
        fk_sep_footer = ["", "", "", "", "", ""]
        fk_footer = ["Gran Total", "", "", "", "", ""]
        fk_total_footer = ["", "", "", "", "", "Gran Total"]

        #col_nm = 6
        all_column = self.get_all_columns()
        # print("All_columns", all_column)
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        # print("All_col_dict", all_col_dict)
        # print("All_col_list", all_col_list)
        for col in all_col_list:
            # cadena = all_col_dict[col].upper()
            # find_exent = cadena.find("EXENTO")
            # find_exent_1 = cadena.find("EXENTA")
            # find_gravado = cadena.find("GRAVADO")
            # find_gravado_1 = cadena.find("GRAVADA")
            # if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            # print("name right:", all_col_dict[col])
            fk_head.append(self.normalize(all_col_dict[col]))
            fk_sep_footer.append("")
            fk_footer.append("")
            #worksheet.write(3, col_nm, all_col_dict[col], font_format_h)
            #col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            # print("monto", t)
            #worksheet.write(3, col_nm, t, font_format_h)
            fk_head.append(t)
            fk_sep_footer.append("")
            fk_footer.append("")
            #col_nm += 1

        output_head = '%s' % (
            _csv_row(fk_head, delimiter),
        )

        payslip_group_by_payslip_number = self.get_payslip_group_by_payslip_number()
        row = 4
        grand_total = {}
        company_name = ""
        for dept in self.env['hr.employee'].browse(payslip_group_by_payslip_number.keys()).sorted(lambda x: x.name):
            fk_body = []
            # company_name = 'OKAWA MEXICANA SA. DE CV'
            company_name = dept.company_id.name
            # row += 1
            # worksheet.write_merge(row, row, 0, 5, dept.name, text_bold_left)
            total = {}
            # row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_payslip_number[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.no_empleado or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                # print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                # print("value slip", slip)
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
                    #worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                    fk_body.append(slip.employee_id.no_empleado)
                else:
                    fk_body.append("")
                #worksheet.write(row, 1, slip.employee_id.name, font_format)
                fk_body.append(self.normalize(slip.employee_id.name).upper())
                work_day = slip.get_total_work_days()
                #worksheet.write(row, 2, work_day, money_format_n)
                fk_body.append(round(work_day, 2))
                #worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                fk_body.append(round(slip.employee_id.contract_id.sueldo_diario, 2))
                #worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                fk_body.append(round(slip.employee_id.contract_id.sueldo_diario_integrado, 2))
                #worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                fk_body.append(round(slip.employee_id.contract_id.sueldo_base_cotizacion, 2))
                # code_col = 6 + contador
                code_col = 6
                # inicio cambios
                # coincidencias = []
                # for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                # pendientes = list(leave_types.keys() - coincidencias)
                # for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    # print("Name col", all_col_dict[code])
                    # print("codigo_f1", code)
                    # cadena = all_col_dict[code].upper()
                    # find_exent = cadena.find("EXENTO")
                    # find_exent_1 = cadena.find("EXENTA")
                    # find_gravado = cadena.find("GRAVADO")
                    # find_gravado_1 = cadena.find("GRAVADA")
                    # if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                    #worksheet.write(row, code_col, round(amt, 2), money_format)
                    fk_body.append(round(amt, 2))
                    code_col += 1
                #worksheet.write(row, code_col, round(slip.get_total_code_value('001'), 2), money_format)
                fk_body.append(round(slip.get_total_code_value('001'), 2))
                code_col += 1
                #worksheet.write(row, code_col, round(slip.get_total_code_value('002'), 2), money_format)
                fk_body.append(round(slip.get_total_code_value('002'), 2))
                row += 1
                output_head += _csv_row(fk_body, delimiter)
            # worksheet.write_merge(row, row, 0, 5, 'Total Departamento', text_bold_left)
            # code_col = 6 + contador
            # code_col = 6
            # for code in all_col_list:
            #    cadena = all_col_dict[code].upper()
            #    find_exent = cadena.find("EXENTO")
            #    find_exent_1 = cadena.find("EXENTA")
            #    find_gravado = cadena.find("GRAVADO")
            #    find_gravado_1 = cadena.find("GRAVADA")
            #    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            #        worksheet.write(row, code_col, total.get(code), text_bold_right)
            #        code_col += 1
        row += 1
        output_head += _csv_row(fk_sep_footer, delimiter)
        #worksheet.write_merge(row, row, 0, 5, 'Gran Total', font_format_l_b)
        #fk_body.append(round(slip.get_total_code_value('002'), 2))
        # code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            # cadena = all_col_dict[code].upper()
            # find_exent = cadena.find("EXENTO")
            # find_exent_1 = cadena.find("EXENTA")
            # find_gravado = cadena.find("GRAVADO")
            # find_gravado_1 = cadena.find("GRAVADA")
            # if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            #worksheet.write(row, code_col, round(grand_total.get(code), 2), money_format_b)
            fk_total_footer.append(round(grand_total.get(code), 2))
            #code_col += 1
        output_head += _csv_row(fk_total_footer, delimiter)
        return output_head

    def export_data_list_payslip_depto(self, delimiter):
        fk_head = ["Codigo", "Empleado", "Dias Pag", "SD", "SDI", "SBC"]
        fk_sep_footer = ["", "", "", "", "", ""]
        fk_footer = ["Gran Total", "", "", "", "", ""]
        fk_total_footer = ["", "", "", "", "", "Gran Total"]

        all_column = self.get_all_columns()
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        for col in all_col_list:
            cadena = all_col_dict[col].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                # print("name right:", all_col_dict[col])
                fk_head.append(self.normalize(all_col_dict[col]))
                fk_sep_footer.append("")
                fk_footer.append("")
        for t in ['Total Efectivo', 'Total Especie']:
            # print("monto", t)
            fk_head.append(t)
            fk_sep_footer.append("")
            fk_footer.append("")

        output_head = '%s' % (
            _csv_row(fk_head, delimiter),
        )

        # inicio cambios
        # leave_ids = self.env['hr.leave.type'].search([])
        # contador = 0
        # leave_types = {}
        # for leave_id in leave_ids:
        #    worksheet.write(0, 6 + contador, leave_id.name, header_style)
        #    leave_types[leave_id.name] = 6 + contador
        #    contador += 1
        # col_nm = 6 + contador
        # fin cambios

        payslip_group_by_department = self.get_payslip_group_by_department()
        row = 4
        grand_total = {}
        company_name = ''
        for dept in self.env['hr.department'].browse(payslip_group_by_department.keys()).sorted(lambda x: x.name):
            fk_body = []
            # company_name = 'OKAWA MEXICANA SA. DE CV'
            company_name = dept.company_id.name
            row += 1
            #worksheet.write(row, 2, dept.name, font_format_l_b)
            fk_body.append(self.normalize(dept.name).upper())
            output_head += _csv_row(fk_body, delimiter)
            total = {}
            row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_department[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.id or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                # print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                # print("value slip", slip)
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
                fk_body = []
                if slip.state == "cancel":
                    continue
                if slip.employee_id.no_empleado:
                    #worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                    fk_body.append(slip.employee_id.no_empleado)
                else:
                    fk_body.append("")
                #worksheet.write(row, 1, slip.employee_id.name, font_format)
                fk_body.append(self.normalize(slip.employee_id.name).upper())
                work_day = slip.get_total_work_days()
                #worksheet.write(row, 2, work_day, money_format_n)
                fk_body.append(round(work_day, 2))
                #worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                fk_body.append(slip.employee_id.contract_id.sueldo_diario)
                #worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                fk_body.append(slip.employee_id.contract_id.sueldo_diario_integrado)
                #worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                fk_body.append(slip.employee_id.contract_id.sueldo_base_cotizacion)
                # code_col = 6 + contador
                code_col = 6
                # inicio cambios
                # coincidencias = []
                # for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                # pendientes = list(leave_types.keys() - coincidencias)
                # for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    # print("Name col", all_col_dict[code])
                    # print("codigo_f1", code)
                    cadena = all_col_dict[code].upper()
                    find_exent = cadena.find("EXENTO")
                    find_exent_1 = cadena.find("EXENTA")
                    find_gravado = cadena.find("GRAVADO")
                    find_gravado_1 = cadena.find("GRAVADA")
                    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                        #worksheet.write(row, code_col, amt, money_format)
                        fk_body.append(round(amt, 2))
                        code_col += 1
                #worksheet.write(row, code_col, slip.get_total_code_value('001'), money_format)
                fk_body.append(slip.get_total_code_value('001'))
                code_col += 1
                #worksheet.write(row, code_col, slip.get_total_code_value('002'), money_format)
                fk_body.append(slip.get_total_code_value('002'))
                row += 1
                output_head += _csv_row(fk_body, delimiter)
            #worksheet.write(row, 2, 'Total Departamento', font_format_l_b)
            fk_total_depto = ["", "", "", "", "", 'Total Departamento']
            # code_col = 6 + contador
            code_col = 6
            for code in all_col_list:
                cadena = all_col_dict[code].upper()
                find_exent = cadena.find("EXENTO")
                find_exent_1 = cadena.find("EXENTA")
                find_gravado = cadena.find("GRAVADO")
                find_gravado_1 = cadena.find("GRAVADA")
                if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                    fk_total_depto.append(total.get(code))
                    #worksheet.write(row, code_col, total.get(code), money_format_b)
                    code_col += 1

            output_head += _csv_row(fk_total_depto, delimiter)
        row += 1
        output_head += _csv_row(fk_sep_footer, delimiter)
        #worksheet.write(row, 2, 'Gran Total', font_format_l_b)
        #fk_footer
        # code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            cadena = all_col_dict[code].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                #worksheet.write(row, code_col, grand_total.get(code), money_format_b)
                fk_total_footer.append(round(grand_total.get(code), 2))
                code_col += 1

        output_head += _csv_row(fk_total_footer, delimiter)
        return output_head

    def _generate_listado_nomina_depto(self, delimiter):
        output_head = self.export_data_list_payslip_depto(delimiter)
        my_utf8 = output_head.encode('iso-8859-3')
        out = base64.b64encode(my_utf8)

        attachment = self.env['ir.attachment'].create({
            'datas': out,
            'name': 'listado_nomina_depto_%s.csv' % (fields.Datetime.to_string(fields.Datetime.now()).replace(" ", "_")),
            'type': 'binary',
        })

        #for record in self:
        #    record.message_post(attachment_ids=[attachment.id])
        self.l10n_id_attachment_id = attachment.id
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def export_data_list_payslip(self, delimiter):
        fk_head = ["Codigo", "Empleado", "Dias Pag", "SD", "SDI", "SBC"]
        fk_sep_footer = ["", "", "", "", "", ""]
        fk_footer = ["Gran Total", "", "", "", "", ""]
        fk_total_footer = ["", "", "", "", "", "Gran Total"]

        all_column = self.get_all_columns()
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        for col in all_col_list:
            cadena = all_col_dict[col].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                # print("name right:", all_col_dict[col])
                fk_head.append(self.normalize(all_col_dict[col]))
                fk_sep_footer.append("")
                fk_footer.append("")
        for t in ['Total Efectivo', 'Total Especie']:
            # print("monto", t)
            fk_head.append(t)
            fk_sep_footer.append("")
            fk_footer.append("")

        output_head = '%s' % (
            _csv_row(fk_head, delimiter),
        )

        payslip_group_by_payslip_number = self.get_payslip_group_by_payslip_number()
        row = 4
        grand_total = {}
        company_name = ""
        for dept in self.env['hr.employee'].browse(payslip_group_by_payslip_number.keys()).sorted(lambda x: x.name):
            fk_body = []
            # row += 1
            # worksheet.write_merge(row, row, 0, 5, dept.name, text_bold_left)
            total = {}
            # row += 1
            slip_sorted_by_employee = {}
            hr_payslips = []
            for slip in payslip_group_by_payslip_number[dept.id]:
                if slip.employee_id:
                    slip_sorted_by_employee[slip.id] = slip.employee_id.no_empleado or '0'
            for values in sorted(slip_sorted_by_employee.values()):
                val_list = list(slip_sorted_by_employee.values())
                key_list = list(slip_sorted_by_employee.keys())
                # print("key list", slip_sorted_by_employee.keys())
                slip = key_list[val_list.index(values)]
                # print("value slip", slip)
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
                    #worksheet.write(row, 0, slip.employee_id.no_empleado, font_format)
                    fk_body.append(slip.employee_id.no_empleado)
                else:
                    fk_body.append("")
                #worksheet.write(row, 1, slip.employee_id.name, font_format)
                fk_body.append(self.normalize(slip.employee_id.name).upper())
                work_day = slip.get_total_work_days()
                #worksheet.write(row, 2, work_day, money_format_n)
                fk_body.append(round(work_day, 2))
                #worksheet.write(row, 3, slip.employee_id.contract_id.sueldo_diario, money_format)
                fk_body.append(round(slip.employee_id.contract_id.sueldo_diario, 2))
                #worksheet.write(row, 4, slip.employee_id.contract_id.sueldo_diario_integrado, money_format)
                fk_body.append(round(slip.employee_id.contract_id.sueldo_diario_integrado, 2))
                #worksheet.write(row, 5, slip.employee_id.contract_id.sueldo_base_cotizacion, money_format)
                fk_body.append(round(slip.employee_id.contract_id.sueldo_base_cotizacion, 2))
                # code_col = 6 + contador
                code_col = 6
                # inicio cambios
                # coincidencias = []
                # for line in slip.worked_days_line_ids:
                #    if line.code in leave_types:
                #        worksheet.write(row, leave_types[line.code], line.number_of_days, text_right)
                #        coincidencias.append(line.code)
                # pendientes = list(leave_types.keys() - coincidencias)
                # for pendiente in pendientes:
                #    worksheet.write(row, leave_types[pendiente], 0, text_right)
                # fin cambios
                for code in all_col_list:
                    # print("Name col", all_col_dict[code])
                    # print("codigo_f1", code)
                    cadena = all_col_dict[code].upper()
                    find_exent = cadena.find("EXENTO")
                    find_exent_1 = cadena.find("EXENTA")
                    find_gravado = cadena.find("GRAVADO")
                    find_gravado_1 = cadena.find("GRAVADA")
                    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
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
                        #worksheet.write(row, code_col, round(amt, 2), money_format)
                        fk_body.append(round(amt, 2))
                        code_col += 1
                #worksheet.write(row, code_col, round(slip.get_total_code_value('001'), 2), money_format)
                fk_body.append(round(slip.get_total_code_value('001'), 2))
                code_col += 1
                #worksheet.write(row, code_col, round(slip.get_total_code_value('002'), 2), money_format)
                fk_body.append(round(slip.get_total_code_value('002'), 2))
                row += 1
            # worksheet.write_merge(row, row, 0, 5, 'Total Departamento', text_bold_left)
            # code_col = 6 + contador
            # code_col = 6
            # for code in all_col_list:
            #    cadena = all_col_dict[code].upper()
            #    find_exent = cadena.find("EXENTO")
            #    find_exent_1 = cadena.find("EXENTA")
            #    find_gravado = cadena.find("GRAVADO")
            #    find_gravado_1 = cadena.find("GRAVADA")
            #    if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
            #        worksheet.write(row, code_col, total.get(code), text_bold_right)
            #        code_col += 1
            output_head += _csv_row(fk_body, delimiter)
        row += 1

        output_head += _csv_row(fk_sep_footer, delimiter)
        fk_body = []
        #worksheet.write_merge(row, row, 0, 5, 'Gran Total', font_format_l_b)
        # code_col = 6 + contador
        code_col = 6
        for code in all_col_list:
            cadena = all_col_dict[code].upper()
            find_exent = cadena.find("EXENTO")
            find_exent_1 = cadena.find("EXENTA")
            find_gravado = cadena.find("GRAVADO")
            find_gravado_1 = cadena.find("GRAVADA")
            if find_exent == -1 and find_exent_1 == -1 and find_gravado == -1 and find_gravado_1 == -1:
                fk_total_footer.append(round(grand_total.get(code), 2))
                #worksheet.write(row, code_col, round(grand_total.get(code), 2), money_format_b)
                #code_col += 1

        output_head += _csv_row(fk_total_footer, delimiter)
        return output_head

    def normalize(self, s):
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
        )
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s