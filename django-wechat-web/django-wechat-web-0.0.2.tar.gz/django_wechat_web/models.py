from __future__ import unicode_literals

from django.db import models

class WechatWebModel(models.Model):
    '''
        DOC: http://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140842&token=&lang=zh_CN
        @param openid   judge user
        @param unionid  judge user whether focus or not
    '''
    openid      = models.CharField(max_length=255, unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    # detail info
    nickname    = models.CharField(max_length=255, null=True)
    sex         = models.CharField(max_length=1, null=True)
    province    = models.CharField(max_length=255, null=True)
    city        = models.CharField(max_length=255, null=True)
    country     = models.CharField(max_length=255, null=True)
    headimgurl  = models.CharField(max_length=255, null=True)
    privilege   = models.CharField(max_length=1024, null=True)
    unionid     = models.CharField(max_length=255, null=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '{0} {1}'.format(self.openid, self.nickname)
