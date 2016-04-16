# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from optionaldict import optionaldict

from wechatpy.client.api.base import BaseWeChatAPI


class WeChatAgent(BaseWeChatAPI):

    def get(self, agent_id):
        """
        获取企业号应用
        详情请参考 http://qydev.weixin.qq.com/wiki/index.php?title=获取企业号应用

        :param agent_id: 授权方应用 id
        :return: 返回的 JSON 数据包
        """
        return self._get(
            'agent/get',
            params={
                'agentid': agent_id
            }
        )

    def set(self,
            agent_id,
            name=None,
            description=None,
            redirect_domain=None,
            logo_media_id=None,
            report_location_flag=0,
            is_report_user=True,
            is_report_enter=True):
        """
        设置企业号应用
        详情请参考 http://qydev.weixin.qq.com/wiki/index.php?title=设置企业号应用

        :param agent_id: 企业应用的 id
        :param name: 企业应用名称
        :param description: 企业应用详情
        :param redirect_domain: 企业应用可信域名
        :param logo_media_id: 企业应用头像的mediaid，通过多媒体接口上传图片获得mediaid
        :param report_location_flag: 企业应用是否打开地理位置上报 0：不上报；1：进入会话上报；2：持续上报
        :param is_report_user: 是否接收用户变更通知
        :param is_report_enter: 是否上报用户进入应用事件
        :return: 返回的 JSON 数据包
        """
        agent_data = optionaldict()
        agent_data['agentid'] = agent_id
        agent_data['name'] = name
        agent_data['description'] = description
        agent_data['redirect_domain'] = redirect_domain
        agent_data['logo_mediaid'] = logo_media_id
        agent_data['report_location_flag'] = report_location_flag
        agent_data['isreportuser'] = 1 if is_report_user else 0
        agent_data['isreportenter'] = 1 if is_report_enter else 0
        return self._post(
            'agent/set',
            data=agent_data
        )

    def list(self):
        """
        获取应用概况列表
        详情请参考
        http://qydev.weixin.qq.com/wiki/index.php?title=获取应用概况列表

        :return: 应用概况列表
        """
        res = self._get('agent/list')
        return res['agentlist']
