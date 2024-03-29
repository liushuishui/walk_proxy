# -*- coding:utf-8 -*-
# -------------------------------------
# 请输入该文件的说明
# -------------------------------------
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WalkConfig(models.Model):
    _name = 'walk.config'
    _description = '对接设置'
    _rec_name = 'mall_name'

    sub_domain = fields.Char('接口前缀', help='商城访问的接口url前缀', index=True, required=True)
    mall_name = fields.Char('商城名称', help='显示在顶部')
    app_id = fields.Char('appid')
    secret = fields.Char('secret')
    # team_id = fields.Many2one('crm.team', string='所属销售渠道', required=True)

    def get_config(self, key):
        if key == 'mallName':
            key = 'mall_name'
        if hasattr(self, key):
            return self.__getattribute__(key)
        return

    @api.model
    def get_entry(self, sub_domain):
        # if sub_domain in ('h5',):
        #     entry = self.env.ref('oejia_weshop.wxapp_config_data_1')
        #     entry._platform = sub_domain
        #     return entry
        config = self.search([('sub_domain', '=', sub_domain)], limit=1)
        if config:
            config._platform = 'wxapp'
            return config
        return False

    # @api.model
    # def get_from_team(self, team_id):
    #     config = self.search([('team_id', '=', team_id)])
    #     if config:
    #         config.ensure_one()
    #         return config
    #     return False

    @api.multi
    def clean_all_token(self):
        self.env['walk.access.token'].search([]).unlink()

    @api.multi
    def clean_all_token_window(self):
        pass
    #     new_context = dict(self._context) or {}
    #     new_context['default_info'] = '确认将所有会话 token 清除？'
    #     new_context['default_model'] = 'walk.config'
    #     new_context['default_method'] = 'clean_all_token'
    #     new_context['record_ids'] = [obj.id for obj in self]
    #     return {
    #         'name': '确认清除',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'wxapp.confirm',
    #         'res_id': None,
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'context': new_context,
    #         'view_id': self.env.ref('oejia_weshop.confirm_view_form').id,
    #         'target': 'new'
    #     }

    def get_level(self):
        return 0

    def get_ext_config(self):
        return {}
