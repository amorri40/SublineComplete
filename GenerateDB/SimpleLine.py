#simple line reading into a mysql database
import sys
sys.path.append("..") #import python modules in parent directory

import pymysql
import dbSettings
import syntaxSettings
import glob
import os
import hashlib
import ast

db = dbSettings.mysql_connect()
db_cursor = db.cursor()
syntax_name = "python"
table_name = syntax_name+"_line"
hash_counts = dict()

folders = syntaxSettings.syntax_folders[syntax_name+'_folders']


def getCount(hash_line):
    global hash_counts
    count = hash_counts.get(hash_line, 0) + 1
    hash_counts[hash_line] = count
    return count

def parse_folder(folder_name):
    os.chdir(folder_name)
    for file_name in glob.glob("*.py"):
        print 'file:'+file_name

        lines = [line.strip() for line in open(file_name)]
        for line in lines:
            if line == '':
                continue

            full_spaces = line
            full_no_spaces = ''.join(line.split())
            hash_line = hashlib.md5(full_no_spaces).hexdigest()
            count = getCount(hash_line)
            db_cursor.executemany(
                  """REPLACE INTO """+table_name+"""
                  VALUES (%s, %s, %s, %s)""",

              [(hash_line, full_no_spaces, full_spaces, count)]
              )

def createTable(c,tableName):
    print "createtable:"+tableName
    c.execute("""CREATE TABLE IF NOT EXISTS `"""+tableName+"""` (
      `hash_line` varchar(32) NOT NULL,
      `Full_No_Spaces` text NOT NULL,
      `Full_spaces` text NOT NULL,
      `count` int NOT NULL,
      UNIQUE KEY `hash_line` (`hash_line`)
    ) ENGINE=MyISAM DEFAULT CHARSET=latin1;""");


if __name__ == '__main__':
    createTable(db_cursor,table_name)
    for folder in folders:
        parse_folder(folder)

