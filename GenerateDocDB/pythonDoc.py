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

# parse_html_to_desc converts a html_tag into a string, adding spaces between elements
def parse_html_to_desc(html_tag):
    #print (dir(html_tag))
    children = list(html_tag.childGenerator())
    output_string=""
    for child in children:
        if 'childGenerator' in dir(child) and len(list(child.childGenerator())) > 1:
            output_string += parse_html_to_desc(child)
        elif 'getText' in dir(child):
            output_string += ' '+(child.getText().encode('utf-8'))
        else:
            output_string += (str(child))#(dir(child))
    return output_string.lstrip()

def hash_string(_string):
    return hashlib.md5(str(_string)).hexdigest()

def parse_sphinx(url):
    #loop over pages
    page = urllib2.urlopen(url)
    print (url)
    soup = BeautifulSoup(page)

    #first get the main docstring of the module
    section = soup.findAll(attrs={"class" : "section"})
    doc_name = section[0]['id'].replace('module-','')
    
    module_text=""
    for tag in section[0]:
        if 'name' in dir(tag) and tag.name == 'p': #all the p tags are part of the module description
         module_text += ' '+parse_html_to_desc(tag)
    
    #now write this module to the database
    addToDB(db_cursor,table_name, hash_string(module_text), 'module', doc_name, module_text, '')
    

    #now get all functions/variables
    tags = soup.findAll('dl')
    try:
        #print (dir(tags[0]))
        for tag in tags:
            try:
                
                doc_name = (tag.findChild('dt')['id'])
                doc_type = (tag['class'])
                #print ((tags[0]).fetchText())
                contents = (tag).renderContents()
                doc_string = contents
                doc_string = parse_html_to_desc(tag)
                #print (doc_string)
                hash_line = hashlib.md5(str(doc_name)).hexdigest()
                addToDB(db_cursor,table_name,hash_line, doc_type, doc_name, doc_string, '')
            except KeyError: pass
    except IndexError: pass

def parse_folder(folder_name):
    os.chdir(folder_name)
    folder_name = 'file://'+folder_name
    for file_name in glob.glob('*.html'):
        url=os.path.join(folder_name, file_name)
        parse_sphinx(url)

python_doc_folders = ['http://omz-software.com/pythonista/docs/ios/beautifulsoup_ref.html', '/Volumes/Macintosh HD/Users/alasdairmorrison/Downloads/python-2.7.5-docs-html/library/']

if __name__ == '__main__':
    db = dbSettings.mysql_connect()
    db_cursor = db.cursor()

    syntax_name = "python"
    table_name = syntax_name+"_doc"
    createTable(db_cursor,table_name)

    for folder in python_doc_folders:
        if folder.startswith('http:/'):
            parse_sphinx(folder)
        else:
            parse_folder(folder)