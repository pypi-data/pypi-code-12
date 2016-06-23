__all__ = ['ack']

def ack(channel,method):
    def f(_):
        try:
            assert _
        except AssertionError:
            channel.basic_nack(method.delivery_tag)
        except:
            raise
        else:
            channel.basic_ack(method.delivery_tag)
        return True
    return f
