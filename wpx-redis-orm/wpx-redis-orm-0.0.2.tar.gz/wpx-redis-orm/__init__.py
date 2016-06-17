# encoding=utf-8
from redisOrm import CharField, IntField, RedisModel
from manager import REDIS_CONNECT_SET


class TestModel(RedisModel):
    name = CharField(name="aaa", max_length=100)
    age = IntField(default=12)

class Blog(RedisModel):
    title = CharField(max_length=110, default="tittle_default")
    auther = CharField()
    click = IntField()

    class Meta:
        app_name = "wupeaking2"

def main(*args, **kwargs):
    try:
        ret = Blog.objects.get(auther="刘东方")
    except Blog.DoesNotExits:
        print "不存在"

if __name__ == "__main__":
    import uuid
    import random
    REDIS_CONNECT_SET.update(dict(db=4))
    # for i in xrange(10):
    #     blog = Blog.objects.create(title=str(uuid.uuid1()), auther="mew man%s"%i, click=10)
    # authers = ["liu dehua", "maliya", "小泽", "花木", "曾工", "kitty", "刘东方"]
    # for i in xrange(1000):
    #     blog = Blog.objects.create(title=str(uuid.uuid1()), auther=authers[random.randrange(0, len(authers))],
    #                                click=1000*random.random())
    # ret = Blog.objects.filter(auther="小泽")
    try:
        ret = Blog.objects.get(auther="刘东方")
    except Blog.DoesNotExits:
        print "不存在"

    print ret.title
    print ret.id
    # for i in ret:
    #     print i.title
    #     print i.auther
    #     print i.click
    #     print i.id
    import threading, time
    for i in xrange(10):
        time.sleep(5)
        th = threading.Thread(group=None, target=main, name=None, args=(), kwargs={})
        th.setDaemon(True)
        th.start()



    time.sleep(100)
