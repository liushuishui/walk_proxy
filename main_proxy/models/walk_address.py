# -*- coding:utf-8 -*-
# -------------------------------------
# 请输入该文件的说明
# -------------------------------------
from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    # phone = fields.Char(index=True)
    province_id = fields.Many2one('walk.province', string='省')
    city_id = fields.Many2one('walk.city', string='市')
    district_id = fields.Many2one('walk.district', string='区/县')
    community_id = fields.Many2one('walk.community', string='社区')
    address = fields.Char(string='街道地址')
    # street 详细地址
    is_default = fields.Boolean('是否为默认地址')
    city_domain_ids = fields.One2many('walk.city', compute='_compute_city_domain_ids')
    district_domain_ids = fields.One2many('walk.district', compute='_compute_district_domain_ids')
    # wx_address = fields.Char(string='地址')
    # wx_name = fields.Char(string='门牌号')
    # latitude = fields.Char(string='纬度')
    # longitude = fields.Char(string='经度')

    @api.onchange('province_id')
    def _onchange_province_id(self):
        self.city_domain_ids = self.province_id.child_ids if self.province_id else False
        self.city_id = False
        self.district_id = False
        return {
            'domain': {
                'city_id': [('id', 'in', self.city_domain_ids.ids if self.city_domain_ids else [0])]
            }
        }

    @api.onchange('city_id')
    def _onchange_city_id(self):
        self.district_domain_ids = self.city_id.child_ids if self.city_id else False
        self.district_id = False
        return {
            'domain': {
                'district_id': [('id', 'in', self.district_domain_ids.ids if self.district_domain_ids else [0])]
            }
        }

    @api.depends('province_id')
    def _compute_city_domain_ids(self):
        self.city_domain_ids = self.province_id.child_ids if self.province_id else False

    @api.depends('city_id')
    def _compute_district_domain_ids(self):
        self.district_domain_ids = self.city_id.child_ids if self.city_id else False


class WalkProvince(models.Model):

    _name = 'walk.province'
    _description = '省份'

    name = fields.Char('名称')
    child_ids = fields.One2many('walk.city', 'pid', string='市')

    @api.model_cr
    def init(self):
        from ..data.location_data import province_init_sql
        self.env.cr.execute(province_init_sql)


class WalkCity(models.Model):

    _name = 'walk.city'
    _description = u'城市'

    pid = fields.Many2one('walk.province', string='省份')
    name = fields.Char('名称')
    child_ids = fields.One2many('walk.district', 'pid', string='区')


    @api.model_cr
    def init(self):
        from ..data.location_data import city_init_sql
        self.env.cr.execute(city_init_sql)


class WalkDistrict(models.Model):

    _name = 'walk.district'
    _description = u'区'

    pid = fields.Many2one('walk.city', string='城市')
    name = fields.Char('名称')
    child_ids = fields.One2many('walk.community', 'pid', string='社区')

    @api.model_cr
    def init(self):
        from ..data.location_data import district_init_sql
        self.env.cr.execute(district_init_sql)


class WalkCommunity(models.Model):
    _name = 'walk.community'
    _description = '社区'

    pid = fields.Many2one('walk.district', string='区/县')
    name = fields.Char(string='名称')
