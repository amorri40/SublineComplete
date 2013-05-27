#!/usr/bin/python
# -*- coding: utf-8 -*-
import pkgutil
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

if __name__ == '__main__':
    db = dbSettings.mysql_connect()
    db_cursor = db.cursor()

    syntax_name = "python"
    table_name = syntax_name+"_doc"
    python_modules=list(pkgutil.iter_modules())
    createTable(db_cursor,table_name)

    for loader, module_name, is_pkg in  pkgutil.iter_modules():
        
        try:
            print "\n Module Name:"+module_name
            hash_line = hashlib.md5(str(module_name)).hexdigest()
            mod = loader.find_module(module_name).load_module(module_name)#__import__(module_name)
            doc_string=mod.__doc__
            addToDB(db_cursor,table_name,hash_line, 'module', module_name, doc_string,'')
            #print ("Doc:"+doc_string)
            functions = dir(mod)
            for function in functions:
                attribute = getattr(mod,function)
                func_type = str(type(attribute).__name__)
                doc_string = attribute.__doc__
                hash_line = hashlib.md5(doc_string).digest()
                addToDB(db_cursor,table_name,hash_line, func_type, function, doc_string, module_name)
                #print mod[function].__doc__
            print (functions)
        except:
            continue

