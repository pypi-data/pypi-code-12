from kombu import Exchange, Queue
import os
BROKER_URL = os.environ['CELERY_BROKER']
CELERY_RESULT_BACKEND = 'rpc'
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']


gwas_exchange = Exchange('gwas', type='direct')
enrichment_exchange = Exchange('enrichment',type='direct')



CELERY_QUEUES = (
    Queue('gwas.portal.worker.slow', gwas_exchange, routing_key='gwas.portal.worker.slow'),
    Queue('gwas.portal.worker.fast', gwas_exchange, routing_key='gwas.portal.worker.fast'),
    Queue('enrichment',enrichment_exchange,routing_key='enrichment')
)

   
CELERY_ROUTES = {
        'gwaportalpipeline.gwas.run_gwas':{'queue':'gwas.portal.worker.fast'},
        'gwaportalpipeline.enrichment.candidate_gene_list_enrichment':{'queue':'enrichment'}
}


