#simple line reading into a mysql database
import MySQLdb
import dbSettings
import glob
import os
import hashlib
import ast

db = dbSettings.mysql_connect()
db_cursor = db.cursor()
table_name = "pythonline"
hash_counts = dict()

folders = ["/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/"]


#use the first 3 letters as a guide
num_of_letters = 3


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
            #try:
            #    tree = ast.parse(line)
#
#            except Exception:
#                continue

            full_spaces = line
            full_no_spaces = ''.join(line.split())
            hash_line = hashlib.md5(full_no_spaces).hexdigest()
            count = getCount(hash_line)
            db_cursor.executemany(
                  """REPLACE INTO """+table_name+"""
                  VALUES (%s, %s, %s, %s)""",

              [(hash_line, full_no_spaces, full_spaces, count)]
              )


if __name__ == '__main__':
    for folder in folders:
        parse_folder(folder)