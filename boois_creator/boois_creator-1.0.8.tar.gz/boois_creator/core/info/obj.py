# coding=utf-8
from utils.table_struc_creator import factory
from utils.table_struc_creator.table import table


class Obj(object):
    def __init__(self,name,comment,fields=None):
        '''

        :param name:
        :param comment:
        :param fields: 当该obj被他的包含的field引用时,该属性就是None
        '''
        self._name=name
        self._comment=comment
        self._fields=fields
        self._fnames=None
        self._unique_fields=None
        self._unique_fnames=None
        self._pk_fields=None

    def _get_name(self):
        return self._name

    def _get_comment(self):
        return self._comment
    def _get_fields(self):
        if not self._fields:
            self._fields=[]
        return self._fields

    def _get_fnames(self):
        if self._fnames is None:
            self._fnames=[x.name for x in self.fields]
        return self._fnames

    def _set_fields(self,v):
        self._fields=v
    def _get_mysql_field_length(self,length_tuple,default_val):
        # ?,11
        if length_tuple[1] is not None:
            return max(length_tuple[1],default_val)
        # None:None
        if length_tuple[0] is None:
            return default_val
        # 11,None
        else:
            return max(length_tuple[0],default_val)
    def _get_unique_fields(self):
        if self._unique_fields is None:
            self._unique_fields=[x for x in self.fields if x.is_unique]
        return self._unique_fields

    def _get_pk_fields(self):
        if self._pk_fields is None:
            self._pk_fields = [x for x in self.fields if x.is_pk]
        return self._pk_fields

    def _get_unique_fnames(self):
        if self._unique_fnames is None:
            self._unique_fnames = [x.name for x in self.unique_fields]
        return self._unique_fnames
    def _get_pk_fnames(self):
        if self._pk_fnames is None:
            self._pk_fnames = [x.name for x in self.pk_fields]
        return self._pk_fnames
    def _get_table_sql(self):
        fields = []
        # f_names=[]
        for f in self._fields:
            # if f.name == '%s_id' % self.name:
            #     one = factory.guid(name=f.name)
            if f.type in ['int']:
                one = factory.int(name=f.name,length=self._get_mysql_field_length(f.length,11))
            elif f.type in ['float']:
                one=factory.float(name=f.name,length="%s,2" % self._get_mysql_field_length(f.length,11))
            elif f.type in ['decimal']:
                one = factory.decimal(name=f.name,length="%s,2" % self._get_mysql_field_length(f.length,11))
            elif f.type in ['<datetime.datetime>']:
                one = factory.datetime(f.name)
            elif f.type in ['str']:
                if f.length[1] and f.length[1]<1024:
                    one = factory.varchar(name=f.name,length=self._get_mysql_field_length(f.length,11))
                else: #None 0 >=1024
                    one = factory.text(name=f.name)
            elif f.type:
                one = factory.text(f.name)
            # f_names.append(f.name)
            one.comment = f.comment or f.name
            fields.append(one)
        # t=table(self.name,"id",fields)
        t = table(name=self.name, pk="id", fields=fields, comment=self.comment)
        return t.to_txt(False)


    name=property(fget=_get_name)
    comment=property(fget=_get_comment)
    fields=property(fget=_get_fields,fset=_set_fields)
    unique_fields=property(fget=_get_unique_fields) #具有唯一值的field实体组成的list
    pk_fields=property(fget=_get_pk_fields) #主键的field实体组成的list
    fnames=property(fget=_get_fnames)#所有fields中的name组成的集合
    unique_fnames=property(fget=_get_unique_fnames) #具有唯一值的field的名称组成的list
    pk_fnames=property(fget=_get_pk_fnames) #具有主键名称组成的list
    table_sql=property(fget=_get_table_sql)
if __name__ == '__main__':
    from field import Field
    import pprint
    parent_obj=Obj(name="goods",comment="货品")
    o=Obj(name="goods",comment="货品",fields=[
        Field(parent_obj=parent_obj,stm_str="name -c 货品名称 -t str"),
        Field(parent_obj=parent_obj,stm_str="category_list -c 分类 -t [{category}]"),
    ])
    print o.name
    for f in  o.fields:
        print f.name,f.type,f.type_sub,f.default