###################################################################################
# Copyright (c) 2012, Alasdair Morrison - www.alasdairmorrison.com
# All rights reserved.
# 
# BSD License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###################################################################################

import sublime, sublime_plugin, re, sys, os, pprint

try:
    import pymysql
except Exception:
    print (sys.path)
    sys.path.extend(['', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/site-packages/distribute-0.6.28-py3.2.egg', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/site-packages/PyMySQL3-0.5-py3.2.egg', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python32.zip', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/plat-darwin', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/lib-dynload', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/site-packages', '/usr/local/Cellar/python3/3.2.3/Frameworks/Python.framework/Versions/3.2/lib/python3.2/site-packages/setuptools-0.6c11-py3.2.egg-info'])
    import pymysql
sys.path.append(os.path.dirname(__file__))
import dbSettings
db = dbSettings.mysql_connect()
db_cursor=db.cursor()

class sublinecompleteCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        def popup_callback(index):
            #sublime.message_dialog('popup_callback called!')
            if(index > -1):
                for i in range(len(self.view.sel())):
                    line = self.view.line(self.view.sel()[i].begin())
                    src = self.view.substr(line)
                    match = re.search(r"$", src)
                    if(match):
                        end = match.end()
                        match = re.search(r"\S", src)
                        if(match):
                            start = match.start()
                        else:
                            start = self.view.sel()[i].begin()
                            end = line.end()
                        length = end - start
                        begin = self.view.sel()[i].begin()-length
                        self.view.replace(edit, sublime.Region(begin, self.view.sel()[i].end()), matches[index])
      
        #first get the line from the editor
        region = sublime.Region(0, self.view.size())
        lines = self.view.lines(region)
        target = DBLineComplete.get_target(self.view).strip()

        matches=DBLineComplete.text_python_line_database(target,limit=100)
        
        if len(matches)>0:
            sublime.active_window().active_view().show_popup_menu(matches,popup_callback)


class sublineCompleteEvent(sublime_plugin.EventListener):
    
    def on_query_completions(self, view, prefix, locations):
        
        #matches=DBLineComplete.text_python_line_database('%'+prefix,limit=5,asTuples=False)
        #if len(matches)<1: 
        #    return None
        
        #return (matches, sublime.INHIBIT_WORD_COMPLETIONS)
        return None

    def on_modified_async(self, view):
        path = view.file_name()
        region = sublime.Region(0, view.size())
        lines = view.lines(region)
        target = view.line(view.sel()[0].begin())
        target = view.substr(target)
        target = target.strip() 
        matches=DBLineComplete.text_python_line_database(target)
        if len(matches)<1: 
            matches=DBLineComplete.text_python_line_database(target,addWildcardToStart=True)
        if len(matches)>0:
            print ("\n\n -- Matches for: "+target+"--")   
            #DBLineComplete.pp.pprint(matches)
            i = 1
            for match in matches:
                
                length = len(match)
                if length >49:
                    match = match[0:50]
                    length = 50
                
                if (i % 3) == 0:
                    print (str(i)+": " + match)
                else:
                    print (str(i)+": " + match + (" "*(55-length)), end= "")
                    #print ("\t\t", end="")
                i = i + 1



class DBLineComplete(): 

    def text_python_line_database(target,limit=30,asTuples=False,addWildcardToStart=False):
                
                target=escape_characters(target)
                if addWildcardToStart: target='%'+target
                 
                matches=[]
                
                if target == '':
                    limit = 30
                
                query="SELECT Full_No_Spaces,Full_spaces, count FROM pythonline "
                query+="WHERE Full_No_Spaces Like '"+target+"%'"
                query+="ORDER BY count DESC LIMIT "+str(limit)
                result=db_cursor.execute(query)

                for row in db_cursor.fetchall():
                    Full_No_Spaces = row[0]
                    Full_spaces = row[1]
                    count = row[2]
                    if asTuples:
                        matches.append((Full_spaces,))
                    else:
                        matches.append(Full_spaces)
                               
                return matches

    def get_target(view):
        line = view.line(view.sel()[0].begin())
        return view.substr(line)

def escape_characters(string):
            line = ''.join(string.split())
            return line.replace('"','\\"').replace("'","\\'") .replace("%","\\%").replace("_","\\_")

