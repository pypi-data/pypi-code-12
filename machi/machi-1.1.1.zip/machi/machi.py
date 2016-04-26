# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Machina.py:  Alpha -0.01
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#

import requests
import json
import webbrowser
import os
import csv
import datetime

class Machina:

    # Gets a var's value from opened session
    def get(self, variableName, defaultValue=None):
        if self.session is None:
            raise Exception('Session not started')
        if variableName in self.session:
            return self.session[variableName]
        return defaultValue

    # Sets a var's value to opened session
    def set(self, variableName, value=None):
        if self.session is None:
            raise Exception('Session not started')
        self.session[variableName] = value

    def __init__(self):
        self.session = None

    def startSession(self, username, password, serverURL='https://charts.machi.na/'):
        if self.session is not None:
            raise Exception('Session already started')
        self.session = {}
        self.set('serverURL', serverURL)
        self.set('username', username)
        self.requestMachina('api/user/authenticateAccount', auth=(username, password))

    # Call end on exit
    def __exit__(self):
        self.endSession()

    # Destroy the opened session and close the model
    def endSession(self):
        if self.session is None:
            return
        self.closeModel()
        self.session = None
        return True

    # Builds service URL from opened session's serverURL plus path
    def buildURL(self, path=''):
        if path.startswith('http'):
            return path
        return self.get('serverURL').strip('/')+'/'+path.strip('/')

    # Main requesting message
    def requestMachina(self, url, parameters=None, method='POST', auth=None):
        if parameters is None:
            parameters = {}
        if self.get('modelName') is not None:
            parameters['modelName'] = self.get('modelName')
        headers = {'access_token': self.get('access_token')}
        url = self.buildURL(url)
        if method == 'POST':
            req = requests.post(url, auth=auth, data=parameters, headers=headers)
        else:
            req = requests.get(url, auth=auth, data=parameters, headers=headers)
        if req.status_code != 200:
            raise Exception(req.text)
        if 'access_token' in req.headers:
            self.set('access_token', req.headers['access_token'])
        d = req.json()
        if 'error' in d:
            raise Exception(d['error'])
        if 'result' in d:
            return d['result']
        return d

    # Main requesting message to model worker
    def sendMessageToMW(self, messageParams=None):
        result = self.requestMachina('api/user/kafka/sendMessageToMW', messageParams)
        return result

    # Retrieve all user's models
    def listModels(self):
        message = {'messageType': 'ListModels'}
        models = self.sendMessageToMW(message)['models']
        self.set('models', models)
        return models

    # Open the model
    def openModel(self, modelName='default'):
        self.set('modelName', modelName)
        # Update the model's rows
        return self.getModel()

    # Close the model
    def closeModel(self):
        self.set('modelName', None)

    # Gets the model's rows
    def getModel(self):
        message = {'messageType': 'GetModel'}
        self.set('modelRows', self.sendMessageToMW(message)['rows'])
        return self.get('modelRows')

    # removes all rows from model
    def clearModel(self, updateRows=True):
        message = {'messageType': 'ClearModel'}
        result = self.sendMessageToMW(message)
        if updateRows:  # Update the model's rows
            self.getModel()
        return result

    # columns we want
    #      "Row"     = character(0),
    #      "Query"   = character(0)
    #            BacktestName = session$model$backtest$backtestName,
    #            PandL = session$model$backtest$pnl,
    #            NumTrades = session$model$backtest$ntrades,
    #            SharpeRatio = session$model$backtest$sharpe,
    #            SortinoRatio = session$model$backtest$sortino)
    def viewModel(self):
        os.system('cls')
        print(' Row\t|\tQuery')  # | PandL | NumTrades | SharpeRatio | SortinoRatio'
        print ('----------------------------------')
        for row in self.get('modelRows'):
            print (row['index']+'\t|\t'+row['query'])

    # undoes last operation on model (addRow or clear)
    def undo(self, updateRows=True):
        message = {'messageType': 'Undo'}
        result = self.sendMessageToMW(message)
        if updateRows:  # Update the model's rows
            self.getModel()
        return result

    # undoes last operation on model (addRow or clear)
    def addRow(self, query, updateRows=True, startTime='', endTime='', includeData=False):
        message = {'messageType': 'AddRow', 'query': query, 'startTime': startTime,
                   'endTime': endTime, 'includeData': includeData}
        result = self.sendMessageToMW(message)
        if updateRows:  # Update the model's rows
            self.getModel()
        return result

    # Get row, optionally with data
    def getRow(self, rowIndex, startTime='', endTime='', includeData=False):
        message = {'messageType': 'GetRow', 'rowIndex': rowIndex, 'startTime': startTime,
                   'endTime': endTime, 'includeData': includeData}
        return self.sendMessageToMW(message)

    # Get timeseries, optionally with data
    def getTimeSeries(self, query, startTime='', endTime='', includeData=False):
        message = {'messageType': 'GetTimeSeries', 'query': query, 'startTime': startTime,
                   'endTime': endTime, 'includeData': includeData}
        return self.sendMessageToMW(message)

    # List backtest configurations
    def listBacktestConfigurations(self):
        message = {'messageType': 'ListBacktestConfigurations'}
        return self.sendMessageToMW(message)

    # Get backtest configuration
    def getBacktestConfiguration(self, backtestName):
        message = {'messageType': 'GetBacktestConfiguration', 'backtestName': backtestName}
        return self.sendMessageToMW(message)

    # Set backtest configuration
    def setBacktestConfiguration(self, backtestName, backtest):
        message = {'messageType': 'SetBacktestConfiguration', 'backtestName': backtestName, 'backtest': backtest}
        return self.sendMessageToMW(message)

    # Export the time series data to csv
    @staticmethod
    def writeCSV(filename, timeSeriesData):
        f = csv.writer(open(filename, 'w'), lineterminator='\n')
        for day in timeSeriesData:
            startTime = datetime.datetime.strptime(day['startTime'], "%Y%m%dT%H%M")
            for bar in day['data']:
                f.writerow([startTime.strftime("%Y%m%dT%H%M"), bar])
                startTime = startTime + datetime.timedelta(minutes=1)

    # Open the remote chart page
    def getRemoteChartUrl(self, openBrowser=True):
        browserURL = self.buildURL('remoteChart?username=' + self.get('username'))
        if openBrowser:
            webbrowser.open(browserURL)
        return browserURL

    # Open the remote chart page
    def openRemoteChartForFirstTime(self):
        isConnected = self.requestMachina('api/user/remoteChart/remoteChartConnected')
        return self.getRemoteChartUrl(not isConnected)

    # Draw series data to the remoteChart page
    # seriesDataList - such as {'GOOG':[], 'SPY':[]}
    def drawSeries(self, seriesDataList):
        seriesDataList = json.dumps(seriesDataList)
        params = {'seriesData': seriesDataList}
        # send data to user's browser
        self.requestMachina('api/user/remoteChart/sendMessageToRemoteChart', params)
        return self.openRemoteChartForFirstTime()

    # Draw rows to the remoteChart page
    def drawRows(self, rowsArray=None, startTime=None, endTime=None):
        params = {'rows': rowsArray, 'startTime': startTime, 'endTime': endTime}
        # send data to user's browser
        self.requestMachina('api/user/remoteChart/sendMessageToRemoteChart', params)
        return self.openRemoteChartForFirstTime()
