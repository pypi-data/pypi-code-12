# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/26.
import six


def title_in_content(title, content):
    """
    基于title文本扫描分析标题
    假设所有标题必会在内容中出现
    :return:
    """
    if title and content and isinstance(title, six.string_types):
        title = title.strip()
        for i in range(len(title)):
            exact_title = title[0:-i - 1]
            if exact_title and exact_title in content:
                title = exact_title
                break
    return title