__all__ = ['startapp']

from time import sleep
from warnings import warn

try :
	import toga
	from toga.style.pack import Pack
	from travertino.constants import COLUMN
except :
	warn('No toga installed, will fail to open webview')

def _wv_main(port, host) :

	class BalCE(toga.App) :
		
		def startup(self) :
			self.main_window = toga.MainWindow(title=self.formal_name)

			self.webview = toga.WebView(
				on_webview_load=self.on_webview_loaded,
				style=Pack(flex=1)
			)

			main_box = toga.Box(
				children=[
					self.webview,
				],
				style=Pack(
					direction=COLUMN,
				)
			)
			
			self.main_window.content = main_box
			self.webview.url = self.url_input

			self.main_window.show()

		def load_page(self, widget) :
			self.webview.url = self.url_input

		def on_webview_loaded(self, widget) :
			self.url_input = self.webview.url
		
	# track: to remove ugly toolbar (windows tested)
	def _create_impl(self):
		factory_app = self.factory.App
		factory_app.create_menus = lambda *x, **y: None
		factory_app(interface=self)
	BalCE._create_impl = _create_impl

	bapp = BalCE(
		'BalCE',
		'com.hibays.balceapp',
		icon='assets/chem.ico',)
	
	bapp.url_input = f'http://{host if host else "127.0.0.1"}:{port}'

	return bapp.main_loop()

from threading import Thread
from asyncio import new_event_loop, set_event_loop

import multiprocessing as mup

import socket

def is_port_used(port) :
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s :
		s.settimeout(0.4)
		try :
			s.connect(('127.0.0.1', port))
			return True
		except :
			return False
		
def get_free_port() :
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s :
		s.bind(('127.0.0.1', 0))
		return s.getsockname()[1]

def _startst(port, host, auto_open_webbrowser, auto_open_webview, debug) :
	from streamlit.web import bootstrap
	from streamlit import config as st_config
	from balceapp.utils import _app_idx_path

	import os
	_ori_cwd = os.getcwd()
	os.chdir(_app_idx_path)

	st_config.set_option('server.port', port)
	# this works for mutilpages
	st_config.set_option('client.showSidebarNavigation', False)

	if host :
		st_config.set_option('server.address', host)

	# Note: Auto ignore `auto_open_webbrowser` if `auto_open_webview` turned on
	if auto_open_webview or not auto_open_webbrowser :
		st_config.set_option('server.headless', True)

	if debug :
		st_config.set_option('server.runOnSave', True)
		st_config.set_option('client.showErrorDetails', True)
	else :
		st_config.set_option('server.runOnSave', False)
		st_config.set_option('client.showErrorDetails', False)
	
	bootstrap.run('index.py', is_hello=False, args=[], flag_options={})

	os.chdir(_ori_cwd)

def startapp(port=8080, host='', auto_open_webbrowser=True, auto_open_webview=False, debug=False) :
	if is_port_used(port) :
		fp = get_free_port()
		warn(f'Port {port} is used, using port {fp}')
		return startapp(fp, host, auto_open_webbrowser, auto_open_webview, debug)

	ws = mup.Process(target=_startst, args=(port, host, auto_open_webbrowser, auto_open_webview, debug))
	ws.start()

	if auto_open_webview :
		_wv_main(port, host)
		ws.terminate()
	else :
		# to fix ctrl+c ignore
		try :
			while 1 :
				sleep(1000)
		except KeyboardInterrupt :
			ws.terminate()

	ws.join()
	ws.close()
