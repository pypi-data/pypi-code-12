# -*- coding: utf-8 -*-
# boois flask 框架,作者:周骁鸣 boois@qq.com
"""mysql_db_helper用来访问mysql"""
import MySQLdb as db

class DbHelper(object):
    """mysql数据访问类"""

    def __init__(self):
        pass

    # 不返回记录  public void execute_non_query(sql字符串)
    @staticmethod
    def execute_non_query(cmdtxt, mapping=None, db_info={}):
        """执行一段sql命令,不返回数据，用于update、insert等"""
        if cmdtxt == "":
            return True
        if mapping is None:
            mapping = ()
        cmdtxt = cmdtxt.replace("?", "%s")
        try:
            conn = db.Connection(**db_info)
            with conn as cursor:
                cursor.execute(cmdtxt, mapping)
                cursor.close()
                return True
        except Exception, ex:
            if vars().has_key('conn'):
                conn.close()
            raise ex

    @staticmethod
    def execute_non_query_bat(cmdtxt, mapping_arr, db_info={}):
        """批量执行条件"""
        if cmdtxt == "":
            return True
        cmdtxt = cmdtxt.replace("?", "%s")
        try:
            conn = db.Connection(**db_info)
            with conn as cursor:
                cursor.executemany(cmdtxt, mapping_arr)
                cursor.close()
                conn.commit()
                return True
        except Exception, ex:
            if vars().has_key('conn'):
                conn.close()
            raise ex

    @staticmethod
    def execute_scalar(cmdtxt, mapping=None, db_info={}):
        """执行一条sql语句,并返回第一条记录"""
        if cmdtxt == "":
            return None
        if mapping is None:
            mapping = ()
        cmdtxt = cmdtxt.replace("?", "%s")
        try:
            conn = db.Connection(**db_info)
            if cmdtxt.lower().find("limit") == -1:
                cmdtxt = cmdtxt.rstrip(";") + " LIMIT 1 OFFSET 0"
            with conn as cursor:
                cursor.execute(cmdtxt, mapping)
                for _ in range(cursor.rowcount):
                    return cursor.fetchone()
                cursor.close()
            return None
        except Exception, ex:
            if vars().has_key('conn'):
                conn.close()
            raise ex

    # 遍历方法
    @staticmethod
    def each(cmdtxt, mapping=None, each_fn=None, db_info={}):
        """使用sql语句获取一组数据结果并用fn(data)来轮询它"""
        if cmdtxt == "":
            return None
        if mapping is None:
            mapping = ()
        cmdtxt = cmdtxt.replace("?", "%s")
        try:
            conn = db.Connection(**db_info)
            result_list = []
            with conn as cursor:
                cursor.execute(cmdtxt, mapping)
                setnum = 0
                while True:
                    for _ in range(cursor.rowcount):
                        result = cursor.fetchone()
                        result['__setnum'] = str(setnum)  # 给返回的记录中添加结果集set的索引
                        result_list.append(result)
                        if each_fn != None:
                            each_fn(result)
                    if not cursor.nextset():
                        break
                    setnum += 1
                cursor.close()
            return result_list
        except Exception, ex:
            if vars().has_key('conn'):
                conn.close()
            raise ex

    @staticmethod
    def paging(tab_name="", fields="*", where_str="", mapping=(), sort_str="", page_size=10, current_page=1,
               each_fn=None, counter=True, db_info={}):
        # pylint: disable=too-many-arguments,too-many-locals
        """遍历方法 public int:总记录数 each(表名,字段名,搜索条件,排序条件,每页数量,第几页,委托方法fn(行对象))"""
        where_str = where_str.replace("?", "%s")
        # try:
        rscount = 0
        conn = db.Connection(**db_info)
        with conn as cursor:
            if current_page < 1:
                current_page = 1
            if counter:
                comtxttmp = "select count(*) as __rscount from {tab_name} {where_str}\
                              {sort_str};select {fields} from {tab_name}  {where_str} {sort_str} \
                              limit {page_size} offset {page}"
            else:
                comtxttmp = "select {fields} from {tab_name}  {where_str} {sort_str} \
                                limit {page_size} offset {page}"

            cmdtxt = comtxttmp.format(
                tab_name=tab_name,
                where_str=(where_str if where_str == "" else " where " + where_str),
                sort_str=(sort_str if sort_str == "" else " order by " + sort_str),
                fields=fields,
                page_size=page_size,
                page=str((current_page - 1) * page_size)
            )
            cursor.execute(cmdtxt, mapping + mapping if counter and mapping else mapping)
            setnum = 0
            while True:
                if each_fn is not None:
                    for _ in range(cursor.rowcount):
                        result = cursor.fetchone()
                        if result.has_key("__rscount"):
                            rscount = int(result["__rscount"])
                            continue
                        result['__setnum'] = str(setnum)  # 给返回的记录中添加结果集set的索引
                        each_fn(result)
                if not cursor.nextset():
                    break
                setnum += 1
            cursor.close()
        return rscount
        # except Exception, ex:
        #     if vars().has_key('conn'):
        #         conn.close()
        #     raise ex
