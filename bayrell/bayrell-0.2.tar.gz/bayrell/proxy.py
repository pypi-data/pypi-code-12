# -*- coding: utf-8 -*-

import asyncio
from foruse import *
from bayrell_aio import *


class MyClient(HttpClient):
	
	def data_received(self, data):
		super().data_received(data)
		#print (data)

#!MyClient


class HTTPProxyServer(HTTPServer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.app_server = kwargs.get('app_server')
		self.client = None
	
	async def handle_request_end(self, request, answer):
		await super().handle_request_end(request, answer)
		
		if self.client is not None:
			self.client.close()
		
		
	async def handle_request(self, request):
		self._log.debug3 ('handle_request')
		
		try:
			client_ip, client_port = self._transport.get_extra_info('peername')
			server_ip, server_port = self._transport.get_extra_info('sockname')
			
			# парсим path, на выходе получаем url
			path = request.get_path()
			host = request.get_header('host', server_ip)
			url = UrlSplitResult()
			url.path = path
			if host is not None:
				arr = host.split(':')
				url.hostname = xarr(arr, 0)
				url.port = xarr(arr, 1)
			url = urlparse2(str(url))
			
			# Ищем приложение
			app, find = self.app_server.find_app(url)
			if app is None:
				return await self.create_error_answer(404)
			
			# Соединяемся с приложением
			filename = app.get_socket_path()
			
			try:
				self.client = await MyClient.connect_unix(filename, loop = self._loop)
			except ConnectionRefusedError as e:
				self._log.debug ('Failed to connect to app "%s"' % (app.api_name), color='b_red')
				return await self.create_error_answer(504)
			
			# Прописываем заголовки
			request.set_header('HOST', host)
			request.set_header('SERVER_NAME', url.hostname)
			request.set_header('SCRIPT_NAME', find.path)
			request.set_header('REQUEST_URI', request.get_path())
			request.set_header('QUERY_STRING', url.query)
			request.set_header('X_FORWARDED_FOR', client_ip)
			request.set_header('X_REAL_IP', client_ip)
			request.set_header('REMOTE_PORT', client_port)
			request.set_header('SERVER_PORT', server_port)
			request.set_header('SERVER_PROTOCOL', request.get_http_version())
			#request.set_header('HTTPS', 'on')
			
			# Меняем путь запроса
			old_path = clone(request.get_path())
			request.set_path(path.replace(find.path, ''))
			
			# Отправляем запрос и получаем ответ
			request.set_header('Connection', 'close')
			await self.client.send_request(request)
			answer = await self.client.get_answer()
			
			# Восстанавливаем старый путь
			request.set_path(old_path)
			
			# Отправляем ответ клиенту
			if answer is not None:
				answer.set_header('Connection', 'close')
				return answer
			
			return await self.create_error_answer(504)
		
		except ConnectionRefusedError as e:
			self._log.debug ('connection refused %s' % (e), color='b_red')
			return await self.create_error_answer(504)
		
		except:
			print (get_traceback())
			return await self.create_error_answer(504)

		return None		

#!ProxyServer