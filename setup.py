#!/usr/bin/env python
# -*- coding: utf8 -*-
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
try:
	cursor.execute("DROP TABLE invitations")
except:
	pass

cursor.execute("CREATE TABLE groups (owner int, groupId int, name varchar(128), maxUsers int, maxTime int,private int, PRIMARY KEY (groupId))")
cursor.execute("CREATE TABLE users (userId int,login varchar(128),password varchar(32),email varchar(256), cpf varchar(11), home text, phone varchar(20) ,positive int, negative int, PRIMARY KEY (userId))")
cursor.execute("CREATE TABLE participations (userId int, groupId int, author varchar(100), title varchar(200), extraInfo text, PRIMARY KEY (userId,groupId))")
cursor.execute("CREATE TABLE invitations (userId int, groupId int, PRIMARY KEY (userId,groupId))")

cursor.execute("INSERT INTO groups (owner,groupId,name,maxUsers,maxTime,private) VALUES \
(0,0,'Clube do Bolinha',5,10,0), \
(0,1,'Os Batutinhas',8,20,0), \
(1,2,'Meu Grupo',4,15,0), \
(2,3,'Private I',8,20,1), \
(2,4,'S3cr3t0',10,16,1) \
;")
cursor.execute("INSERT INTO users (userId,login,password,email,cpf,home,phone,positive,negative) VALUES \
(0,'ana','asd','ana@banana.invalid','01234567890','rua dos bobos, numero 0', '88996767', 0,0), \
(1,'beatriz','qwe','bea@home.invalid','18302582120','avenida qualquer, numero 100, apartamento 101', '90807060', 2,6), \
(2,'carlos','ijk','carlos@hell.gov','65839295782','bairro patopolis, numero 666', '91238145', 10,2), \
(3,'denis','lmnw','denis@nowhere.invalid','47729617482','rua 24 de outubro, numero 999', '83938242', 5,5)")
cursor.execute("INSERT INTO participations (userId,groupId,title,author) VALUES \
(0,0,'O Tempo e o Vento','Érico Veríssimo'), \
(0,1,'Memorias Póstumas de Brás Cubas','Machado de Assis'), \
(0,2,'O Conde de Monte Cristo Vol. I','Alexandre Dumas'), \
(1,2,'Concerto Campestre','Luiz Antonio de Assis Brasil'), \
(2,3,'A Moreninha','Joaquim Manuel de Macedo'), \
(3,4,'Neuromancer','William Gibson') \
")
cursor.execute("INSERT INTO invitations (userId,groupId) VALUES \
(0,3) \
")

db.commit()
cursor.close()
db.close()