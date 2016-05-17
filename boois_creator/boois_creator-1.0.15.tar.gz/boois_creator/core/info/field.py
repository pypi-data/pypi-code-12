# coding=utf-8
import datetime
import json

from utils.cmd_parser import cmd_parser
from utils.str_fmt_helper import camel


class Field(object):

    F_NAME="name"
    F_CMNT="cmnt"
    F_TYPE="type"
    F_LENGTH="length"
    F_DEFAULT="default"
    F_VALIDATOR="validator"
    F_ENUM="enum"
    F_IMG="img"
    F_WIDTH="width"
    F_HEIGHT="height"
    F_EXT="ext"
    F_FILE="file"
    F_INFO="info"
    F_ERR="err"
    F_UNIQUE="unique"
    F_PK="pk"
    WARP_SUB_OBJ_LEFT="{"
    WARP_SUB_OBJ_RIGHT="}"
    WRAP_SUB_OBJ_LIST_LEFT="[{"
    WRAP_SUB_OBJ_LIST_RIGHT="}]"
    WARP_SYS_LEFT="<"
    WARP_SYS_RIGHT=">"

    def __init__(self,parent_obj,stm_str):
        '''
        :param obj_name: 该字段所属于的对象,该对象只包含name和comment时
        :param stm_str:定义该字段的信息,就是json中key值:如 service_list -c 服务 -t [{service}]
        '''
        self._stm_str = stm_str.replace("'", '"')  # category_list -t guid
        self._name, self._arr = cmd_parser(self._stm_str)
        self._parent=parent_obj

        _t = self._arr.get(Field.F_TYPE) or "str"
        _d = self._arr.get(Field.F_DEFAULT)
        _l = self._arr.get(Field.F_LENGTH).split(",") if self._arr.get(Field.F_LENGTH) else None
        _c = self._arr.get(Field.F_CMNT) or self._name
        _v = self._arr.get(Field.F_VALIDATOR) or '-t str'
        _enum=self._arr.get(Field.F_ENUM)
        # _img=self._arr.get(Field.F_IMG)
        _width = self._arr.get(Field.F_WIDTH)
        _height= self._arr.get(Field.F_HEIGHT)
        _ext= self._arr.get(Field.F_EXT)
        _info=self._arr.get(Field.F_INFO) or ""
        _err=self._arr.get(Field.F_ERR) or ""
        # _file = self._arr.get(Field.F_FILE)
        # 处理defalut
        if _d is None:
            if _t in ['str']:
                _d = ""
            elif _t in ['int']:
                _d = 0
            elif _t in ['float','double', 'decimal']:
                _d = 0.0

        if _l is None:
            if _t in ['str']:
                _l = (255,255)
            elif _t in ['int']:
                _l = (11,11)
            elif _t in ['float', 'double', 'decimal']:#TODO decimal这个要额外处理
                _l = (11,11)

        self._type = _t
        self._type_str = ""
        self._type_sub = ""
        self._length = _l
        # 这里要根据type转成相应的值

        if self._type in ['str']:
            self._type_str = "str"
            self._default = self._arr.get(Field.F_DEFAULT) or ""

        elif self._type in ['int']:
            self._type_str = "int"
            self._default = int(_d) if _d else 0

        elif self._type in ['float']:
            self._type_str = "float"
            self._default = float(_d) if _d else 0.0

        elif self._type in ['double']:
            self._type_str = "double"
            self._default = float(_d) if _d else 0.0


        elif self._type in ['decimal']:
            self._type_str = "decimal"
            self._default = float(_d) if _d  else 0.00


        elif self._type.startswith(Field.WRAP_SUB_OBJ_LIST_LEFT) and self._type.endswith(Field.WRAP_SUB_OBJ_LIST_RIGHT):
            self._type_str = "list"
            self._type_sub = self._type.replace(Field.WRAP_SUB_OBJ_LIST_LEFT, "").replace(Field.WRAP_SUB_OBJ_LIST_RIGHT, "")
            self._default = []


        elif self._type.startswith(Field.WARP_SUB_OBJ_LEFT) and self._type.endswith(Field.WARP_SUB_OBJ_RIGHT):
            self._type_str = "obj"
            self._type_sub = self._type.replace(Field.WARP_SUB_OBJ_LEFT, "").replace(Field.WARP_SUB_OBJ_RIGHT, "")

            self._default = None


        elif self._type.startswith(Field.WARP_SYS_LEFT) and self._type.endswith(Field.WARP_SYS_RIGHT):
            self._type_str = "sys"
            self._type_sub = self._type.replace(Field.WARP_SYS_LEFT, "").replace(Field.WARP_SYS_RIGHT, "")

            if self._type_sub == "datetime.datetime":
                self._default = datetime.datetime.strptime(_d or '1970-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
            else:
                raise ValueError("非法type:%s," % self._type)
        else:
            raise ValueError("非法type:%s" % self._type)


        self._comment = _c
        self._validator = _v

        self._enum= _enum
        self._img= Field.F_IMG in self._arr #有声明-img 就说明是图片链接
        self._width= int(_width) if _width else 0
        self._height= int(_height) if _height else 0
        self._ext= _ext
        self._file= Field.F_FILE in self._arr #有声明 -file就说明是文件的链接
        self._unique=Field.F_UNIQUE in self._arr # 有声明-unique就说明是唯一值
        self._pk=Field.F_PK in self._arr #有声明-pk就是主键
        self._info=_info
        self._err=_err
        self._enum_data=None
    def _get_is_sub_obj_list(self):
        return self._type_str=="list"

    def _get_is_sub_obj(self):
        return self._type_str == "obj"

    def _get_is_sys(self):
        return self._type_str == "sys"
    def _get_is_base(self):
        return self._type in ["int","str","float","double","decimal"]
    def _get_is_mix(self):
        return not self._get_is_base()
    def _get_is_unique(self):
        return self._unique

    def _get_is_pk(self):
        return self._pk

    def _get_name(self):
        return self._name

    def _get_type(self):
        return self._type
    def _get_type_sub(self):
        return self._type_sub

    def _get_length(self):
        return self._length
    def _get_validator(self):
        return self._validator
    def _get_comment(self):
        return self._comment
    def _get_default(self):
        return self._default

    def _get_enum(self):
        return self._enum
    def _get_img(self):
        return self._enum
    def _get_width(self):
        return self._width
    def _get_height(self):
        return self._height
    def _get_ext(self):
        return self._ext
    def _get_file(self):
        return self._file

    def _get_info(self):
        return self._info

    def _get_err(self):
        return self._err

    def _get_enum_data(self):
        if self._enum_data is None:
            from utils import enum_parser
            self._enum_data=enum_parser.EnumParser.parse(self._enum)
        return self._enum_data
    # def _get_info_field_name(self):
    #     return "%s_list" % self.name if self.is_sub_obj_list else self.name
    name=property(fget=_get_name) #json的key值,如name,category_list,注意json的key什么样,该值就什么样,要拼接出对象的名称请使用type_sub
    type=property(fget=_get_type) #json中定义的类型,就是-type后面的值
    type_sub=property(fget=_get_type_sub) #复合类型的对象的名称,仅字段类型为复合对象时才有值,如goods,cover_img,category,datetime.datetime
    length=property(fget=_get_length) #11,11 12
    default=property(fget=_get_default) #默认值
    validator=property(fget=_get_validator) #检查器
    comment=property(fget=_get_comment) #注释
    enum = property(_get_enum) #json中枚举的声明
    enum_data = property(_get_enum_data) #json中枚举的声明,使用enum_parser解析之后的值
    img = property(_get_img) #返回True表示该字段是图片链接
    width = property(_get_width)#返回int 图片宽度
    height = property(_get_height)#返回int  图片高度
    ext = property(_get_ext) #图片或文件的后缀名
    file = property(_get_file) #返回True表示该字段是文件链接
    info = property(fget=_get_info)  # 前端在输入该字段值的提示信息,如请输入中文,长度1~4个字符
    err = property(fget=_get_err)  # 前端在输入该字段发生错误时的提示提示信息,如格式错误,请输入中文,长度1~4个字符

    is_sub_obj_list=property(fget=_get_is_sub_obj_list) #是否为多个子对象
    is_sub_obj=property(fget=_get_is_sub_obj) #是否为单个子对象
    is_sys=property(fget=_get_is_sys) #是否为系统类型
    is_base=property(fget=_get_is_base) #是否为基本类型
    is_mix=property(fget=_get_is_mix) #是否为复合类型
    is_unique=property(fget=_get_is_unique) #是否具有唯一性
    is_pk=property(fget=_get_is_pk) #是否是主键


