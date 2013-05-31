import MySQLdb

from struct import *

from sys import stderr,stdout

class Database():

	def __init__(self,host,user,passwd,db):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.db = db

	def getGroupInfo(self,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		groupId = connection.escape_string(groupId)
		cursor = connection.cursor()

		groupInfo = Struct()
		# determina os participantes e seus respectivos livros
		query = "SELECT title,author,userId FROM participations WHERE groupId='%s'"%(groupId)
		print(query)
		cursor.execute(query)
		rows = cursor.fetchall()
		groupInfo.books = []
		groupInfo.userInfo = []
		groupInfo.numMembers = 0
		for r in rows:
			groupInfo.books.append([r[0],r[1]])
			#informacoes sobre o usuario
			cursor.execute("SELECT positive,negative FROM users WHERE userId=%d"%(r[2]))
			users = cursor.fetchall()
			for user in users:
				groupInfo.userInfo.append([user[0],user[1]])
			groupInfo.numMembers+=1

		cursor.close()
		connection.close()

		return groupInfo

	# retorna uma lista de Struct com os atributos:
	#  id, minUsers, maxUsers, maxTime
	def getGroupList(self):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		cursor.execute("SELECT groupId,minUsers,maxUsers,maxTime FROM groups")
		rows = cursor.fetchall()
		groups = []
		for r in rows:
			g = Struct()
			g.id = r[0]
			g.minUsers = r[1]
			g.maxUsers = r[2]
			g.maxTime = r[3]
			groups.append(g)

		cursor.close()
		connection.close()

		return groups

	def getUsersGroups(self,user):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		cursor.execute("SELECT groupId,title FROM participations WHERE userId=%d"%(user.userId))
		rows = cursor.fetchall()
		groups = []
		for r in rows:
			group = Struct()
			group.id = r[0]
			group.book = r[1]
			groups.append(group)

		cursor.close()
		connection.close()

		return groups






