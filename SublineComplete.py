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
from SublineComplete import syntaxSettings
from time import time

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
output_area="window" #window or console
output_layout="column" #row or column

time_of_last_completion=time()
previous_completion=""
   
class printtooutputwindowCommand(sublime_plugin.TextCommand):
    current_location=0
    output_text=""

    def run(self,edit):
        return run(self,edit,"","")

    def run(self, edit,print_string,ending,flush=False):
        if len(print_string)>1:
            self.output_text+=print_string+ending
            #print (print_string,end=ending)
        if flush: 
            self.view.set_read_only(False) 
            
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            self.view.sel().clear()
            
            self.view.insert(edit, 0, self.output_text)
            #self.view.show(sublime.Region(self.view.size()-2,self.view.size())) #scroll to the bottom
            self.view.set_read_only(True)   
            self.output_text=""   
                                    
class sublinecompleteCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        def popup_callback(index):

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
        DBLineComplete.createWindow(self.view)

        syntax_name = DBLineComplete.getSyntaxName(self.view)
        if DBLineComplete.isSyntaxSupported(syntax_name) == False: return

        #first get the line from the editor
        region = sublime.Region(0, self.view.size())
        lines = self.view.lines(region)
        target = DBLineComplete.get_target(self.view).strip()

        matches=DBLineComplete.text_python_line_database(target,syntax_name,limit=100)
        
        if len(matches)>0:
            sublime.active_window().active_view().show_popup_menu(matches,popup_callback)
        




class DBDocumentation():
    doc_view=0

    def createDocWindow(self,view):
        if self.doc_view: return
        window = view.window()
        wannabes = filter(lambda v: v.name() == ("SublineDoc Output"), window.views())
        window_list=list(wannabes)
        self.doc_view = window_list[0] if len(window_list) else window.new_file()
        self.doc_view.set_name("SublineDoc Output")
        self.doc_view.set_syntax_file(view.settings().get('syntax'))
        self.doc_view.set_scratch(True)

    def writeDocumentation(self,view, target, syntax_name):
        num_of_doc_results = self.get_doc_from_database(target, syntax_name,addWildcardToStart=False)
        if num_of_doc_results < 1:
            self.get_doc_from_database(target, syntax_name,addWildcardToStart=True)
        self.printToDocWindow("",end="",flush=True)

    def printToDocWindow(self,print_string,end="\n",flush=False):
        ending=end
        if output_layout == "column": ending = "\n"
        if output_area == "window":
            self.doc_view.run_command("printtooutputwindow",{'print_string':print_string, 'ending':ending, 'flush':flush})
        else:
            print (print_string,end=ending) 

    def isSyntaxSupported(self, syntax_name):
        isSupported = syntax_name in syntaxSettings.syntax_docs
        return isSupported 

    def get_doc_from_database(self, target,syntax_name,limit=30,asTuples=False,addWildcardToStart=False):
            if self.isSyntaxSupported(syntax_name) == False: return
            target=escape_characters(target)
            if addWildcardToStart: target='%'+target
             
            matches=[]
            
            if target == '':
                limit = 30

            syntax_name+='_doc'
            
            query="SELECT type, name, doc_string FROM "+syntax_name+" "
            query+="WHERE name Like '"+target+"%'"
            query+=" LIMIT 5"
            
            result=db_cursor.execute(query)

            for row in db_cursor.fetchall():
                _type = row[0]
                _name = row[1]
                doc_string = row[2]
                doc_string = "\n === "+_name+" === \n"+doc_string+"\n"
                self.printToDocWindow(doc_string)
                if asTuples:
                    matches.append((doc_string,))
                else:
                    matches.append(doc_string)
                           
            return len(matches)

class DBLineComplete(): 
    output_view=0; #output view for line completions

    def text_python_line_database(target,syntax_name,limit=30,asTuples=False,addWildcardToStart=False):
                
                target=escape_characters(target)
                if addWildcardToStart: target='%'+target
                 
                matches=[]
                
                if target == '':
                    limit = 30

                syntax_name+='_line'
                
                query="SELECT Full_No_Spaces,Full_spaces, count FROM "+syntax_name+" "
                query+="WHERE Full_No_Spaces Like '"+target+"%'"
                query+="ORDER BY count DESC LIMIT "+str(limit)
                print
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

    def getSyntaxName(view):
        syntax_name = (view.settings().get('syntax')).replace('.tmLanguage','').lower()
        syntax_name = os.path.basename(syntax_name)
        return syntax_name

    def isSyntaxSupported(syntax_name):
        isSupported = syntax_name in syntaxSettings.syntax_folders
        return isSupported  

    def createWindow(self,view):
        if self.output_view: return
        window = view.window()
        wannabes = filter(lambda v: v.name() == ("SublineComplete Output"), window.views())
        window_list=list(wannabes)
        self.output_view = window_list[0] if len(window_list) else window.new_file()
        self.output_view.set_name("SublineComplete Output")
        self.output_view.set_syntax_file(view.settings().get('syntax'))
        self.output_view.set_scratch(True)

    def getCurrentSymbol(view):
        selection_list = view.sel()
        selection = selection_list[0]
        return (view.substr(view.word(selection)))
    
    def getPreviousSymbol(view):
        currentWord=DBLineComplete.getCurrentSymbol(view)
        selection_list = view.sel()
        selection = sublime.Region(selection_list[0].a-len(currentWord)-1,selection_list[0].b-len(currentWord)-1)
        previous_word = view.substr(view.word(selection))
        return (previous_word)

    def getPreviousAndCurrentSymbol(view):
        current_word = DBLineComplete.getCurrentSymbol(view)
        previous_word = DBLineComplete.getPreviousSymbol(view)
        query = previous_word + "%%%" + current_word
        #print ("both:"+query)
        return (query)

    def printToOutput(self,print_string,end="\n",flush=False):
        ending=end
        if output_layout == "column": ending = "\n"
        if output_area == "window":
            self.output_view.run_command("printtooutputwindow",{'print_string':print_string, 'ending':ending, 'flush':flush})
        else:
            print (print_string,end=ending) 
            
def escape_characters(string):
            line = ''.join(string.split())
            line = line.replace('"','\\"').replace("'","\\'") .replace("%","\\%").replace("\\%\\%\\%","%").replace("_","\\_")
            return line

class sublineCompleteEvent(sublime_plugin.EventListener):
    dbline = DBLineComplete()
    dbdoc = DBDocumentation()
    
    def on_query_completions(self, view, prefix, locations):
        
        #matches=DBLineComplete.text_python_line_database('%'+prefix,limit=5,asTuples=False)
        #if len(matches)<1: 
        #    return None
        
        #return (matches, sublime.INHIBIT_WORD_COMPLETIONS)
        return None

    def on_selection_modified_async(self,view):
        #print("selection modified")
        if (len(view.sel())<1): return
        target = view.substr(view.sel()[0])
        if len(target) < 3: return
        #print (target)
        self.create_output_windows(view)
        syntax_name = DBLineComplete.getSyntaxName(view)
        self.dbdoc.writeDocumentation(view, target, syntax_name) 
        return

    def create_output_windows(self, view):
        self.dbline.createWindow(view)
        self.dbdoc.createDocWindow(view)

    def on_modified_async(self, view):
        global time_of_last_completion,previous_completion
        #if ((time()-time_of_last_completion)<0.2): return
        #time_of_last_completion=time()

        self.create_output_windows(view)
        
        syntax_name = DBLineComplete.getSyntaxName(view)
        if DBLineComplete.isSyntaxSupported(syntax_name) == False: return
        if (len(view.sel())<1): return
                      
        path = view.file_name()
        region = sublime.Region(0, view.size())
        lines = view.lines(region)
        target = view.line(view.sel()[0].begin())
        target = view.substr(target)
        target = target.strip() 
        
        if previous_completion == target: return #no point in displaying the same completion
        previous_completion = target

        
        
        matches=DBLineComplete.text_python_line_database(target,syntax_name)
        #self.dbdoc.writeDocumentation(view, target, syntax_name) 
        if len(matches)<5: 
            
            matches.extend(DBLineComplete.text_python_line_database(target,syntax_name,addWildcardToStart=True))
        if len(matches)<7:
            target=DBLineComplete.getPreviousAndCurrentSymbol(view)
            matches.extend(DBLineComplete.text_python_line_database(target,syntax_name,addWildcardToStart=True))
        if len(matches)<10:
            target=DBLineComplete.getCurrentSymbol(view)
            
            matches.extend(DBLineComplete.text_python_line_database(target,syntax_name,addWildcardToStart=True))
        if len(matches)>0:
            self.dbline.printToOutput (" -- Matches for: "+target+"--")   
            
            i = 1
            for match in matches:
                
                length = len(match)
                if length >49:
                    match = match[0:50]
                    length = 50
                
                if (i % 3) == 0:
                    self.dbline.printToOutput (str(i)+": " + match)
                else:
                    self.dbline.printToOutput (str(i)+": " + match + (" "*(55-length)), end= "")
                i = i + 1
        self.dbline.printToOutput("",end="",flush=True)