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

	def show(self,postVars = {}, path = "", user = User()):
		if path in self.pageMap:
			return self.pageMap[path].show(postVars,path,user)
		#verifica se eh a pagina de um grupo
		else:
			if path[:5] == "grupo":
				return self.groupPage.show(postVars,path,user)
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

	def makeGroupLink(self,groupId=0):
		return "<a href='/grupo%d'>Grupo %d</a>"%(groupId,groupId)

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
		groupList = self.database.getUsersGroups(user)
		tableData = [[self.makeGroupLink(g.id),g.book] for g in groupList]
		table = self.makeTable(tableData, ["Grupo","Livro Oferecido"] )
		return self.header() + table + self.tail(), ".html"

class GroupPage(WebPage):

	# pagina que mostra um grupo
	def show(self,postVars = {}, path = "grupo1", user = User()):
		groupId = path[5:]



		groupInfo = self.database.getGroupInfo(groupId)
		#lista os livros oferecidos
		tableData = [groupInfo.books[i] + groupInfo.userInfo[i] for i in range(groupInfo.numMembers)]
		#tabela com o que cada usuario oferece
		infoTable = self.makeTable(tableData,["Título","Autor","Avaliações Positivas","Avaliações Negativas"])
		return self.header() + infoTable + self.tail(), ".html"

class GroupSearch(WebPage):

	def show(self,postVars = {}, path = "busca", user = User()):
		f = open("pages/busca.html")
		contents = f.read()
		f.close()
		groupList = self.database.getGroupList()
		tableData = [ [self.makeGroupLink(g.id),g.minUsers,g.maxUsers,g.maxTime] for g in groupList ]
		contents += self.makeTable(tableData,["Grupo","Min", "Max", "Tempo Máximo"])
		contents += "</body>\n</html>\n"
		return self.header() + contents, ".html"

class Home(WebPage):

	def show(self,postVars = {}, path = "home", user = User()):
		f = open("pages/home.html")
		contents = f.read()
		f.close()
		return self.header() + contents, ".html"
