
import logging
from flask import Flask,  request, render_template,redirect
from search_engine_app.services.MainSearchService import MainSearchService
from search_engine_app.Settings.Settings import Settings
from logging import Formatter
from logging.handlers import RotatingFileHandler
import os

def define_app_setting():
    global app
    app.config.update(dict(
        SECRET_KEY = 'yEfNpgx57l63k<6616Ei^9cT4g,0k:R?CyU"62cT!39ej8m48Y124UR433rI',
        DEBUG = Settings.getAppMode() == 'DEBUG',
        #TESTING = True
    ))
    app.config.from_envvar('SEARCH_ENGINE_APP_SETTINGS', silent=True)


def define_app_routing():
    global app
    # START ROUTING
    @app.route('/', methods=['GET'])
    def search_console():
        return render_template('search_console.html')

    @app.route('/', methods=['POST'])
    def upload_file():
        try:
            response = []
            file = request.files.get('file')
            (good_reponse,wrong_responses,wrong_queries) = MainSearchService.searchOnGoogleFromFile(file)
            return render_template('search_response.html',good_reponse=good_reponse,wrong_responses=wrong_responses,wrong_queries=wrong_queries)
            app.logger.debug('Search result founded sucessfully:{0}'.format(response))
        except Exception as e:
            app.logger.debug('Error during upload_file:{0}'.format(str(e)))

        return response

        # END ROUTING

    @app.route('/url', methods=['GET'])
    def redirect_from_arg_url():
        redirect_url = request.args.get('q', None)
        return redirect(redirect_url)

def define_error_handling():
    global app

    # START ERROR HANDLING
    @app.errorhandler(404)
    def page_not_found(error):
      app.logger.debug('Page was not found')
      return render_template('404.html'), 404




    # END ERROR HANDLING

def define_app_logger():
    # DEFINE LOGGER
    maxBytes = 10 * 1024
    appLogFileName = Settings.getAppLogFile()
    if appLogFileName == "DEFAULT":
        appLogFileName = os.path.join(app.root_path, 'log', 'error.log')
    file_handler = RotatingFileHandler(appLogFileName, mode='a', maxBytes=0, )
    file_handler.setFormatter(Formatter(
        '''
        Message type: %(levelname)s
        Location: %(pathname)s:%(lineno)d
        Module: %(module)s
        Function: %(funcName)s
        Time: %(asctime)s
        Message:
        %(message)s
        '''
    ))
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)






def define_module_behaviour():
    global app
    if __name__ == '__main__':
        serve();


def serve():
    if Settings.getAppMode() == 'PRODUCTION':
        logging.basicConfig(level=logging.ERROR)
        app.run(host='0.0.0.0',port=8888)  # ssl_context='adhoc'
    else:
        ##from  modules.search_engine_app.services.MainSearchService import MainSearchService
        # from  tests.modules.search_engine_app.services.googleSearchTests import googleSearchTests
        ##mockupPath = googleSearchTests.getGoogleResponseMockupFilePath()
        ##MainSearchService.setMockupMode(mockupPath)
        logging.basicConfig(level=logging.DEBUG)
        app.run(debug=True, use_reloader=True, use_debugger=False)  # ssl_context='adhoc'

'''
###################                        ###################
###################    SEARCH ENGINE APP   ###################
###################                        ###################
'''
try:

    app = Flask(__name__)

    define_app_setting()

    define_app_logger()

    define_app_routing()

    define_error_handling()

    define_module_behaviour()


except Exception as e:

    logging.exception(e)
