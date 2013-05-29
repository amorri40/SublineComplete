import json
import CommonDocParsing
from CommonDocParsing import *

global_module_name=""
#global_current_function=""
global_section=""
global_current_type=""
global_current = {'function':'', 'exception':[], 'parameter':[] }

def parseDT(tag):
	return CommonDocParsing.parse_tag_to_string(tag)

def parseDD(tag):
	return CommonDocParsing.parse_tag_to_string(tag)

def isList(_var):
	return (type(_var).__name__) == 'list'

def writeFunctionToDB():
	global global_current
	if global_section != "Methods": return
	if global_current['function'] != '':
		full_name = global_module_name+'.'+global_current['function']
		print 'write '+ full_name + ' to DB'
		doc_string=""
		for prop in global_current:
			if isList(global_current[prop]):
				doc_string += '\n '+prop+'s:\n'
				for item in global_current[prop]:
					doc_string += " "+ item[0][0] + ": "+item[0][1] + "\n"
		print doc_string
		hash_line = hash_string(full_name)
		addToDB(db_cursor,CommonDocParsing.table_name,hash_line, 'function', str(full_name), str(doc_string), str(global_module_name))
	#now reset global_current
	global_current = {'function':'', 'exception':[], 'parameter':[] }

def parseMainTags(tag):
	global global_current_function, global_current_parameters, global_current_type, global_section
	if tagHasId(tag,'Methods'):
		global_section='Methods'
	elif isTagName(tag, 'h3'):
		if tagHasId(tag,'Read') or tagHasId(tag,'Write'):
			return
		writeFunctionToDB()
		global_current['function']=tag.contents[0]
		print global_current['function']
	elif isTagName(tag, 'dl'):
		dl_list = CommonDocParsing.parseDLTags(tag, parseDT, parseDD)
		if global_current_type == '':
			print "Warning global_current_type was ''"
		else:
			global_current[global_current_type].append(dl_list)
		
	elif isTagName(tag, 'h6'):
		if tagHasId(tag,'Parameters'):
			global_current_type="parameter"
			
		elif tagHasId(tag,'Exceptions_thrown'):
			global_current_type="exception"
			
		else:
			global_current_type=tag['id']

	elif isTagName(tag,'div'):
		CommonDocParsing.parseChildren(tag, parseMainTags)



if __name__ == '__main__':

	json_files = []

	db_cursor = CommonDocParsing.setupMysql('javascript')

	data = json.load(open('./JSON/js-mdn.json'))
	data_string = json.dumps(data)


	for element in data:
		url = element['url']
		print url
		#sections = element['sectionNames']
		#for section in sections:
		#	print section
		
		soup = CommonDocParsing.getSoupFromUrl(url)

		global_module_name = CommonDocParsing.findTagsWithClass(soup, 'h1', 'page-title')[0].contents[0].encode('utf-8')
		print "\n == "+global_module_name

		dl_tags = findtagsWithName(soup,'dl')
		for dl_tag in dl_tags:
			dl_tag_data = CommonDocParsing.parseDLTags(dl_tag, parseDT, parseDD)
			for data in dl_tag_data:
				full_name =  global_module_name.encode('utf-8') + '.' 
				full_name += data[0].encode('utf-8')
				doc_string = data[1] + '\nMore Info:'+url.encode('utf-8')
				hash_line = hash_string(full_name)
				addToDB(db_cursor,CommonDocParsing.table_name,hash_line, 'function', str(full_name), str(doc_string), str(global_module_name))

		
		
		#main_article = CommonDocParsing.findTagsWithId(soup, 'div', 'wikiArticle')[0]
		
		#CommonDocParsing.parseChildren(main_article, parseMainTags)
		#writeFunctionToDB() #write the last function
	
