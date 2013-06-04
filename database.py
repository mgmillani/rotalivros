import MySQLdb

from struct import *
from user import *

class Database():

	def __init__(self,host,user,passwd,db):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.db = db

	def getGroupInfo(self,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()

		groupInfo = Struct()
		# determina os participantes e seus respectivos livros
		query = "SELECT title,author,userId FROM participations WHERE groupId=%d"%(groupId)
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
	#  id, name,numMembers, maxUsers, maxTime, private
	def getGroupList(self,user = User()):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		#lista os grupos publicos
		cursor.execute("SELECT groupId,name,maxUsers,maxTime,private FROM groups WHERE private=0 and not EXISTS \
		(SELECT groupId FROM participations WHERE participations.groupId=groups.groupId and participations.userId=%d)"%(user.userId))
		rows = cursor.fetchall()
		#lista os grupos privados aos quais o usuario foi convidado
		cursor.execute("SELECT groupId FROM invitations WHERE userId=%d"%(user.userId))
		private = cursor.fetchall()

		#adiciona esses grupos a lista de grupos disponiveis
		for p in private:
			cursor.execute("SELECT groupId,name,maxUsers,maxTime,private FROM groups WHERE groupId=%d"%(p[0]))
			rows += cursor.fetchall()

		groups = []
		for r in rows:
			g = Struct()
			g.id = r[0]
			g.name = r[1]
			g.maxUsers = r[2]
			g.maxTime = r[3]
			g.private = r[4]==1

			#determina o numero de membros
			cursor.execute("SELECT COUNT(*) FROM participations WHERE groupId=%d"%(g.id))
			total = cursor.fetchall()
			g.numMembers = total[0][0]

			groups.append(g)

		cursor.close()
		connection.close()

		return groups

	def getUsersGroups(self,user):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		cursor.execute("SELECT groupId,title FROM participations WHERE userId=%s"%(user.userId))
		rows = cursor.fetchall()
		groups = []
		for r in rows:
			group = Struct()
			group.id = r[0]
			#determina o nome do grupo
			cursor.execute("SELECT name FROM groups WHERE groupId=%d"%(group.id))
			name = cursor.fetchall()
			group.name = name[0][0]
			group.book = r[1]
			groups.append(group)

		cursor.close()
		connection.close()

		return groups

	#determina se um usuario eh moderador de um grupo
	def isModeratorOf(self,userId,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		#lista os grupos publicos
		cursor.execute("SELECT groupId FROM groups WHERE owner=%d and groupId=%d"%(userId,groupId))
		rows = cursor.fetchall()
		result = False
		if(len(rows)!=0):
			result = True

		cursor.close()
		connection.close()
		return result

	def isMemberOf(self,userId,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		#lista os grupos publicos
		cursor.execute("SELECT groupId FROM participations WHERE userId=%d and groupId=%d"%(userId,groupId))
		rows = cursor.fetchall()
		result = False
		if(len(rows)!=0):
			result = True

		cursor.close()
		connection.close()
		return result

	def removeUserFromGroup(self,userId,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		cursor.execute("DELETE FROM participations WHERE groupId=%d and userId=%d"%(groupId,userId))

		connection.commit()
		cursor.close()
		connection.close()

	# adiciona um usuario em um grupos
	# book eh uma Struct com os seguintes campos:
	# title,author,extra
	def addUserToGroup(self,userId,groupId,book = Struct()):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()

		book.title = connection.escape_string(book.title)
		book.author= connection.escape_string(book.author)
		book.extra = connection.escape_string(book.extra)
		try:
			cursor.execute("INSERT INTO participations (userId,groupId,title,author,extraInfo) VALUES (%d,%d,'%s','%s','%s')"%(userId,groupId,book.title,book.author,book.extra))
		except:
			pass
		connection.commit()

		cursor.close()
		connection.close()





