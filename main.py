#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import BaseHTTPServer
import os
import cgi
from mimetypes import types_map
from urlparse import urlparse, parse_qs

import pageHandlers
from user import *

HOST_NAME = 'localhost'
PORT_NUMBER = 9000

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def do_POST(self):
		print("POST RECEIVED")
		self.init()

		ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
		if ctype == 'multipart/form-data':
			postvars = cgi.parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers.getheader('content-length'))
			postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}
		self.postVars = postvars.copy()

		self.do_GET()

	def do_GET(self):
		"""Respond to a GET request."""
		#print("GET RECEIVED")
		self.init()
		if self.path[0] == "/":
			self.path = self.path[1:]
		if self.path == "":
			self.path = "home"

		page,ext = self.pageToShow(self.path)
		if ext in (".html", ".css"):
			self.send_response(200)
			self.send_header('Content-type', types_map[ext])
			self.end_headers()
			self.wfile.write(page)

	#determina qual conteudo vai ser retornado
	#retorna uma string e a extensao do arquivo
	def pageToShow(self,name):
		try:
			return self.pageHandler.show(self.postVars,name,self.loggedUser)
		except pageHandlers.PageNotFound:
			print("Default behaviour for %s"%(name))
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
			self.postVars = {}
			database = pageHandlers.Database(host="localhost",user="engsoft",passwd="wingedlizards",db="rotalivros")
			self.pageHandler = pageHandlers.MainHandler(database)
			self.loggedUser = User(userId=0)
			self.hasBeenInitialized = True

if __name__ == '__main__':
	server_class = BaseHTTPServer.HTTPServer
	httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
	print (time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	print (time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))