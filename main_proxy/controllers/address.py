# -*- coding:utf-8 -*-
# -------------------------------------
# 用户地址相关；筛选、新增、编辑、删除
# -------------------------------------
from odoo import http
# from odoo.http import request

from .base import DataProxy

import logging
_logger = logging.getLogger(__name__)


class WalkAddressApi(http.Controller, DataProxy):
    @http.route('/walk/<string:sub_domain>/address/province', auth='public', methods=['GET'])
    def get_all_province(self, **kw):
        """
        获取省份
        :param kw:
        :return:
        """
        province = self.get_model('walk.province').search([], order='id asc')
        if not province:
            return self.res_ok([])
        data = self.get_province_data(province)
        return self.res_ok(data)

    @http.route('/walk/<string:sub_domain>/address/city', auth='public', methods=['GET'])
    def get_all_city(self, **kw):
        """
        获取某省份下的城市
        :param kw:
            provinceId: 省份id
        :return:
        """
        try:
            _logger.info('== get_all_city params: %s' % kw)
            province_id = kw.get('provinceId')
            if not province_id:
                return self.res_err(300)
            city = self.get_model('walk.province').browse(int(province_id)).child_ids
            if not city:
                return self.res_ok([])
            data = self.get_city_data(city)
            return self.res_ok(data)
        except ValueError:
            return self.res_err(1001)
        except Exception as e:
            _logger.error('== get_all_city error: %s' % str(e))
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/address/district', auth='public', methods=['GET'])
    def get_all_district(self, **kw):
        """
        获取某城市下的区/县
        :param kw:
            cityId: 城市id
        :return:
        """
        try:
            _logger.info('== get_all_district params: %s' % kw)
            city_id = kw.get('cityId')
            if not city_id:
                return self.res_err(300)
            district = self.get_model('walk.city').browse(int(city_id)).child_ids
            if not district:
                return self.res_ok([])
            data = self.get_district_data(district)
            return self.res_ok(data)
        except ValueError:
            return self.res_err(1001)
        except Exception as e:
            _logger.error('== get_all_district error: %s' % str(e))
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/address/community', auth='public', methods=['GET'])
    def get_all_community(self, **kw):
        """
        获取某区/县下的社区
        :param kw:
            districtId: 区/县id
        :return:
        """
        try:
            _logger.info('== get_all_community params: %s' % kw)
            district_id = kw.get('districtId')
            if not district_id:
                return self.res_err(300)
            community = self.get_model('walk.district').browse(int(district_id)).child_ids
            if not community:
                return self.res_ok([])
            data = self.get_community_data(community)
            return self.res_ok(data)
        except ValueError:
            return self.res_err(1001)
        except Exception as e:
            _logger.error('== get_all_community error: %s' % str(e))
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/address/create', auth='public', methods=['POST'], csrf=False)
    def create_address(self, **kw):
        """
        新建地址
        :param kw:
            token: 用户身份令牌
            community_id: 社区id
            name: 收件人姓名
            phone: 手机号
            address: 门牌号
            is_default: 是否默认
        :return:
        """
        try:
            _logger.info('== create_address params: %s' % kw)
            community_id = kw.get('communityId')
            token = kw.get('token')
            phone = kw.get('phone')
            name = kw.get('name')
            address = kw.get('address')
            is_default = kw.get('isDefault')
            if not token or not community_id or not phone or not name or not address:
                return self.res_err(300)
            user = self._check_token(token)
            if not user:
                return self.res_err(901)

            community = self.get_model('walk.community').browse(int(community_id))
            if not community:
                return self.res_err(1002)

            self.get_model('res.partner').create({
                'name': name,
                'type': 'delivery',
                'province_id': community.pid.pid.pid.id,
                'city_id': community.pid.pid.id,
                'district_id': community.pid.id,
                'community_id': community.id,
                'address': address,
                'phone': phone,
                'is_default': True if is_default else False,
                'parent_id': user.partner_id.id
            })
            return self.res_ok()
        except ValueError:
            return self.res_err(1001)
        except Exception as e:
            _logger.error('== create_address error: %s' % str(e))
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/address/list', auth='public', methods=['GET'])
    def get_address_list(self, **kw):
        """
        获取当前用户地址列表
        :param kw:
            token: 用户身份令牌
        :return:
        """
        _logger.info('== get_address_list params: %s' % kw)
        token = kw.get('token')
        if not token:
            return self.res_err(300)

        user = self._check_token(token)
        if not user:
            return self.res_err(901)

        address = user.address_ids

        if not address:
            return self.res_ok([])

        data = [
            self.get_address_data(each)
            for each in address
        ]
        return self.res_ok(data)

    @http.route('/walk/<string:sub_domain>/address/test', auth='public', methods=['GET'])
    def address_test(self, **kw):
        _logger.info('== address_test params: %s' % kw)
        token = kw.get('token')
        if not token:
            return self.res_err(300)
        user = self._check_token(token)
        if not user:
            return self.res_err(901)

        print(user)
        print(user.partner_id)

        # community = self.get_model('walk.community').browse(int(community_id))
        # if not community:
        #     return self.res_err(1002)
        #
        # self.get_model('res.partner').create({
        #     'name': name,
        #     'type': 'delivery',
        #     'province_id': community.pid.pid.pid,
        #     'city_id': community.pid.pid,
        #     'district_id': community.pid,
        #     'community_id': community.id,
        #     'address': address,
        #     'phone': phone,
        #     'is_default': True if is_default else False,
        #     'parent_id': user.parent_id.id
        # })
        # return self.res_ok()
