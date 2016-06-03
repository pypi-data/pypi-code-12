# -*- coding: utf-8 -*-
from ..const import *
from ..util import smart_unicode
from ..const import STRING

def getJSON():
    o = __get_json()

    for (k,v) in o.items():
        if isinstance(v, STRING):
            o[k]=smart_unicode.format_utf8(v)
        if isinstance(v, dict):
            for k2,v2 in v.items():
                if isinstance(v2, STRING):
                    v[k2]=smart_unicode.format_utf8(v2)
                if isinstance(v2, dict):
                    for k3,v3 in v2.items():
                        if isinstance(v3,STRING):
                            v2[k3]=smart_unicode.format_utf8(v3)
    return o

def __get_json():
    return {
        "login": {
            "description": "使用阿里云AccessKey登录"
        },
        "config": {
            "description": "配置管理",
            "detail": "修改配置, 不带参数则查看配置",
            "option": {
                "region": '设置区域, 如:cn-qingdao',
                "osspath": '设置默认OSS路径',
                "locale": '设置语言地域, 可选范围:[zh_CN|en]',
                "image": '设置默认镜像Id',
                "type": "设置默认InstanceType, 运行 '%s it' 可以看到本区域支持的instanceType" % (CMD),
                'version': "设置版本, 支持预发环境使用,版本如: 2015-10-01",
                'god': "使用上帝模式"
            }
        },
        'info': {
            "description": "显示关于batchcompute-cli的信息",
            "latest_version": "最新版本",
            "current_version": "当前版本",
            "has_upgrade": "你可以执行 'pip install -U batchcompute-cli' 来升级",
            "has_upgrade2": "如果提示没有权限, 请使用 'sudo pip install -U batchcompute-cli'"
        },
        "instance_type": {
            "description": '显示资源类型列表.'
        },
        "cluster": {
            "description": '获取集群列表, 获取集群详情.',
            "option": {
                'description': '获取集群描述JSON'
            }
        },
        "job": {
            "description": '获取作业列表, 获取作业,任务详情等.',
            "option": {
                'top': '显示结果集行数, 只在获取作业列表时生效',
                'all': '显示所有结果',
                'state': '获取作业列表时, 按状态过滤, 取值范围: [Running|Stopped|Waiting|Finished|Failed]',
                "id": '获取作业列表时, 按 JobId 模糊查询',
                'name': '获取作业列表时, 按 JobName 模糊查询',
                'description': '获取作业描述JSON'
            }
        },
        'log': {
            'description': '显示作业日志, 或者从oss下载日志保存到本地',
            'option': {
                'dir_path': '指定本地目录用以保存oss日志, 如果没有指定,则显示日志到屏幕',
                'stderr': '只显示stderr日志',
                'stdout': '只显示stdout日志'
            }
        },
        'create_cluster': {
            'description': '创建集群',
            'option': {
                'image': "可选, imageId, 默认: %s" % IMG_ID,
                'type': "可选, instanceType, 更多信息输入 %s it 查看, 默认: %s" % (CMD, INS_TYPE),
                'nodes': "可选, int类型, default: 1",
                'description': "可选, 描述信息, string",
                'userData': "可选, 用户数据, k:v 对,多个逗号隔开, 格式: k:v,k2:v2",
                'disk': """可选, 挂载磁盘, 支持系统盘配置和一块数据盘(可选)的配置,

        使用方法如: "--disk system:ephemeral:40,data:cloud:50:/home/disk1".
        默认只挂载一个系统盘:类型为ephemeral,大小40GB.
        系统盘配置格式: system:<cloud|ephemeral>:<40-500>, 举例: system:cloud:40, 表示系统盘挂载40GB的云盘.
        数据盘配置格式: data:<cloud|ephemeral>:<5-2000>:<mount-point>, 举例: data:cloud:5:/home/disk1, 表示挂载一个5GB的云盘作为数据盘, window下只能挂载到驱动,如E盘:"data:cloud:5:E".
        (注意: 数据盘使用ephemeral的时候,size取值范围限制为:[5-1024]GB).""",
                'show_json': '只显示cluster json不创建'
            }
        },
        'delete_cluster': {
            'description': '删除集群, 支持批量删除',
            'option': {
                'yes': "可选, 不要询问直接删除"
            }
        },
        'update_cluster': {
            'description': '修改集群信息, 目前只支持修改期望机器数',
            'option': {
                'yes': "可选, 不要询问直接修改",
                'nodes': "必选, 期望修改的机器数, 必须为正整数"
            }
        },
        'create_job': {
            'description': '通过 JSON 创建作业',
            'option': {
                'filePath': '本地 JSON 路径'
            }
        },
        'restart_job': {
            'description': '重新启动作业, 支持批量操作',
            'option': {
                'yes': "可选,直接重启作业无需询问"
            }
        },
        'stop_job': {
            'description': '停止作业, 支持批量操作',
            'option': {
                'yes': "可选,直接停止作业无需询问"
            }
        },
        'delete_job': {
            'description': '删除作业, 支持批量操作',
            'option': {
                'yes': "可选,直接删除作业无需询问"
            }
        },
        'update_job': {
            'description': '修改作业, 目前只支持修改优先级',
            'option': {
                'yes': "可选,直接修改无需询问",
                'priority': "必选, 取值范围: 1-1000"
            }
        },
        'submit': {
            'description': '快速提交单个任务的作业',
            'option': {
                'cluster': """可选,可以使一个集群ID或者AutoCluster配置字符串.
                                      默认是一个AutoCluster配置字符串: img=%s:type=%s.
                                      你可以使用一个已经存在的集群ID(type '%s c' for more cluster id),
                                      或者可以使用AutoCluster配置字符串, 格式: img=<imageId>:type=<instanceType>
                                      (imageId可以查看官网帮助文档)
                                      (运行 '%s it' 可以看到本区域支持的instanceType). """ % (
                IMG_ID, INS_TYPE, CMD, CMD),
                'pack': "可选,打包指定目录下的文件,并上传到OSS, 如果没有指定这个选项则不打包不上传",
                'priority': '可选,int类型,指定作业优先级,默认:0\n',
                'timeout': "可选,超时时间(如果实例运行时间超时则失败), 默认: 172800(单位秒,表示2天)",
                'nodes': "可选,需要运行程序的机器数, 默认: 1",
                'description': '可选,设置作业描述',
                'force': "可选,当instance失败时job不失败, 默认:当instance失败时job也失败",
                'env': "可选,设置环境变量, 格式: <k>:<v>[,<k2>:<v2>...]",
                'read_mount': """可选,只读模式挂载配置, 格式: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                      如: oss://bucket/key:/home/admin/ossdir 表示将oss的路径挂载到本地目录""",
                'write_mount': """可选,可写模式挂载配置(任务结束后写到本地目录的文件会被上传到相应的oss_path下),
                                      格式: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                      如: oss://bucket/key:/home/admin/ossdir 表示将oss的路径挂载到本地目录""",
                'mount': """可选,读写模式挂载配置, 格式: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                      如: oss://bucket/key:/home/admin/ossdir 表示将oss的路径挂载到本地目录""",
                'docker': """可选, 使用docker镜像运行, 格式: <image_name>@<storage_oss_path>,
                                      如: localhost:5000/myubuntu@oss://bucket/dockers/
                                      或者: myubuntu@oss://bucket/dockers/""",
                'file': """可选,使用配置文件提交作业,如果你显示指定其他选项,配置文件中的选项会被覆盖""",
                'disk': """可选,挂载磁盘, 只在使用AutoCluster时有效, 支持系统盘配置和一块数据盘(可选)的配置,

                使用方法如: "--disk system:ephemeral:40,data:cloud:50:/home/disk1".
                默认只挂载一个系统盘:类型为ephemeral,大小40GB.
                系统盘配置格式: system:<cloud|ephemeral>:<40-500>, 举例: system:cloud:40, 表示系统盘挂载40GB的云盘.
                数据盘配置格式: data:<cloud|ephemeral>:<5-2000>:<mount-point>, 举例: data:cloud:5:/home/disk1, 表示挂载一个5GB的云盘作为数据盘, window下只能挂载到驱动,如E盘:"data:cloud:5:E".
                (注意: 数据盘使用ephemeral的时候,size取值范围限制为:[5-1024]GB).
                        """,
                'show_json': '只显示json不提交作业'

            }
        },
        'check': {
            'description': "检查job状态以及失败原因"
        },
        'project': {
            'description': '作业工程命令,包括: create, build, submit 等',
            'create': {
                'description': '创建作业工程',
                'option': {
                    'type': """可选, 创建作业工程类型, 默认: empty(python), 取值范围:[empty|python|java|shell]""",
                    'job': '可选, 从一个已有 job_id 创建一个作业工程'
                }
            },
            'build': {
                'description': '编译, 打包 src/ 为 worker.tar.gz.'

            },
            'update': {
                'description': '修改job.json, 可以指定task名称修改, 不指定则修改全部task',
                'option': {
                    'cluster': """可以使一个集群ID或者AutoCluster配置字符串.
                              默认是一个AutoCluster配置字符串: img=%s:type=%s.
                              你可以使用一个已经存在的集群ID(type '%s c' for more cluster id),
                              或者可以使用AutoCluster配置字符串, 格式: img=<imageId>:type=<instanceType>
                              (运行 '%s it' 可以看到本区域支持的instanceType). """
                               % (IMG_ID, INS_TYPE, CMD, CMD),
                    "docker": """可选,使用docker镜像运行, 格式如:<oss_docker_storage_path>:<docker_name>"""
                }
            },
            'submit':{
                'description': '上传worker.tar.gz, 并提交作业'
            },
            'status': {
                'description': '显示工程状态.'
            },
            'add_task': {
                'description': '增加一个任务',
                'detail': "在job.json中增加一个任务节点, 并且在src目录创建一个程序文件(目前只支持python)",
                'option': {
                    'cluster': """可以使一个集群ID或者AutoCluster配置字符串.
                                  默认是一个AutoCluster配置字符串: img=%s:type=%s.
                                  你可以使用一个已经存在的集群ID(type '%s c' for more cluster id),
                                  或者可以使用AutoCluster配置字符串, 格式: img=<imageId>:type=<instanceType>
                                  (运行 '%s it' 可以看到本区域支持的instanceType). """
                               % (IMG_ID, INS_TYPE, CMD, CMD),

                    'docker': 'Docker镜像名, 需要以前缀"localhost:5000/"打tag'
                }
            }
        },
        'oss': {
            'description': 'OSS相关命令: upload, download, mkdir, ls 等.',
            'login': {
                'description': '登录OSS',
            },
            'logout': {
                'description': '登出OSS',
            },
            'pwd': {
                'description': '显示当前osspath',
            },
            'ls': {
                'description': '列出一个osspath下面的目录和文件',
                'option': {
                    'name': '模糊搜索',
                    'top': '显示结果集行数',
                }
            },
            'cat': {
                'description': '打印文件内容',
            },
            'copy': {
                'description': '复制OSS文件或目录',
                'detail': '复制OSS文件或目录, 可以跨域复制, 使用osspath格式: <region>#<osspath>'
            },
            'upload': {
                'description': '上传文件或目录到OSS'
            },
            'download': {
                'description': '下载文件或目录',
                'option': {
                    'recursion': '下载整个目录'
                }
            },
            'delete': {
                'description': '删除OSS上的目录或文件',
                'option': {
                    'yes': '可选,直接删除无需询问'
                 }
            }
        }
    }
