# -*- coding: utf-8 -*-
import sys
import urllib2
import os
import glob
print (sys.path)
sys.path.extend(['', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/site-packages/distribute-0.6.28-py3.2.egg', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/site-packages/PyMySQL3-0.5-py3.2.egg', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python32.zip', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/plat-darwin', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/lib-dynload', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/site-packages', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/site-packages/setuptools-0.6c11-py3.2.egg-info'])

from BeautifulSoup import BeautifulSoup, SoupStrainer


import sys
sys.path.append("..") #import python modules in parent directory
import pymysql
import dbSettings
import hashlib

def createTable(c,tableName):
    print "createtable:"+tableName
    c.execute("""CREATE TABLE IF NOT EXISTS `"""+tableName+"""` (
      `hash_line` varchar(32) NOT NULL,
      `type` text NOT NULL,
      `name` text NOT NULL,
      `doc_string` text,
      `parent` text,
      UNIQUE KEY `hash_line` (`hash_line`)
    ) ENGINE=MyISAM DEFAULT CHARSET=latin1;""");

def addToDB(db_cursor,table_name,hash_line, doc_type, doc_name, doc_string, parent):
    db_cursor.executemany(
                  """REPLACE INTO """+table_name+"""
                  VALUES (%s, %s, %s, %s, %s)""",

              [(hash_line, doc_type, doc_name, doc_string, parent)]
              )

def parse_folder(folder_name):
    os.chdir(folder_name)
    for file_name in glob.glob('*.html'):
        url=os.path.join('file://'+folder_name, file_name)
        #loop over pages
        page = urllib2.urlopen(url)
        print (url)
        soup = BeautifulSoup(page)

        tags = soup.findAll('dl')
        try:
            print (dir(tags[0]))
            for tag in tags:
                try:
                    
                    doc_name = (tag.findChild('dt')['id'])
                    doc_type = (tag['class'])
                    #print ((tags[0]).fetchText())
                    contents = (tag).renderContents()
                    doc_string = contents
                    hash_line = hashlib.md5(str(doc_name)).hexdigest()
                    addToDB(db_cursor,table_name,hash_line, doc_type, doc_name, doc_string, '')
                except KeyError: pass
        except IndexError: pass

if __name__ == '__main__':
    db = dbSettings.mysql_connect()
    db_cursor = db.cursor()

    syntax_name = "python"
    table_name = syntax_name+"_doc"
    createTable(db_cursor,table_name)

    parse_folder('/Volumes/Macintosh HD/Users/alasdairmorrison/Downloads/python-2.7.5-docs-html/library/')