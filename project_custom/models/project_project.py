# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"


    def _compute_stage_id(self):
        for proyecto in self:
            if not proyecto.stage_id:
                proyecto.stage_id = self.env.ref('project_custom.project_project_estado_1')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_id1 = self.env.ref('project_custom.project_project_estado_1')
        stage_id2 = self.env.ref('project_custom.project_project_estado_2')
        stage_id3 = self.env.ref('project_custom.project_project_estado_3')
        stage_id4 = self.env.ref('project_custom.project_project_estado_4')
        stage_id5 = self.env.ref('project_custom.project_project_estado_5')
        return stage_id1 + stage_id2 + stage_id3 + stage_id4 + stage_id5

    stage_id = fields.Many2one(
        comodel_name='project.project.estado',
        string='Estado KUH7',
        index=True,
        tracking=True,
        compute='_compute_stage_id',
        readonly=False,
        store=True,
        copy=False,
        group_expand='_read_group_stage_ids',
        ondelete='restrict',
        default=lambda self: self.env.ref('project_custom.project_project_estado_1'),
    )


class ProjectProjectEstado(models.Model):
    _name = "project.project.estado"

    name = fields.Char(string='Nombre')
