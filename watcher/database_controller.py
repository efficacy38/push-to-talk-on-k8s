#!/bin/python3
import pymysql

class Controller:
    def __init__(self, host='localhost', user='root', password='', database='kamailio'):
        self.db = pymysql.connect(host=host,
                                  user=user,
                                  password=password,
                                  database=database)

    def __del__(self):
        self.db.close()

    def add_new_rtpengine(self, url):

        sql = """
        INSERT INTO rtpengine (url)
        SELECT '{url}'
        WHERE NOT EXISTS ( SELECT url FROM rtpengine WHERE url = '{url}' );
        """.format(url="udp:{}:2223".format(url))
        cursor = self.db.cursor()

        try:
            # execute sql instruction
            cursor.execute(sql)
            # send to mysql to execute
            self.db.commit()
        except:
            # if encounter error, then rollback
            self.db.rollback()

    def delete_old_rtpengine(self, url):
        sql = """
        DELETE FROM rtpengine
        WHERE url='{url}';
        """.format(url="udp:{}:2223".format(url))
        cursor = self.db.cursor()

        try:
            # execute sql instruction
            cursor.execute(sql)
            # send to mysql to execute
            self.db.commit()
        except:
            # if encounter error, then rollback
            self.db.rollback()
