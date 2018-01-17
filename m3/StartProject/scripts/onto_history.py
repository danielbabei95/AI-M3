import sqlite3
import os
import time
import datetime
import jsondiff
import json
import sys

from calendar import timegm

DB_FILE = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources"),
                       "history.db")


class DB(object):
    def __init__(self, db_path=DB_FILE):
        self.connection = None
        self.cursors = None
        if db_path is not None:
            self.connect(db_path)

    def connect(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursors = self.connection.cursor()

    def execute(self, cmd, values=''):
        self.cursors.execute(cmd, values)
        self.commit()

    def commit(self):
        self.connection.commit()

    def exit(self, commmit=False):
        if commmit is not False:
            self.commit()
        self.connection.close()

    def insert_into_table(self, ontology):
        self.cursors.execute("select ontology from version order by date_added desc limit 1")
        last_version = self.cursors.fetchone()[0]
        last_version = json.loads(last_version)
        difference = jsondiff.diff(last_version, ontology)
        self.cursors.execute("insert into version(ontology, date_added, differences) values(?, ?, ?)",
                             (str(json.dumps(ontology)), datetime.datetime.now(), str(difference)))
        self.commit()

    def remove(self, date):
        # if isinstance(date, str):
        #     date = datetime.date.fromtimestamp(timegm(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f').timetuple()))
        print(date)
        self.cursors.execute("delete from version where date_added=?", (date,))
        self.commit()

    def get_by_date(self, date):
        return self.cursors.execute("select ontology from version where date_added=?", (date,)).fetchall()[0]


def create_table(conn):
    conn.execute('''create table version (ontology text, date_added date, differences text)''')
    d = dict()
    conn.execute("insert into version(ontology, date_added, differences) values(?, ?, ?)",
                 (json.dumps(d), datetime.datetime.now(), ''))


def addDataToJson():
    dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
    dbObj = DB(os.path.join(dir_path, "history.db"))
    dbObj.execute('select * from version')
    json_data = dict()
    for i in dbObj.cursors.fetchall():
        json_data[i[1]] = i[2]
    return json_data


if __name__ == '__main__':
    dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
    # dbObj = DB(os.path.join(dir_path, "history.db"))
    # dbObj.execute("drop table version")
    # create_table(dbObj)
    # j1 = json.load(open(os.path.join(os.path.dirname(DB_FILE), "input.json")))
    # dbObj.execute('insert into version(ontology, date_added, differences) values(?, ?, ?)', (json.dumps(j1), datetime.datetime.now(), ""))
    # j2 = json.load(open(os.path.join(os.path.dirname(DB_FILE), "input2.json")))
    # dbObj.execute('select * from version')
    # for i in dbObj.cursors.fetchall():
    #     print(i)
    #     print(i[2])
    # dbObj.insert_into_table(j2)
