# -*- coding:utf-8 -*-
# -------------------------------------
# 请输入该文件的说明
# -------------------------------------
from odoo import fields, models, api
from .base import DataProxy


class ProductTemplateInherit(models.Model, DataProxy):
    _inherit = 'product.template'

    image_url = fields.Char(
        string='首图链接',
        compute='_compute_image',
    )

    @api.depends('image_medium')
    def _compute_image(self):
        url = self.env['ir.config_parameter'].get_param('web.base.url')
        for rec in self:
            rec.image_url = self.get_image_url(
                url=url,
                model='product.template',
                id=rec.id,
                field='image_medium'
            )