# -*- coding:utf-8 -*-
# -------------------------------------
# 产品相关接口
# -------------------------------------
from odoo import http
from odoo.exceptions import MissingError

from .base import DataProxy

import logging

_logger = logging.getLogger(__name__)


class WalkProductApi(http.Controller, DataProxy):
    @http.route('/walk/<string:sub_domain>/cate/list', auth='public', methods=['GET'])
    def get_category(self, **kw):
        """
        一级分类或某分类下的子分类
        :param kw:
            parentId: 父分类id
        :return:
        """
        try:
            _logger.info('== get_category params: %s' % kw)
            parent_id = kw.get('parentId')
            if parent_id:
                domain = [('parent_id', '=', int(parent_id))]
            else:
                domain = [('parent_id', '=', False)]
            cate = self.get_model('product.public.category').search(domain, order='sequence desc')
            if not cate:
                return self.res_ok([])
            data = [
                self.get_cate_data(each)
                for each in cate
            ]
            return self.res_ok(data)
        except ValueError:
            return self.res_err(1001)
        except Exception as e:
            _logger.error('== get_category error: %s' % str(e))
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/product/list', auth='public', methods=['GET'])
    def get_product(self, **kw):
        """
        获取指定分类下的商品/或获取所有商品列表
        :param kw:
            cateId: 分类id
        :return:
        """
        try:
            _logger.info('== get_product params: %s' % kw)
            cate_id = kw.get('cateId')
            page = kw.get('page', 1)
            size = kw.get('size', 20)
            domain = [('sale_ok', '=', True)]
            if cate_id:
                category = self.get_model('product.public.category').browse(int(cate_id))
                domain.append(('public_categ_ids', 'in', [int(cate_id)] + category.child_id.ids))
            product = self.get_model('product.template').search(
                domain, limit=size,
                offset=(page - 1) * size
            )
            if not product:
                return self.res_ok([])
            data = [
                self.get_product_data(each)
                for each in product
            ]
            return self.res_ok(data)
        except MissingError:
            _logger.error('== get_product category id not found: %s' % kw.get('cateId'))
            return self.res_ok([])
        except ValueError:
            return self.res_err(1001)
        except Exception as e:
            _logger.error('== get_product error: %s' % str(e))
            return self.res_err(-1)

    @http.route('/walk/<string:sub_domain>/product/detail', auth='public', methods=['GET'])
    def get_product_detail(self, **kw):
        """
        传入模板id，返回商品详情
        :param kw:
            productId: 模板id
        :return:
        """
        try:
            _logger.error('== get_product_detail info: %s' % kw)
            product_id = kw.get('productId')
            if not product_id:
                return self.res_err(300)
            product = self.get_model('product.template').browse(int(product_id))
            if not product:
                return self.res_ok([])
            return self.res_ok(self.get_product_data(product))
        except MissingError:
            _logger.error('== get_product_detail product id not found: %s' % kw.get('productId'))
            return self.res_ok([])
        except ValueError:
            return self.res_err(1001)
        except Exception as e:
            _logger.error('== get_product_detail error: %s' % str(e))
            return self.res_err(-1)