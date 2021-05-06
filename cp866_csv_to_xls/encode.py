import os
import csv
import xlwt

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source\\')
RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'result\\')

files = os.listdir(BASE_DIR)
if not files:
	print(f"{BASE_DIR} is EMPTY")
	return
for filename in files:
	with open(BASE_DIR + filename, 'r', encoding='cp866u') as source:
		content = source.read()
		delimiter = content[0]
		source.seek(0)		
		reader = csv.reader(source, delimiter=delimiter)		
		workbook = xlwt.Workbook()
		sheet = workbook.add_sheet("1")
		for num, line in enumerate(reader):
			for index, col in enumerate(line):
				sheet.write(num, index, col)
		workbook.save(RESULT_DIR + filename + ".xls")
	print(f"File {filename} is converted")
	
