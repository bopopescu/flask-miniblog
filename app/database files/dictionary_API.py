from python_mysql_dbconfig import read_db_config
import sys
sys.path.append("C:\\Python27")
from mysql.connector import MySQLConnection, Error
import json
import requests

def main() :
	search_term = raw_input("Enter a word: ")
	json_result = Call_API(search_term)
	add_word_to_wordlist(json_result)
	add_sentences(search_term)

def add_word_to_wordlist(json):
	conn = connect_to_database()
	cursor = conn.cursor()

	try:
		word = json['results'][0]['word']
		insert_command = "INSERT INTO `word_list`(`word`) VALUES (\"%s\")" %word

		try:
			cursor.execute(insert_command)
			conn.commit()
			word_id_number = find_row_number(cursor,word)
			cursor.close()
			conn.close()
			add_definitions(word_id_number, json)
		except Error as e:
			print(e)
			cursor.close()
			conn.close()
		
		
		
		
		
		
		

	except Error as e:
		print(e)
		print("Could not add word")
		cursor.close()
		conn.close()
		return

def add_definitions(id_number, json):
	conn = connect_to_database()
	cursor = conn.cursor()
		
	def insert_to_db(id,lexical_entry_index,definition,domain,register, cursor, conn):
		insert_command = """
		INSERT INTO definitions (`word_id`, `definition_number`, `definition`, `domains`, `register`)
		VALUES(%i,%i,\"%s\",\"%s\",\"%s\")
		""" %(id,lexical_entry_index,definition,domain,register)
		
		print(insert_command)
		
		cursor.execute(insert_command)
		conn.commit()	
		definition,domain,register = clear_variables(definition,domain,register)
		
	
	lexical_entries = json['results'][0]['lexicalEntries'][0]['entries']
	lexical_entry_index = 0
	
	for index, entry in enumerate(lexical_entries):
		lexical_entry_index = 0
		definitions = entry['senses']
		definition = ""
		domain = ""
		register = ""
		for sense in definitions:
			try:
				for subsense in sense['subsenses'][0]:
					definition = str(subsense['definitions'][0])
					try: 
						domain = str(subsense['domains'][0])
					except:
						pass
					try:
						register = str(subsense['registers'][0])
					except:
						pass
					insert_to_db(id_number, lexical_entry_index,definition,domain,register, cursor, conn)
					
			except:
				definition = str(sense['definitions'][0])
			
			try:
				domain = str(sense['domains'][0])
			except:
				pass
			try: 
				register = str(sense['register'][0])
			except:
				pass
			insert_to_db(id_number, lexical_entry_index,definition,domain,register, cursor, conn)
	
	cursor.close()
	conn.close()
	
		
def add_sentences(word):
	print("Beginning add_sentences")
	conn = connect_to_database()
	cursor = conn.cursor()
	
	row_number = find_row_number(cursor,word)
	print(row_number)
	
	json_result = Call_API(word, extra_parameter = "sentences")
	
	lexical_entries = json_result['results'][0]['lexicalEntries'][0]['sentences']
	for sentence_index, lexical_entry in enumerate(lexical_entries):
		sentence = lexical_entry['text']
		region = lexical_entry['regions'][0]
		insert_command = """
		INSERT INTO sentences (`id`, `sentence`, `region`, `sentence_index`)
		VALUES(%i,\"%s\",\"%s\",\"%i\")
		""" %(row_number,sentence,region,sentence_index)
		print(insert_command)
		
		sentence,region,sentence_index = clear_variables(sentence,region,sentence_index)
		
		try :
			cursor.execute(insert_command)
			conn.commit()
		except Error as e:
			print(e)
	cursor.close()
	conn.close()

def find_row_number(cursor, word):
	get_id_command = "select `id` from `word_list` where `word` = \"%s\"" %word
	try:
		cursor.execute(get_id_command)
	except Error as e:
		print(e)

	print(get_id_command)
	row = cursor.fetchone()
	return row[0]


def connect_to_database():
	try:
		dbconfig = read_db_config()
		return MySQLConnection(**dbconfig)
	except Error as e:
		print(e)


def Call_API(search_term, **kwargs):
	extra_parameter = kwargs.get("extra_parameter", "")
	if extra_parameter != "":
		extra_parameter = "/" + extra_parameter
	baseURL = "https://od-api.oxforddictionaries.com/api/v1/entries/en/%s%s" % (search_term,extra_parameter)
	try:
		auth = {"app_id": "15c382c3","app_key": "2f9b49469c209430a038ae9239d19c6d"}
		r = requests.get(baseURL, headers=auth)
	except:
		print("An error ocurred")
	finally:
		print("Finished")
	return r.json()

def clear_variables(*args):
	empty_list = []
	for arg in args:
		if isinstance(arg,str):
			empty_list.append("")
		else:
			empty_list.append(0)
		
	return empty_list


if __name__ == '__main__':
	main()
