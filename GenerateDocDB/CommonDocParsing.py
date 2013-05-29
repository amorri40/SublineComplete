import sys
sys.path.append("..") #import python modules in parent directory
import pymysql
import dbSettings
import hashlib

import urllib2
from BeautifulSoup import BeautifulSoup, SoupStrainer

table_name=""

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

def setupMysql(syntax_name):
    global table_name
    db = dbSettings.mysql_connect()
    db_cursor = db.cursor()

    table_name = syntax_name+"_doc"
    createTable(db_cursor,table_name)
    return db_cursor

def hash_string(_string):
    return hashlib.md5(_string.encode('utf-8')).hexdigest()

#
# converts a html_tag into a string, adding spaces between elements
#
def parse_tag_to_string(html_tag):
    if not html_tag: return ""
    children = list(html_tag.childGenerator())
    output_string=""
    for child in children:
        if 'childGenerator' in dir(child) and len(list(child.childGenerator())) > 1:
            output_string += parse_tag_to_string(child)
        elif 'getText' in dir(child):
            output_string += ' '+(child.getText().encode('utf-8'))
        else:
            output_string += (str(child))#(dir(child))
    return output_string.lstrip()

def parseChildren(html_tag, parse_child):
    children = list(html_tag.childGenerator())
    output_string=""
    for child in children:
        parse_child(child)

def findTagsWithId(soup, tag_name, id_name):
    return soup.findAll(tag_name, {'id' : id_name})

def findTagsWithClass(soup, tag_name, class_name):
    return soup.findAll(tag_name, {'class' : class_name})

def findtagsWithName(soup,tag_name):
    return soup.findAll(tag_name)

def isTagName(tag,name):
    if 'name' in dir(tag):
        if tag.name == name:
            return True
    return False

def tagHasId(tag,_id):
    try:
        if tag['id'] == _id:
            return True
    except: pass
    return False

def parseDLTags(tag, parse_dt, parse_dd):
    #now get all functions/variables
    #tags = soup.findAll('dl')
    
    return_list = []
      
    
    dt_tags = tag.findChildren('dt')
    dd_tags = tag.findChildren('dd')
    for i in range(len(dt_tags)):
        try:
            doc_name = parse_dt(dt_tags[i])
            doc_string = parse_dd(dd_tags[i])
            #print "name:"+doc_name+" string:"+doc_string
            return_list.append((doc_name,doc_string))
        except IndexError: pass
    
    return return_list

def isList(_var):
    return (type(_var).__name__) == 'list'

def getSoupFromUrl(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    return soup