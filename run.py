import psutil
import socket
import sys
from datetime import date, datetime

from flask import Flask, render_template, jsonify, request
if sys.version_info[0] > 3:
    from .db import Database
else:
    import db
    Database = db.Database

app = Flask(__name__)
# app.debug = True # Uncomment to debug

event = Database('events.db')


@app.route('/')
def home():
    db.addEvent("Login to Web interface from {0}".format("127.0.0.1"))
    return render_template('index.html', data='LolEmpty')


@app.route('/events')
def parse():
    event.connect()
    event.setName('event')
    r = event.getJson()
    event.close()
    return jsonify(r)

@app.route('/stats')
def stats():
    # cpu disk ram procc users ++
    cpu = str(psutil.cpu_percent())

    mem = str(psutil.virtual_memory().percent)

    dis = str(psutil.disk_usage(psutil.disk_partitions()[0].mountpoint).percent)

    memory = psutil.virtual_memory()
    mavbl = round(memory.available/1024.0/1024.0, 1)
    mttl = round(memory.total/1024.0/1024.0, 1)

    disk = psutil.disk_usage('/')
    davbl = round(disk.free/1024.0/1024.0/1024.0, 1)
    dttl = round(disk.total/1024.0/1024.0/1024.0, 1)

    users = [i.name for i in psutil.users()]

    procc = len(psutil.pids())

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        LIP = s.getsockname()[0]
    except:
        LIP = '127.0.0.1'
    finally:
        s.close()


    rep = {'cpu': cpu, 'mem': mem, 'dis': dis, 'ip': LIP, 'memory_available': mavbl, 'disk_available': davbl, 'users': users, 'procc': procc}
    return jsonify(rep)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
