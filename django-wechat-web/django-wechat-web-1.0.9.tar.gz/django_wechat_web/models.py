from __future__ import unicode_literals

from django.db import models

class WechatBase(models.Model):
    '''
        DOC: http://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140842&token=&lang=zh_CN
        @param openid   judge user
        @param unionid  judge user whether focus or not
    '''
    openid      = models.CharField(max_length=255, unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '{0}'.format(self.openid)

    def json(self):
        return {
            'id': self.pk,
            'openid': self.openid,
            'created_at': self.created_at,
        }

class WechatUserInfoManager(models.Manager):
    def empty_json(self):
        return {
            'nickname': '',
            'sex': '',
            'province': '',
            'city': '',
            'country': '',
            'headimgurl': '',
            'privilege': '',
            'unionid': '',
            'created_at': '',
        }

class WechatUserInfo(models.Model):
    wechatbase  = models.OneToOneField(WechatBase, on_delete=models.CASCADE)
    # detail info
    openid      = models.CharField(max_length=255, unique=True)
    nickname    = models.CharField(max_length=255, null=True)
    sex         = models.CharField(max_length=1, null=True)
    province    = models.CharField(max_length=255, null=True)
    city        = models.CharField(max_length=255, null=True)
    country     = models.CharField(max_length=255, null=True)
    headimgurl  = models.CharField(max_length=255, null=True)
    privilege   = models.CharField(max_length=1024, null=True)
    unionid     = models.CharField(max_length=255, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    objects = WechatUserInfoManager()

    def __str__(self):
        return '{0} - {1}'.format(self.wechatbase.openid, self.nickname)

    class Meta:
        ordering = ['-created_at']

    def json(self):
        return {
            'nickname': self.nickname,
            'sex': self.sex,
            'province': self.province,
            'city': self.city,
            'country': self.country,
            'headimgurl': self.headimgurl,
            'privilege': self.privilege,
            'unionid': self.unionid,
            'created_at': self.created_at,
        }
