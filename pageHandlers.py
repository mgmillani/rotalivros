# -*- coding: utf8 -*-

from database import *
from sys import stderr
from struct import *
from user import *

class PageNotFound(Exception):
	pass

class MainHandler():

	def __init__(self,database):
		self.database = database
		self.pageMap = {}
		self.pageMap["home"] = Home(database)
		self.pageMap["grupos"] = UserGroups(database)
		self.pageMap["busca"] = GroupSearch(database)
		self.groupPage = GroupPage(database)
		self.formPage = FormPage(database)

	def show(self,postVars = {}, path = "", user = User()):
		if path in self.pageMap:
			return self.pageMap[path].show(postVars,path,user)
		#verifica se eh a pagina de um grupo
		else:
			if path[:5] == "grupo":
				return self.groupPage.show(postVars,path,user)
			elif path[:4] == "form":
				return self.formPage.show(postVars,path,user)
			else:
				raise(PageNotFound)

class WebPage():

	def __init__(self,database):
		self.database = database

	#retorna a string com o cabecalho de uma pagina
	def header(self):
		f = open("pages/header.html")
		contents = f.read()
		f.close()
		return contents

	def tail(self):
		f = open("pages/tail.html")
		contents = f.read()
		f.close()
		return contents

	def makeGroupLink(self,groupId=0,groupName=""):
		return "<a href='/grupo%d'>%s</a>"%(groupId,groupName)

	def makeTable(self,data = [], titles = []):
		# titulo
		table = ["<table class='table'><tr>"]
		for t in titles:
			table.append("<th class='header'> %s </th>"%(t))
		table.append("\n")
		table.append("</tr>")

		# linhas
		i=0
		for d in data:
			if i==1:
				colType = "rowOdd"
				i=0
			else:
				colType = "rowEven"
				i=1
			table.append("<tr>\t")
			for col in d:
				table.append("<td class='%s'> %s </td>"%(colType,col))
			table.append("\t</tr>\n")

		table.append("</table>")
		return "".join(table)


class UserGroups(WebPage):

	# lista todos os grupos no qual o usuario faz parte
	def show(self,postVars = {}, path = "grupo", user = User()):
		groupList = self.database.getUsersGroups(user.userId)
		tableData = [[self.makeGroupLink(g.id,g.name),g.book] for g in groupList]
		table = self.makeTable(tableData, ["Grupo","Livro Oferecido"] )
		return self.header() + table + self.tail(), ".html"

class GroupPage(WebPage):

	# pagina que mostra um grupo
	def show(self,postVars = {}, path = "grupo1", user = User()):
		groupId = int(path[5:])

		#determina se o botao de desistencia foi pressionado
		if 'bailout' in postVars:
			#remove o usuario do grupo
			self.database.removeUserFromGroup(user.userId,groupId)
		#caso o usuario tente se juntar ao grupo
		elif 'join' in postVars:
			book = Struct()
			book.title = postVars['bookTitle'][0]
			book.author= postVars['bookAuthor'][0]
			book.year = postVars['bookYear'][0]
			book.publisher = postVars['bookPublisher'][0]
			book.edition = postVars['bookEdition'][0]
			book.isbn = postVars['bookISBN'][0]
			book.language = postVars['bookLanguage'][0]
			if book.title != "" and book.author != "":
				self.database.addUserToGroup(user.userId,groupId,book)
		elif 'confirm' in postVars:
			self.database.confirmUserParticipation(user.userId,groupId)

		groupInfo = self.database.getGroupInfo(groupId)
		#lista os livros oferecidos
		tableData = [groupInfo.books[i] + ["%d+/%d-"%(groupInfo.userInfo[i][0],groupInfo.userInfo[i][1])] for i in range(groupInfo.numMembers)]
		#tabela com o que cada usuario oferece
		infoTable = self.makeTable(tableData,["Título","Autor","Avaliações do Usuário"])

		contents = ""
		# verifica a relacao entre o usuario e o grupo
		if self.database.isModeratorOf(user.userId,groupId):
			contents += "Adicionar funcionalidades do moderador"
		elif self.database.isMemberOf(user.userId,groupId):
			if not self.database.userHasConfirmed(user.userId,groupId):
				# Adiciona opcoes de desistencia
				f = open("pages/bailout.html","rt")
				contents += f.read()%(groupId)
				f.close()
				# se o grupo estiver cheio, adiciona a possiblidade de confirmar a participação
				if self.database.isFull(groupId):
					f = open("pages/confirm.html","rt")
					contents += f.read()%(groupId)
					f.close()
			# se o ciclo de trocas ja comecou, mostra ao usuario para quem deve mandar o livro, e quanto tempo tem para faze-lo
			elif self.database.groupCicleHasStarted(groupId):
				contents += "Ciclo de trocas já começou"
			# caso contrario, apenas informa que o usuario ja confirmou sua participacao
			else:
				contents += "Participação no grupo já foi confirmada"
		else:
			# Adiciona a possiblidade de se juntar ao grupo
			f = open("pages/join.html","rt")
			contents += f.read()%(groupId)
			f.close()


		'''
		elif:
			# caso esteja cheio, libera as opcoes de desistencia e de confirmacao
			f = open("pages/groupMember.html")
			contents = f.read()
			f.close()
		'''
		return self.header() + contents + infoTable + self.tail(), ".html"

class GroupSearch(WebPage):

	def show(self,postVars = {}, path = "busca", user = User()):
		f = open("pages/busca.html")
		contents = f.read()
		f.close()
		groupList = self.database.getGroupList(user.userId)
		tableData = [ [self.makeGroupLink(g.id,g.name) , "%d/%d"%(g.numMembers,g.maxUsers) , "%d dias"%(g.maxTime) , g.private] for g in groupList ]
		contents += self.makeTable(tableData,["Grupo","Usuários", "Tempo Máximo","Privado"])
		contents += "</body>\n</html>\n"
		return self.header() + contents + self.tail(), ".html"

class FormPage(WebPage):

	def show(self,postVars = {}, path = "form", user = User()):
		# usuario desistiu de algum grupo
		if 'bailout' in postVars:
			f = open("pages/bailoutForm.html")
			contents = f.read()%(int(postVars['group'][0]))
			f.close()
		# usuario ja respondeu um formulario
		elif 'answered' in postVars:
			if postVars['answered'][0] == 'bailout':
				f = open("pages/bailoutFormAnswered.html")
				contents = f.read()
				f.close()
				self.database.removeUserFromGroup(user.userId,int(postVars['group'][0]))
			else:
				contents = ""

		return self.header() + contents + self.tail(), ".html"

class Home(WebPage):

	def show(self,postVars = {}, path = "home", user = User()):
		f = open("pages/home.html")
		contents = f.read()
		f.close()
		return self.header() + contents + self.tail(), ".html"

