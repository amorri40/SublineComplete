import json
import CommonDocParsing
from CommonDocParsing import *

global_module_name=""
global_section=""
global_current_type=""
global_current = {'function':'', 'exception':[], 'parameter':[] }

def parseDT(tag):
	return CommonDocParsing.parse_tag_to_string(tag)

def parseDD(tag):
	return CommonDocParsing.parse_tag_to_string(tag)

if __name__ == '__main__':

	json_files = ['./JSON/html-mdn.json','./JSON/js-mdn.json']

	db_cursor = CommonDocParsing.setupMysql('javascript')
	for json_file in json_files:
		data = json.load(open(json_file))
		data_string = json.dumps(data)


		for element in data:
			url = element['url']

			try:
				soup = CommonDocParsing.getSoupFromUrl(url)

				global_module_name = CommonDocParsing.findTagsWithClass(soup, 'h1', 'page-title')[0].contents[0].encode('utf-8')
				print " == "+global_module_name+": "+url+" ==\n" #show progress

				dl_tags = findtagsWithName(soup,'dl')
				for dl_tag in dl_tags:
					dl_tag_data = CommonDocParsing.parseDLTags(dl_tag, parseDT, parseDD)
					for data in dl_tag_data:
						try:
							full_name =  global_module_name.decode('utf-8').replace('&lt;','<').replace('&gt;','>') + '.' 
							full_name += data[0].decode('utf-8')
							doc_string = data[1].decode('utf-8') + '\nMore Info: '+url.encode('utf-8')
							hash_line = hash_string(full_name)
							addToDB(db_cursor,CommonDocParsing.table_name,
								hash_line, 
								'function', 
								full_name, 
								doc_string.encode('utf-8'), 
								global_module_name.decode('utf-8'))
						except UnicodeEncodeError: print ('unicode encode error')
			except: pass
		
