#!/usr/bin/env python
import MySQLdb

db = MySQLdb.connect(host="localhost",user="engsoft",passwd="wingedlizards",db="rotalivros")
cursor = db.cursor()

try:
	cursor.execute("DROP TABLE groups")
except:
	pass
try:
	cursor.execute("DROP TABLE users")
except:
	pass
try:
	cursor.execute("DROP TABLE participations")
except:
	pass

cursor.execute("CREATE TABLE groups (owner int, groupId int, minUsers int, maxUsers int, maxTime int)")
cursor.execute("CREATE TABLE users (userId int,login varchar(128),password varchar(32),email varchar(256), cpf varchar(11), home text, phone varchar(20) ,positive int, negative int)")
cursor.execute("CREATE TABLE participations (userId int, groupId int, author text, title text)")

cursor.execute("INSERT INTO groups (owner,groupId,minUsers,maxUsers,maxTime) VALUES (0,0,3,5,10),(0,1,5,8,20),(1,2,3,4,15),(2,3,5,8,20);")
cursor.execute("INSERT INTO groups VALUES (4,4,4,5,45);")
cursor.execute("INSERT INTO users (userId,login,password,email,cpf,home,phone,positive,negative) VALUES \
(0,'ana','asd','ana@banana.invalid','01234567890','rua dos bobos, numero 0', '88996767', 0,0), \
(1,'beatriz','qwe','bea@home.invalid','18302582120','avenida qualquer, numero 100, apartamento 101', '90807060', 2,6), \
(2,'carlos','ijk','carlos@hell.gov','65839295782','bairro patopolis, numero 666', '91238145', 10,2), \
(3,'denis','lmnw','denis@nowhere.invalid','47729617482','rua 24 de outubro, numero 999', '83938242', 5,5)")
cursor.execute("INSERT INTO participations (userId,groupId,author,title) VALUES \
(0,0,'O Tempo e o Vento','Erico Verissimo'), \
(0,1,'Memorias Postumas de Bras Cubas','Machado de Assis'), \
(1,2,'Concerto Campestre','?'), \
(2,3,'A Moreninha','?'), \
(4,4,'Neuromancer','William Gibson') \
")


db.commit()
cursor.close()
db.close()