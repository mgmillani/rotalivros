import MySQLdb

class Database():

	def __init__(self,host,user,passwd,db):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.db = db

	# Determina quais os grupos existentes
	# retorna uma string com uma tabela em formato html
	def makeGroupTable(self):
		table = "<table class='group'>\n"
		connection = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db)
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM groups")
		rows = cursor.fetchall()
		rowsStr = ["<tr><th class='group'> Grupo </th> <th class='group'> Minimo </th> <th class='group'> Maximo </th></tr>\n"]

		numF = len(cursor.description)
		print("Description")
		for k in cursor.description:
			print("Next!")
			for j in k:
				print(j)
		
		i=0		
		for r in rows:
			rowsStr.append("<tr>")			
			if i%2==0:
				rowType = "groupEven"
			else:
				rowType = "groupOdd"
			rowsStr.append("<td class='%s'><a href=/grupo%d>Grupo %d </a></td>"%(rowType,i+1,i+1))
			c=0
			for col in r:
				if cursor.description[c][0] in ("minUsers","maxUsers"):
					rowsStr.append("<td class='%s'>%s</td>"%(rowType,col))
				c+=1
			rowsStr.append("</tr>\n")
			i+=1

		cursor.close()
		connection.close()

		return table + "".join(rowsStr) + "</table>"
		

class GroupPage(WebPage):

	def show(self):

		

class WebPage():

	def __init__(self,database):
		self.database = database

	#retorna a string com o cabecalho de uma pagina
	def header(self):
		f = open("pages/header.html")
		contents = f.read()
		f.close()
		return contents
		
class Busca(WebPage):

	def show(self):
		f = open("pages/busca.html")
		contents = f.read()
		f.close()
		contents += self.database.makeGroupTable()
		contents += "</body>\n</html>\n"
		return self.header() + contents, ".html"

class Home(WebPage):

	def show(self):
		f = open("pages/home.html")
		contents = f.read()
		f.close()
		return self.header() + contents, ".html"
