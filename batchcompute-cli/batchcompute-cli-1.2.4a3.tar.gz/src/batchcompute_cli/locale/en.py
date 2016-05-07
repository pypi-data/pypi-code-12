# -*- coding: utf-8 -*-
from ..const import *


def getJSON():
    return {
        "login": {
            "description": "login with Aliyun AccessKey"
        },
        "config": {
            "description": "read and write configurations",
            "detail": "set configurations, show configurations if no options",
            "option": {
                "region": 'set region, example: cn-qingdao',
                "osspath": 'set default oss path',
                "locale": 'set locale, scope:[zh_CN|en]',
                "image": 'set default image Id ',
                "type": "set default InstanceType, type '%s it' for more instanceType" % (CMD),
                'version': "set version for stg environment, example: 2015-10-01",
                "god": "use god mode"
            }
        },
        'info': {
            "description": "show information of batchcompute-cli",
            "latest_version": "Latest version",
            "current_version": "Current version",
            "has_upgrade": "Type 'pip install -U batchcompute-cli' to upgrade",
            "has_upgrade2":  "If fails with permission deny, try 'sudo pip install -U batchcompute-cli'"
        },
        "instance_type": {
            "description": 'show instance type list.'
        },
        "cluster": {
            "description": 'show cluster list, show cluster detail.',
            "option": {
                'description': 'show description of the cluster'
            }
        },
        "job": {
            "description": 'show job list, show detail of job and task',
            "option": {
                'top': 'length of result-set to show, works only in list jobs',
                'all': 'show all jobs',
                'state': 'state filter for listing jobs, scope: [Running|Stopped|Waiting|Finished|Failed]',
                "id": 'jobId filter for listing jobs',
                'name': 'jobName filter for listing jobs',
                'description': 'show description of the job'
            }
        },
        'log': {
            'description': 'print logs, or download them from oss to local directory',
            'option': {
                'dir_path': 'directory path to save logs, if your don\'t set this option, just print logs',
                'stderr': 'show stderr log only',
                'stdout': 'show stdout log only'
            }
        },
        'create_cluster': {
            'description': 'create cluster',
            'option': {
                'image': "optional, imageId, default: %s" % IMG_ID,
                'type': "optional, instanceType, type '%s it' for more, default: %s" % (CMD, INS_TYPE),
                'nodes': "optional, int, default: 1",
                #'groups': "optional, format: <groupName>[:type=<instanceType>][:nodes=<instanceCount>], default:group1",
                'description': "optional, description, string",
                'userData': "optional, user data k-v pairs, exp: a:b,c:e",
                'disk': """optional, mount system disk and a data disk(optional),

        Usage: "--disk system:ephemeral:40,data:cloud:50:/home/disk1".
        Default: system:ephemeral:40, mount 40GB ephemeral disk as system disk.
        System disk config format: system:<cloud|ephemeral>:<40-500>, example: system:cloud:40, mount 40GB ephemeral disk as system disk.
        Data disk config format: data:<cloud|ephemeral>:<5-2000>:<mount-point>, example: data:cloud:5:/home/disk1, mount a 5GB cloud disk as data disk, in windows must mount to driver, such as E driver, like: "data:cloud:5:E". (Attention please: Using ephemeral disk as data disk, the size scope should limit to [5-1024]GB).""",
                'show_json': 'optional, just output cluster json, don\'t create a cluster, default: false'
            }
        },
        'delete_cluster': {
            'description': 'delete cluster, multi-supported',
            'option': {
                'yes': "optional, delete in silent mode"
            }
        },
        'update_cluster': {
            'description': 'update cluster, only support updating DesiredVMCount currently',
            'option': {
                'yes': "optional, update in silent mode",
                'nodes': "required, should be positive integer"
            }
        },
        'create_job': {
            'description': 'create job from description json or a json file path.',
            'option': {
                'filePath': 'local job description json file path'
            }
        },
        'restart_job': {
            'description': 'restart jobs, multi-supported',
            'option': {
                'yes': "optional, restart jobs in silent mode"
            }
        },
        'stop_job': {
            'description': 'stop jobs, multi-supported',
            'option': {
                'yes': "optional, stop jobs in silent mode"
            }
        },
        'delete_job': {
            'description': 'delete jobs, multi-supported',
            'option': {
                'yes': "optional, delete jobs in silent mode"
            }
        },
        'update_job': {
            'description': 'update job, only support update priority currently',
            'option': {
                'yes': "optional, update in silent mode",
                'priority': "required, should be in scope [1..1000]"
            }
        },
        'submit': {
            'description': 'submit a single task job quickly',
            'option': {
                'cluster': """optional, should be a cluster_id, or an auto_cluster string.
                                      default value is an auto_cluster string: img=%s:type=%s.
                                      you can use a exists cluster(type '%s c' for more cluster id),
                                      or use auto cluster, format: img=<imageId>:type=<instanceType>
                                      (instanceType default: %s, type '%s it' for more instanceType). """ % (
                IMG_ID, INS_TYPE, CMD, INS_TYPE, CMD),
                'pack': "optional,pack the files in the program_folder into worker.tar.gz, and upload to oss, if you don't set this option, no pack, no upload",
                'priority': 'optional,int,job priority,default:0\n',
                'timeout': "optional,job would failed if it had expired, default: 172800(2 days)",
                'nodes': "optional,the number of machines you needed to run the program, default: 1",
                'description': 'optional,set job description',
                'force': "optional,job don't fail when instance were failed, default: job fail when even one instance were failed",
                'env': "optional,set environment variables, format: <k>:<v>[,<k2>:<v2>...]",
                'read_mount': """optional,mount a oss path to local file system in read-only mode, kv-pairs, multi-supported,
                                      format: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                      example: oss://bucket/key:/home/admin/ossdir """,
                'write_mount': """optional,mount a oss path to local file system in writable mode
                                      (files in the mounted folder will be upload to oss_path after the task is finished),
                                      kv-pairs, multi-supported, format: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                      example: oss://bucket/key:/home/admin/ossdir """,
                'mount': """optional,mount a oss path to local file system in read/write mode, kv-pairs, multi-supported,
                                      format: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                      example: oss://bucket/key:/home/admin/ossdir """,
                'docker': """optional,optional, use docker, format: <docker_image_name>@<docker_storage_oss_path>,
                                      example: localhost:5000/myubuntu@oss://bucket/dockers/
                                      or for short: myubuntu@oss://bucket/dockers/ """,
                'file': """optional,submit job from a config file, if you give options explicitly, options from this file will be override""",
                'disk': """optional, mount system disk and a data disk(optional), only works with AutoCluster.

        Usage: "--disk system:ephemeral:40,data:cloud:50:/home/disk1".
        Default: system:ephemeral:40, mount 40GB ephemeral disk as system disk.
        System disk config format: system:<cloud|ephemeral>:<40-500>, example: system:cloud:40, mount 40GB ephemeral disk as system disk.
        Data disk config format: data:<cloud|ephemeral>:<5-2000>:<mount-point>, example: data:cloud:5:/home/disk1, mount a 5GB cloud disk as data disk, in windows must mount to driver, such as E driver, like: "data:cloud:5:E". (Attention please: Using ephemeral disk as data disk, the size scope should limit to [5-1024]GB).
        """,
                'show_json': 'optional,just output job.json, don\'t submit a job, default: false'
            }
        },
        'check': {
            'description': "check job status and failed reasons"
        },
        'project': {
            'description': 'project commanders: create, build, submit, etc.',
            'create': {
                'description': 'create a job project',
                'option': {
                    'type': """optional, job project type, default: empty(python), scope: [empty|python|java|shell]""",
                    'job': 'optional, create job project from an exists job_id'
                }
            },
            'build': {
                'description': 'build project, package src/ to worker.tar.gz.'

            },
            'update': {
                'description': 'update job.json',
                'option': {
                    'cluster': """optional, should be a cluster_id, or an auto_cluster string.
                              default value is an auto_cluster string: img=%s:type=%s.
                              you can use a exists cluster(type '%s c' for more cluster id),
                              or use auto cluster, format: img=<imageId>:type=<instanceType>
                              (instanceType default: %s, type '%s it' for more instanceType). """
                    % (IMG_ID, INS_TYPE, CMD, INS_TYPE, CMD),
                    "docker": """optional, use docker image to run, format:<oss_docker_storage_path>:<docker_name>"""
                }
            },
            'submit':{
                'description': 'upload worker.tar.gz and create a job'
            },
            'status': {
                'description': 'show project status.'
            },
            'add_task': {
                'description': 'add a task',
                'detail': "add a task node into job.json, and create a promgram(python) file in src folder.",
                'option': {
                    'cluster': """optional, should be a cluster_id, or an auto_cluster string.
                                 default value is an auto_cluster string: img=%s:type=%s.
                                 you can use a exists cluster(type '%s c' for more cluster id),
                                 or use auto cluster, format: img=<imageId>:type=<instanceType>
                                 (instanceType default: %s, type '%s it' for more instanceType).  """
                    % (IMG_ID, INS_TYPE, CMD, INS_TYPE, CMD),

                    'docker': 'docker image name, must tag with prefix:"localhost:5000/", type "docker images" for more'
                }
            }
        },
        'oss': {
            'description': 'oss commanders: upload, download, ls, etc.',
            'login': {
                'description': 'login OSS',
            },
            'logout': {
                'description': 'logout OSS',
            },
            'pwd': {
                'description': 'show current osspath',
            },
            'ls': {
                'description': 'show folders and files in an osspath',
                'option': {
                    'name': 'search by name',
                    'top': 'length of result-set to show',
                }
            },
            'cat': {
                'description': 'print oss file content',
            },
            'copy': {
                'description': 'copy oss file or folder',
                'detail': 'copy oss file or folder. across region support format: <region>#<osspath>, only if the AK is validated'
            },
            'upload': {
                'description': 'upload file or directory to oss'
            },
            'download': {
                'description': 'download file or directory from oss',
                'option': {
                    'recursion': "download directory and the entire subtree from oss"
                }
            },
            'delete': {
                'description': 'delete file or directory from oos',
                'option': {
                    'yes': 'delete in silent mode'
                 }
            }
        }
    }
