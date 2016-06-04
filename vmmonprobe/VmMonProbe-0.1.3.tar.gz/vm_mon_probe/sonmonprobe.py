#!/usr/bin/python


import urllib2, time, logging                                                                                                       
import json,urllib2
from threading import  Thread
from VmData import vmdt
from configure import configuration
from logging.handlers import RotatingFileHandler
import inspect, os

class probe(object):
    def init(self,nm,srv):
        global prometh_server
        global node_name
        global logger
        global vm_id
       
        node_name=nm
        prometh_server=srv
        '''
        if os.environ.has_key('PW_URL') and os.environ.has_key('ND_NAME'):
            prometh_server = str(os.environ['PW_URL']).strip()
            node_name = str(os.environ['ND_NAME']).strip()
        else:
            path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            conf = configuration(path+'/node.conf')
            prometh_server = conf.ConfigSectionMap("Prometheus")['server_url']
            node_name = conf.ConfigSectionMap("vm_node")['node_name']
        '''
        #read configuration
        logger = logging.getLogger('dataCollector')
        #hdlr = logging.FileHandler('dataCollector.log', mode='w')
        hdlr = RotatingFileHandler('/var/log/dataCollector.log', maxBytes=10000, backupCount=1)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.WARNING)
        logger.setLevel(logging.INFO)
        vm_id = self.getMetaData()
        if vm_id == None:
            vm_id = node_name
        print vm_id
        logger.info('SP Data Collector')
        logger.info('Promth P/W Server '+prometh_server)
        logger.info('Monitoring Node '+node_name)

    def postNode(self,node_,type_, data_):
        #print data
        url = prometh_server+"/job/"+type_+"/instance/"+node_
        #print url
        logger.info('Post on: \n'+url)
        #logger.info('Post ports metrics: \n'+data_)
        try: 
            req = urllib2.Request(url)
            req.add_header('Content-Type','text/html')
            req.get_method = lambda: 'PUT'
            response=urllib2.urlopen(req,data_,timeout=2)
            code = response.code
            logger.info('Response Code: '+str(code))      
        except urllib2.HTTPError, e:
            logger.warning('Error: '+str(e))
        except urllib2.URLError, e:
            logger.warning('Error: '+str(e))
        
    def getMetaData(self):
        try:
            url = 'http://169.254.169.254/openstack/latest/meta_data.json'
            req = urllib2.Request(url)
            req.add_header('Content-Type','application/json')
        
            response=urllib2.urlopen(req, timeout = 3)
            code = response.code
            data = json.loads(response.read())
            #print json.dumps(data)
            return data["uuid"]
    
        except urllib2.HTTPError, e:
            logger.warning('Error: '+str(e))
        except urllib2.URLError, e:
            logger.warning('Error: '+str(e))
        except ValueError, e:
            logger.warning('Error: '+str(e))

    def collectVM(self,id_):
        global vm_dt
        vm_dt = ''
        while 1:
            vm_dt = vmdt(id_).prom_parser()
            time.sleep(1)
    
    def run(self,node,server):
        self.init(node,server)
        t1 = Thread(target = self.collectVM, args=(vm_id,))
        t1.daemon = True
        t1.start()
    
    
        while 1:
            time.sleep(3)
            self.postNode(node_name,"vnf",vm_dt)



if __name__ == "__main__":
    p=probe()
    p.run()
        


