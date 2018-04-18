import sqlite3
from datetime import date, datetime
import os


class Database:
    def __init__(self, dfile='local.db'):
        self._db_folder = 'db'
        self.path = './'+self._db_folder+'/'+dfile
        if not os.path.exists(self._db_folder):
            os.makedirs(self._db_folder)
        self.conn = None
        self.c = None
        self._tableName = 'stocks'  # TODO: Change table Name

    def setName(self, name):
        self._tableName = "{}".format(name)

    def connect(self):
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()

    def save(self):
        self.conn.commit()

    def BuildETable(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS {0}
            (date text, data text, id real)'''.format(self._tableName))

    def BuildTable(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS {0}
            (date text, trans text, symbol text, qty real, price real)'''.format(self._tableName))

    def request(self, requestData):
        return self.c.execute(requestData)

    def insert(self, values):
        self.c.execute("INSERT INTO {0} VALUES {1}".format(self._tableName, values))

    def count(self):
        return self.c.execute("SELECT count(1) from {0}".format(self._tableName)).fetchall()[0]

    def getAll(self):
        for row in self.c.execute('SELECT * FROM {0}'.format(self._tableName)):
            print row   # TODO : Compatible Print 2 / 3

    def getJson(self):
        t = []
        for row in self.c.execute('SELECT * FROM {0}'.format(self._tableName)):
            edate = row[0].encode('ascii', 'ignore')
            text = row[1].encode('ascii', 'ignore')
            eid = row[2]
            line = {'date': edate, 'text': text, 'id': eid}
            t.append(line)
            # print row    TODO : Compatible Print 2 / 3
        return t

    def close(self):
        self.conn.close()


event = Database('events.db')


def addEvent(text):
    event.connect()
    event.setName('event')
    event.BuildETable()
    today = date.today()
    event.insert("('{0}','{1}',{2})".format(today, "{0}".format(text), 1))
    print event.getJson()
    print event.count()
    event.save()
    event.close()

# conn = sqlite3.connect('./db/local.db')
# c = conn.cursor()

# c.execute('''CREATE TABLE stocks
#              (date text, trans text, symbol text, qty real, price real)''')

# c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")





# event = Database('events.db')
# event.connect()
# event.setName('event')
# event.BuildETable()
# today = date.today()
# event.insert("('{0}','{1}',{2})".format(today, "Im an important message", 1))
# event.insert("('{0}','{1}',{2})".format(today, "Im a message too", 2))
# event.insert("('{0}','{1}',{2})".format(today, "Im another message", 3))
# print event.getJson()
# print event.count()
# event.save()
# event.close()
#
# db1 = Database('mydb1.db')
# db1.connect()
# db1.BuildTable()
# today = date.today()
# db1.request("INSERT INTO stocks VALUES ('{0}','BUY','RHAT',100,35.14)".format(today))
# db1.insert("('{0}','{1}','{2}',{3},{4})".format(today, "user", "name", 1, 2))
# db1.request("INSERT INTO stocks VALUES ('{0}','BUYS','RHATS',100,35.4)".format(today))
# db1.getAll()
# print db1.count()
# db1.save()
# db1.close()
