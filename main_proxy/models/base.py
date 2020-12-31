# -*- coding:utf-8 -*-
# -------------------------------------
# 模型的mix-in
# -------------------------------------

RegisterType = [
    ('app', '小程序'),
    ('gzh', '公众号')
]


class DataProxy:
    def get_image_url(self, url, model, id, field):
        image_url = '{url}/web/image/{model}/{id}/{field}'.format(
            url=url,
            model=model,
            id=id,
            field=field
        )
        return image_url



