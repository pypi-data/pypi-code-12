import urllib2
import storm.locals as storm
from storm.expr import Asc, Desc
import models
from threading import Thread, Lock
import time
from collections import deque




class Offline:
    """
        Esta classe tem como objetivo guardar dados(payload) numa base
        de dados local e ao fim de um certo tempo(delay) envia os dados
        para um servidor(por ex.) por meio de uma callback(callback)
    """
    _dbpath = None
    _database = None
    _callback = None #def _funtion_name_(data)
    _store = None
    _unsent = None
    _lock = None
    _thread = None
    delay = None
    _DEFAULT_IP='http://84.91.171.94' #google.com



    def __init__(self, dbname, callback, delay=1):
        """
            Args:
                dbname(string) : nome da base de dados
                callback(function): Funcao que e chamada sempre que existem dados. Estrutura, def function_name_ (data): ,
                    em que data e o payload guardado em send. Esta funcao deve retornar um boolean, True, se os dados forem
                    enviados com sucesso, False, caso contrario.
                delay(opcional)(int): temo de espera entre as chamadas a callback
        """

        self._dbpath = 'sqlite:' + dbname
        self._unsent = deque([])
        self._callback = callback
        self._lock = Lock()
        self.delay = delay
        self._create_database()
        self._store = storm.Store(self._database)
        self._create_tables()
        self._store.close()
        self._start()

    def send(self, payload):
        """
            Metodo que guarda o payload numa base de dados local, e evia-o para o cliente por
            meio da callback.

            Args:
                payload(string): Informacao a enviar para o(s) cliente(s), por ex. JSON, '{temperature:20, humidity:29}'
        """

        if self._store!=None:
            self._lock.acquire()
            try:
                self._unsent.append(payload)
            finally:
                self._lock.release()
                time.sleep(self.delay)


    def _create_tables(self):
        try:
            models.Data.create_table(self._store)
            self._store.commit()
        except:     #tabelas ja existem
            #print 'db ja existe'
            pass


    def _create_database(self):
        if self._database==None and self._dbpath!=None:
            self._database = storm.create_database(self._dbpath)


    def _start(self):
        if self._dbpath!=None:
            #inicia um novo thread
            self._thread = Thread(target=self._push_payloads)
            self._thread.daemon = True
            self._thread.start()


    #thread que faz o envio dos dados ao fim de um tempo(delay)
    def _push_payloads(self):

        local_store = storm.Store(self._database)

        def commit():
            try:
                local_store.commit()
            except:
                #print 'locked'
                local_store.rollback()#'database is locked' error


        while True:
            #guarda os dados na base de dados
            self._lock.acquire()
            try:
                while len(self._unsent) > 0:
                    dt = self._unsent.popleft()
                    data = models.Data()
                    data.payload = dt
                    data.sent = False
                    local_store.add(data)
            finally:
                 commit()
                 self._lock.release()



            #envia os dados da base de dados para os consumers
            data = None
            try:
                unsent = local_store.find(models.Data, models.Data.sent == False).order_by(Asc(models.Data.id))
                for data in unsent:
                    if self._callback(data.payload):
                        local_store.remove(data)
                        commit()
                       #print 'enviado'
                    else:
                        #pass
                        break
                       #print 'nao ha internet!'
            finally:
                commit()
                time.sleep(1/10)


    def safe_exit(self):
        """
            IMPORTANTE!!!
            QUANDO O PROGRAMA TERMINA, PODERAM EXISTIR DADOS QUE AINDA NAO
            FORAM GUARDADOS LOCALMENTE, POR ISSO, RECOMENDAMOS VIVAMENTE O USO DESTE METODO
            E ACONSELHAVEL COLOCAR A INSTRUCAO NO FINAL, PORQUE VAI BLOQUEAR
            AS INSTRUCOES SEGUINTES ATE TEREM SIDO GUARDADAS TODAS AS INFORMACOES
            LOCALMENTE
        """
        while True:
            time.sleep(1)


    @staticmethod
    def active_internet_connection(consumer_url=_DEFAULT_IP, timeout=1):
        """
            Esta funcao serve para verificar se existe uma conexao ao
            parametro <consumer_url>

            Args:
                consumer_url(string): endereco do cliente
                timeout(opcional)(int):
        """
        try:
            response = urllib2.urlopen(consumer_url, timeout=timeout)
            return True
        except:
            pass
        return False
