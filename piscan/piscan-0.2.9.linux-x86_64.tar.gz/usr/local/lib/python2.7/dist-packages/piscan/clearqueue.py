import pika
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_delete(queue='LameQ')
channel.close()
connection.close()
