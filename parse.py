import xml.etree.ElementTree as Xet
import dbf
import sys
import os
from click import echo, style


'''
CREATE TABLE atom_khk_ul_test.dbo.OGRULmini (
	name varchar(1024) NULL,
	rname varchar(1024) NULL,
	inn varchar(20) NULL,
	ogrn varchar(20) NULL,
	category varchar(100) NULL,
	[type] varchar(100) NULL
);
'''

def parse_file(lc_file_name:str, lc_unload_path:str, fileHandler, DatabaseName:str):
	xmlparse = Xet.parse(lc_file_name)
	root = xmlparse.getroot()

	for i in root.findall('Документ'):
		if len(i.findall('ИПВклМСП'))>0:
			lc_category = 'Микро' if i.attrib['КатСубМСП']=='1' else ('Малые' if i.attrib['КатСубМСП']=='2' else ('Средние' if i.attrib['КатСубМСП']=='3' else ''))
			lc_type = 'Организация' if i.attrib['ВидСубМСП']=='1' else ('ИП' if i.attrib['ВидСубМСП']=='2' else '')
			ld_date = i.attrib['ДатаВклМСП']
			i2 = i.findall('ИПВклМСП')[0]
			lc_inn = i2.attrib['ИННФЛ'] if 'ИННФЛ' in i2.attrib else ''
			lc_ogrnip = i2.attrib['ОГРНИП'] if 'ОГРНИП' in i2.attrib else ''
			lc_surname = ''
			lc_name = ''
			lc_patronymic = ''
			if len(i2.findall('ФИОИП'))>0:
				i3 = i2.findall('ФИОИП')[0]
				lc_surname = i3.attrib['Фамилия'] if 'Фамилия' in i3.attrib else ''
				lc_name = i3.attrib['Имя'] if 'Имя' in i3.attrib else ''
				lc_patronymic = i3.attrib['Отчество'] if 'Отчество' in i3.attrib else ''
			recordIP = {'surname':lc_surname, 'name':lc_name, 'patronymic':lc_patronymic, 'inn':lc_inn, 'ogrnip':lc_ogrnip, 'category':lc_category, 'type':lc_type, 'date':ld_date}
			fileHandler.write(f"""insert into {DatabaseName}.OGRULmini (fsurname, fname, fpatronymic, inn, ogrnip, category, kind) values('{lc_surname}', '{lc_name}', '{lc_patronymic}', '{lc_inn}', '{lc_ogrnip}', '{lc_category}', '{lc_type}');\n""")
		for i4 in i.findall('КатСубМСП'):
			print(i.attrib)

	for i in root.findall('Документ'):
		if len(i.findall('ОргВклМСП'))>0:
			lc_category = 'Микро' if i.attrib['КатСубМСП']=='1' else ('Малые' if i.attrib['КатСубМСП']=='2' else ('Средние' if i.attrib['КатСубМСП']=='3' else ''))
			lc_type = 'Организация' if i.attrib['ВидСубМСП']=='1' else ('ИП' if i.attrib['ВидСубМСП']=='2' else '')
			ld_date = i.attrib['ДатаВклМСП']
			i2 = i.findall('ОргВклМСП')[0]
			lc_full_name = i2.attrib['НаимОрг'] if 'НаимОрг' in i2.attrib else ''
			lc_reduce_name = i2.attrib['НаимОргСокр'] if 'НаимОргСокр' in i2.attrib else ''
			lc_inn = i2.attrib['ИННЮЛ'] if 'ИННЮЛ' in i2.attrib else ''
			lc_ogrn = i2.attrib['ОГРН'] if 'ОГРН' in i2.attrib else ''
			recordUL = {'name':lc_full_name[:250], 'rname':lc_reduce_name[:250], 'inn':lc_inn, 'ogrn':lc_ogrn, 'category':lc_category, 'type':lc_type, 'date':ld_date}
			fileHandler.write(f"""insert into {DatabaseName}.OGRULmini (name, rname, inn, ogrn, category, kind)	values('{lc_full_name}', '{lc_reduce_name}', '{lc_inn}', '{lc_ogrn}', '{lc_category}', '{lc_type}');\n""")
	fileHandler.write(f"""GO\n""")
#	os.remove(lc_file_name)

ln_files_count = len(os.listdir(sys.argv[1]))
ln_counter = 0

lc_DatabaseName = sys.argv[3]	#'atom_khk_ul_test.dbo'
TargetFile = open(sys.argv[2],'w', encoding='cp1251', errors='ignore')
TargetFile.write(f"""CREATE TABLE {lc_DatabaseName}.OGRULmini (
	fsurname varchar(1024) COLLATE Cyrillic_General_CI_AS NULL,
	fname varchar(1024) COLLATE Cyrillic_General_CI_AS NULL,
	fpatronymic varchar(1024) COLLATE Cyrillic_General_CI_AS NULL,
	name varchar(1024) COLLATE Cyrillic_General_CI_AS NULL,
	rname varchar(1024) COLLATE Cyrillic_General_CI_AS NULL,
	inn varchar(20) COLLATE Cyrillic_General_CI_AS NULL,
	ogrn varchar(20) COLLATE Cyrillic_General_CI_AS NULL,
	ogrnip varchar(20) COLLATE Cyrillic_General_CI_AS NULL,
	category varchar(100) COLLATE Cyrillic_General_CI_AS NULL,
	kind varchar(100) COLLATE Cyrillic_General_CI_AS NULL
	);\n\nGO\n
""");

for file in os.listdir(sys.argv[1]):
	if file.endswith(".xml"):
		ln_counter=ln_counter+1
		echo(style(text=f"{ln_counter} / {ln_files_count}", bg='blue', fg='bright_yellow') 
	   		+ "    "
	   		+ style(text=os.path.join(sys.argv[1], file), fg='bright_green') + style(text='   ==>  ', fg='cyan') 
			+ style(text=sys.argv[2], fg='bright_blue'))
		print()

		parse_file(os.path.join(sys.argv[1], file), sys.argv[2], TargetFile, lc_DatabaseName)

TargetFile.close()
exit()