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
file_hashs = []

folders = syntaxSettings.syntax_folders[syntax_name]

def hash_string(_string):
    return hashlib.md5(str(_string)).hexdigest()

def getCount(hash_line):
    global hash_counts
    count = hash_counts.get(hash_line, 0) + 1
    hash_counts[hash_line] = count
    return count

def parse_folders(folder_name):
    for dirname, dirnames, filenames in os.walk(folder_name):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            parse_folder(os.path.join(dirname, subdirname))

        parse_folder(folder_name)

def parse_folder(folder_name):
    global file_hashs
    os.chdir(folder_name)
    for file_name in glob.glob(syntaxSettings.syntax_globs[syntax_name]):
        

        lines = [line.strip() for line in open(file_name)]
        _hash=hash_string(file_name)

        if _hash in file_hashs: continue
        file_hashs.append(hash_string(file_name))
        print 'file:'+file_name
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
    c.execute("""ALTER TABLE """+tableName+""" ADD FULLTEXT(Full_No_Spaces);""")


if __name__ == '__main__':
    createTable(db_cursor,table_name)
    for folder in folders:
        parse_folders(folder)

