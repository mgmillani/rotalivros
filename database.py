import MySQLdb

from struct import *
from user import *
from random import Random

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

	# determina os grupos disponiveis ao usuario
	# retorna uma lista de Struct com os atributos:
	#  id, name,numMembers, maxUsers, maxTime, private
	def getGroupList(self,userId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		#lista os grupos publicos
		cursor.execute("SELECT groupId,name,maxUsers,maxTime,private FROM groups WHERE private=0 and not EXISTS \
		(SELECT groupId FROM participations WHERE participations.groupId=groups.groupId and participations.userId=%d)"%(userId))
		rows = cursor.fetchall()
		#lista os grupos privados aos quais o usuario foi convidado
		cursor.execute("SELECT groupId FROM invitations WHERE userId=%d"%(userId))
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

	# lista todos os grupos dos quais o usuario eh membro
	def getUsersGroups(self,userId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		cursor.execute("SELECT groupId,title FROM participations WHERE userId=%s"%(userId))
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

	# retorna uma Struct com os atributos
	# address, date
	def getDestinationInfo(self,userId,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		# determina para qual usuario deve-se mandar o livro
		cursor.execute("SELECT userId FROM exchanges WHERE fromUser=%s and groupId=%d"%(userId,groupId))
		rows = cursor.fetchall()
		toUser = rows[0][0]

		cursor.execute("SELECT address FROM users WHERE userId=%d"%(toUser))
		result = Struct()
		result.address = cursor.fetchall()[0][0]
		cursor.execute("SELECT beginDate FROM cicles WHERE groupId=%d"%(groupId))
		result.date = cursor.fetchall()[0][0]

		cursor.close()
		connection.close()
	
		return result

		

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

	def isFull(self,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		#conta o numero de usuarios no grupo
		cursor.execute("SELECT count(*) FROM participations WHERE groupId=%d"%(groupId))
		members = cursor.fetchall()[0][0]
		#determina a capacidade do grupo
		cursor.execute("SELECT maxUsers	FROM groups WHERE groupId=%d"%(groupId))
		if members == cursor.fetchall()[0][0]:
			return True
		else:
			return False

	def userHasConfirmed(self,userId,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		#conta o numero de usuarios no grupo
		cursor.execute("SELECT count(*) FROM participations WHERE groupId=%d and userId=%d and confirmed=1"%(groupId,userId))
		if cursor.fetchall()[0][0] == 0:
			return False
		else:
			return True

	def groupCicleHasStarted(self,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		#conta o numero de usuarios que confirmaram a participacao
		cursor.execute("SELECT count(*) FROM participations WHERE groupId=%d and confirmed=1"%(groupId))
		numConfirmed = cursor.fetchall()[0][0]
		#determina o numero necessario de usuarios
		cursor.execute("SELECT maxUsers FROM groups WHERE groupId=%d"%(groupId))
		maxUsers = cursor.fetchall()[0][0]

		if maxUsers == numConfirmed:
			return True
		else:
			return False

	def removeUserFromGroup(self,userId,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		cursor.execute("DELETE FROM participations WHERE groupId=%d and userId=%d"%(groupId,userId))

		connection.commit()
		cursor.close()
		connection.close()

	# adiciona um usuario em um grupos
	# book eh uma Struct com os seguintes campos:
	# title,author,year,publisher,edition,isbn,language
	def addUserToGroup(self,userId,groupId,book = Struct()):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()

		book.title = connection.escape_string(book.title)
		book.author= connection.escape_string(book.author)
		book.year = connection.escape_string(book.year)
		book.publisher = connection.escape_string(book.publisher)
		book.edition = connection.escape_string(book.edition)
		book.isbn = connection.escape_string(book.isbn)
		book.language = connection.escape_string(book.language)

		try:
			cursor.execute("INSERT INTO participations\
			(userId,groupId,title,author,year,publisher,edition,isbn,language) VALUES\
			(%d,    %d,     '%s',  '%s', '%s',  '%s',    '%s',   '%s','%s')"%(userId, groupId, book.title, book.author, book.year, book.publisher, book.edition, book.isbn, book.language))
			connection.commit()
		except MySQLdb.Error, e:
			print("Erro no banco de dados: %s"%e)

		cursor.close()
		connection.close()

	def confirmUserParticipation(self,userId,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()

		try:
			query = "UPDATE participations SET confirmed=1 WHERE groupId=%d and userId=%d"%(groupId,userId)
			cursor.execute(query)
			connection.commit()
			# verifica se todos confirmaram
			if self.groupCicleHasStarted(groupId):
				# gera um ciclo aleatorio
				self.generateGroupCicle(groupId)			

		except MySQLdb.Error, e:
			print("Erro no banco de dados: %s"%e)
			print("Tentou-se executar %s"%(query))

		cursor.close()
		connection.close()


	def generateGroupCicle(self,groupId):
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()

		# determina todos os membros do grupo
		cursor.execute("SELECT userId FROM participations WHERE groupId=%d"%(groupId))
		rows = cursor.fetchall()
		users = []
		for r in rows:
			users.append(r[0])
		r = Random()
		r.shuffle(users)
		
		tupples = []
		for a in range(0,len(users)-1):
			tupples.append("(%d,%d,%d)"%(users[a],users[a+1],groupId))
		tupples.append("(%d,%d,%d)"%(users[-1],users[0],groupId))

		query = "INSERT INTO exchanges (fromUser, toUser, groupId) VALUES " + ",".join(tupples)
		try:
			cursor.execute(query)
		except MySQLdb.Error, e:
			print("Erro no banco de dados: %s"%e)
			print("Tentou-se executar %s"%(query))

		# adiciona a data em que o ciclo comecou
		today = "2013/04/02"
		query = "INSERT INTO cicles (groupId,beginDate) VALUES (%d,%s)"%(groupId,today)
		try:
			cursor.execute(query)
		except MySQLdb.Error, e:
			print("Erro no banco de dados: %s"%e)
			print("Tentou-se executar %s"%(query))	
		
		connection.commit()

		cursor.close()
		connection.close()



