# -*- coding:utf-8 -*-
# -------------------------------------
# 请输入该文件的说明
# -------------------------------------
from odoo import fields
from odoo.http import request
from odoo.loglevels import ustr

import json
from datetime import date, datetime
import time
import pytz
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import logging

_logger = logging.getLogger(__name__)

error_code = {
    -99: '',
    -2: '用户名或密码不正确',
    -1: '服务器内部错误',
    0: 'success',
    403: '禁止访问',
    405: '错误的请求类型',
    501: '数据库错误',
    502: '并发异常，请重试',
    600: '缺少参数',
    601: '无权操作:缺少 token',
    602: '签名错误',
    700: '暂无数据',
    701: '该功能暂未开通',
    702: '资源余额不足',
    901: '登录超时',
    902: '登录超时',
    300: '缺少参数',
    400: '域名错误',
    401: '该域名已删除',
    402: '该域名已禁用',
    404: '暂无数据',
    10000: '微信用户未注册'
}


def json_default(obj):
    """
    Properly serializes date and datetime objects.
    """
    if isinstance(obj, date):
        if isinstance(obj, datetime):
            return fields.Datetime.to_string(obj)
        return fields.Date.to_string(obj)
    return ustr(obj)


class BaseController(object):
    def _check_domain(self, sub_domain):
        wxapp_entry = request.env['walk.config'].sudo().search([('sub_domain', '=', sub_domain)])
        if not wxapp_entry:
            return self.res_err(404), None
        return None, wxapp_entry[0]

    def _check_token(self, token):
        user_info = request.env["walk.access.token"].sudo().check_user(token)
        if not user_info:
            return None
        union_id = user_info.get('union_id')

        if token:
            wx_info = request.env["qs.member.info"].sudo().search([("union_id", "=", union_id)])
            return wx_info.wxapp_open_id
        return None

    def _check_get_union_id(self, token):
        user_info = request.env["member.access_token"].sudo().check_user(token)
        if not user_info:
            return None
        union_id = user_info.get('union_id')

        if token:
            wx_info = request.env["qs.member.info"].sudo().search([("union_id", "=", union_id)])
            return wx_info.union_id
        return None

    def _check_params(self, sub_domain, token):
        ret, entry = self._check_domain(sub_domain)
        if ret:
            return ret
        if not token:
            return self.res_err(-1)
        token_info = self._check_token(token)
        if not token_info:
            return self.res_err(-1)

    def _check_user(self, sub_domain, token):
        wxapp_entry = request.env['walk.config'].sudo().search([('sub_domain', '=', sub_domain)])
        if not wxapp_entry:
            return self.res_err(404), None, wxapp_entry

        wxapp_entry = wxapp_entry[0]
        if not token:
            return self.res_err(300), None, wxapp_entry

        if request.uid != request.env.ref('base.public_user').id:
            if str(request.uid) == token:  # request.session.sid==token:
                _logger.info('>>> login user %s', request.env.user)
                return None, WechatUser(request.env.user.partner_id, request.env.user), wxapp_entry

        user_info = request.env['member.access_token'].sudo().check_user(token)
        if not user_info:
            return self.res_err(901), None, wxapp_entry
        union_id = user_info.get('union_id')

        member = request.env['qs.member.info'].sudo().search([
            ('union_id', '=', union_id),
            # ('create_uid', '=', user.id)
        ])

        if not member:
            return self.res_err(10000), None, wxapp_entry

        request.wechat_user = member
        return None, member, wxapp_entry

    def check_userid(self, token, userid):
        if token and userid:
            user_info = request.env(user=1)['member.access_token'].check_user(token)

            if not user_info:
                return
            union_id = user_info.get('union_id')
            member = request.env(user=1)['qs.member.info'].search([
                ('union_id', '=', union_id),
            ])
            if not member:
                return

            if hasattr(member, 'user_id') and str(member.user_id.id) == str(userid):
                request.wechat_user = member

    def res_ok(self, data=None):
        ret = {'code': 0, 'msg': 'success'}
        if data != None:
            ret['data'] = data
        return request.make_response(
            headers={'Content-Type': 'json'},
            data=json.dumps(ret, default=json_default)
        )

    def res_err(self, code, data=None):
        ret = {'code': code,
               'msg': error_code.get(code) or data}
        if data:
            ret['data'] = data
        return request.make_response(json.dumps(ret))


class DataProxy(BaseController):
    def get_model(self, model_name=None):
        return request.env(user=1)[model_name].sudo()

    # ##############
    # 用户注册相关   #
    # ##############

    def get_user_info(self, user):
        if hasattr(user, 'phone'):
            mobile = user.phone
        else:
            mobile = user.partner_id.mobile
        data = {
            'base': {
                'mobile': mobile or '',
                'userid': ''
            }
        }
        return data
