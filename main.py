#!/usr/bin/env python

import time
import BaseHTTPServer
import os
import pageHandlers
import cgi
from mimetypes import types_map
from urlparse import urlparse, parse_qs

HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 9000 # Maybe set this to 9000.

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def do_POST(self):
		print("POST RECEIVED")

		ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
		if ctype == 'multipart/form-data':
			postvars = cgi.parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers.getheader('content-length'))
			postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}
		self.postVars = postvars

		self.do_GET()

	def do_GET(self):
		print("GET RECEIVED")
		"""Respond to a GET request."""
		self.init()
		if self.path[0] == "/":
			self.path = self.path[1:]
		if self.path == "":
			self.path = "home"
		page,ext = self.pageToShow(self.path)
		#fname,ext = os.path.splitext(page)
		if ext in (".html", ".css"):
			self.send_response(200)
			self.send_header('Content-type', types_map[ext])
			self.end_headers()
			self.wfile.write(page)

	#determina qual conteudo vai ser retornado
	#retorna uma string e a extensao do arquivo
	def pageToShow(self,name):
		if name in self.pageMap:
			return self.pageMap[name].show()
		else:
			f = open(name)
			contents = f.read()
			f.close()
			fname,ext = os.path.splitext(name)
			return contents,ext

	#inicializa o mapa das paginas se ele nao foi inicializado
	def init(self):
		try:
			self.hasBeenInitialized
		except:
			self.pageMap = {}
			database = pageHandlers.Database(host="localhost",user="engsoft",passwd="wingedlizards",db="rotalivros")
			self.pageMap["home"] = pageHandlers.Home(database)
			self.pageMap["busca"] = pageHandlers.Busca(database)
			self.hasBeenInitialized = True
		else:
			return

if __name__ == '__main__':
	server_class = BaseHTTPServer.HTTPServer
	httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
	print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)