from flask import Flask, redirect, url_for, request, render_template, Markup
import time, sys, subprocess, pika, os, subprocess
from sh import tail

app = Flask(__name__)

@app.route("/")
def hello():
    htmlcode = ''
    connection = pika.BlockingConnection()
    channel = connection.channel()
    q = channel.queue_declare(queue='LameQ',passive=True,exclusive=False)
    q_len = q.method.message_count

    p = subprocess.Popen(["service", "pirec", "status"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    p = subprocess.Popen(["service", "piqueue", "status"], stdout=subprocess.PIPE)
    out2, err = p.communicate()
    out = "<h2>Pirec Service:</h2><br>" + out + "<br><br><h2>Piqueue Service:</h2><br>" + out2

    htmlcode = htmlcode + out + "<br><br>"
    htmlcode = htmlcode + "There are " + str(q_len) + " messages in the local queue"
    htmlcode = htmlcode.decode('utf-8')
    return render_template('index.html', item=Markup(htmlcode))

@app.route("/logs/piqueue")
def piqueuelogs():
    #return render_template('index.html', item='Here!')
    logfile = r"/var/log/piqueue.log"
    logs = ""
    file = open(logfile, 'rU')
    logs = file.read()
    logs = logs[-4000:]
    logs = logs.replace('\n', '<br>')
    logs = logs.decode('utf-8')
    return render_template('index.html', item=Markup(logs))

@app.route("/logs/pirec")
def pireclogs():
    #return render_template('index.html', item='Here!')
    logfile = r"/var/log/pirec.log"
    logs = ""
    file = open(logfile, 'rU')
    logs = file.read()
    logs = logs[-4000:]
    logs = logs.replace('\n', '<br>')
    logs = logs.decode('utf-8')
    return render_template('index.html', item=Markup(logs))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True) 
