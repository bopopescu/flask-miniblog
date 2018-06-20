import sys,os
import dictionary_API


def retrieve_words():
	conn = dictionary_API.connect_to_database()
	cursor = conn.cursor()
	result = {}
	i = 0
	retrieve_command = """
	SELECT * FROM word_list
	"""
	cursor.execute(retrieve_command)
	
	row = cursor.fetchone()

	while row is not None:
		result[row[0]] = {
		"word" : row[1]
		}		
		row = cursor.fetchone()
		i += 1
				
	cursor.close()
	conn.close()
	
	return	result
if __name__ == '__main__':
		retrieve_words()
