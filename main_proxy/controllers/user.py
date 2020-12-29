# -*- coding:utf-8 -*-
# -------------------------------------
# 请输入该文件的说明
# -------------------------------------
from odoo import http
from odoo.http import request
from odoo import fields

from .base import DataProxy
from .weixin_proxy import get_wx_session_info, get_wx_user_info, get_decrypt_info

import logging

_logger = logging.getLogger(__name__)


class WalkUserApi(http.Controller, DataProxy):
    @http.route('/walk/<string:sub_domain>/user/register', auth='public', methods=['POST'], csrf=False)
    def register(self, sub_domain, code=None, encryptedData=None, iv=None, **kwargs):
        """
        微信用户授权注册
        :param sub_domain:
        :param code:
        :param encryptedData:
        :param iv:
        :param kwargs:
        :return:
        """
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:
                return ret

            encrypted_data = encryptedData
            if not code and encrypted_data and iv:
                return self.res_err(300)

            app_id = entry.get_config('app_id')
            secret = entry.get_config('secret')
            if not app_id or not secret:
                return self.res_err(404)
            session_key, user_info = get_wx_user_info(app_id, secret, code, encrypted_data, iv)
            user_id = None
            if hasattr(request, 'user_id'):
                user_id = request.user_id
            value = {
                'name': user_info['nickName'],
                'nickname': user_info['nickName'],
                'open_id': user_info['openId'],
                'gender': user_info['gender'],
                'language': user_info['language'],
                'country': user_info['country'],
                'province': user_info['province'],
                'city': user_info['city'],
                'avatar_url': user_info['avatarUrl'],
                'register_ip': request.httprequest.remote_addr,
                'user_id': user_id,
                'partner_id': user_id and request.env['res.users'].sudo().browse(user_id).partner_id.id or None,
            }
            if user_id:
                value['user_id'] = user_id
                value['partner_id'] = self.get_model('res.users').browse(user_id).partner_id.id
                value.pop('name')
            user = self.get_model('walk.users').create(value)
            request.wechat_user = user
            request.entry = entry
            return self.res_ok()
        except AttributeError:
            return self.res_err(404)
        except Exception as e:
            _logger.error(str(e))
            return self.res_err(-1, str(e))

    @http.route('/walk/<string:sub_domain>/user/login', auth='public', methods=['POST'], csrf=False)
    def login(self, sub_domain, code=None, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:
                return ret

            app_id = entry.get_config('app_id')
            secret = entry.get_config('secret')
            if not app_id or not secret:
                return self.res_err(300)

            session_info = get_wx_session_info(app_id, secret, code)
            if session_info.get('errcode'):
                return self.res_err(-1, session_info.get('errmsg'))
            open_id = session_info['openid']
            user = self.get_model('walk.users').search(
                [('open_id', '=', open_id)]
            )
            if not user:
                return self.res_err(10000)
            user.write({'last_login': fields.Datetime.now(), 'ip': request.httprequest.remote_addr})
            access_token = self.get_model('walk.access.token').search(
                [('open_id', '=', open_id)]
            )
            if not access_token:
                session_key = session_info['session_key']
                access_token = self.get_model('walk.access.token').create(
                    {
                        'open_id': open_id,
                        'session_key': session_key,
                        'sub_domain': sub_domain
                    }
                )
            else:
                access_token.write({'session_key': session_info['session_key']})
            data = {
                'token': access_token.token,
                'uid': user.id,
                'info': self.get_user_info(user)
            }
            return self.res_ok(data)
        except Exception as e:
            _logger.error(str(e))
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/user/check-token', auth='public', methods=['GET'])
    def check_token(self, sub_domain, token=None, **kwargs):
        try:
            res, user, entry = self._check_user(sub_domain, token)
            if res:
                return res
            data = self.get_user_info(user)
            return self.res_ok(data)
        except Exception as e:
            _logger.error(e)
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/user/detail', auth='public', methods=['GET'])
    def detail(self, sub_domain, token=None):
        try:
            res, user, entry = self._check_user(sub_domain, token)
            if res:
                return res
            data = self.get_user_info(user)
            return self.res_ok(data)
        except Exception as e:
            _logger.error(e)
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/user/bind-mobile', auth='public', methods=['POST'], csrf=False)
    def bind_mobile(self, sub_domain, token=None, encryptedData=None, iv=None, **kwargs):
        try:
            res, user, entry = self._check_user(sub_domain, token)
            if res:
                return res
            encrypted_data = encryptedData
            if not token and encrypted_data and iv:
                return self.res_err(300)

            app_id = entry.get_config('app_id')
            secret = entry.get_config('secret')
            if not app_id or not secret:
                return self.res_err(404)

            access_token = self.get_model('walk.access.token').search(
                [('token', '=', token)]
            )
            if not access_token:
                return self.res_err(901)
            session_key = access_token[0].session_key
            _logger.info('>>> decrypt: %s %s %s %s', app_id, session_key, encrypted_data, iv)
            user_info = get_decrypt_info(app_id, session_key, encrypted_data, iv)
            _logger.info('>>> bind_mobile: %s', user_info)
            user.write({'phone': user_info.get('phoneNumber')})
            user.partner_id.write({'mobile': user_info.get('phoneNumber')})
            return self.res_ok()
        except Exception as e:
            _logger.error(e)
            return self.res_err(-1)
