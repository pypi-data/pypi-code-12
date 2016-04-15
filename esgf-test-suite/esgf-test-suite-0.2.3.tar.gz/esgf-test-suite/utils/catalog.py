import re
import urllib2
from lxml import etree
import multiprocessing
from multiprocessing import Queue
from operator import itemgetter
from StringIO import StringIO

import configuration as config



class ThreddsUtils(object):
        def __init__(self):
		# init
		global in_queue 
		in_queue = multiprocessing.JoinableQueue()
		global out_queue
		out_queue = multiprocessing.Queue()

		global catalog_ns
		catalog_ns = '{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}'

		self.config = config.read_config()
		self.data_node = self.config['nodes']['data_node']

	def chunk_it(self, seq, num):
        	avg = len(seq) / float(num)
        	res = []
        	last = 0.0

        	while last < len(seq):
                	res.append(seq[int(last):int(last + avg)])
                	last += avg

        	return res

	def get_dataset_services(self, dataset, services_def):
		ds_services = []

		# Collecting available services from <serviceName>some_service</serviceName>
		for sv in dataset.iterchildren(tag=catalog_ns + 'serviceName'):
			ds_services.append(services_def[sv.text])
		# Collecting available services from <access serviceName="some_service">
		for acc in dataset.iterchildren(tag=catalog_ns + 'access'):
			try:
				ds_services.append(services_def[acc.get('serviceName')])
                        except:
                                continue

		return ds_services


	def get_dataset_size(self, dataset):
		# Set aggregations size to inf
		if "aggregation" in dataset.get('urlPath'):
			size = float('inf')
		else:
			for si in dataset.iterchildren(tag=catalog_ns + 'dataSize'):
				units = si.get('units')
				if units == 'Kbytes':
                        		size = float(si.text) / 1024
                        	elif units == 'Mbytes':
                        		size = float(si.text)
                        	elif units == 'Gbytes':
                                	size = float(si.text) * 1024
                        	else:
                        		size = float('inf')

		return size

	def get_datasets_list(self, data, services_def):
		datasets_list = []

		# Parsing datasets XML document
		for events, ds in etree.iterparse(StringIO(data), tag=catalog_ns + 'dataset'):
			# Only interested in datasets which have an URL
			if ds.get('urlPath'):
				# Building dataset entry with URL, size and available services
				dataset = []
				dataset.append(ds.get('urlPath'))
                                dataset.append(self.get_dataset_size(ds))
                                dataset.append(self.get_dataset_services(ds, services_def))
                                datasets_list.append(dataset)

		return datasets_list

	def get_services_definition(self, data):
		services_def = {}

		for events, sv in etree.iterparse(StringIO(data), tag=catalog_ns + 'service'):
                	if sv.get('serviceType') != 'Compound':
                        	services_def.update({sv.get('name'):sv.get('serviceType')})

		return services_def

	def worker(self, catalogrefs):
		datasets_list = []

		for cr in catalogrefs:
			try:
				content = urllib2.urlopen(cr)
				data = content.read()
			except:
				continue

			# Parsing services definition
			services_def = self.get_services_definition(data)
			# Parsing datasets
			datasets_list = self.get_datasets_list(data, services_def)

		return datasets_list

	def queue_manager(self):
		for item in iter(in_queue.get, None):
			out_queue.put(self.worker(item))
			in_queue.task_done()
		in_queue.task_done()

	def map_processes(self, chunks):
		processes = []

		# Starting nb_chunk processes calling the queue manager
		for i in chunks:
			processes.append(multiprocessing.Process(target=self.queue_manager))
			processes[-1].daemon = True
			processes[-1].start()

		# Feeding the input queue with chunks
		for cr in chunks:
			in_queue.put(cr)

		# Waiting for every chunk to be processed
		in_queue.join()

		# Feeding the input queue with None to be sure
		for p in processes:
			in_queue.put(None)

		# Collecting results from output queue
		datasets_list = []
		for p in processes:
			datasets_list.extend(out_queue.get())

		in_queue.join()

		for p in processes:
			p.join()

		return datasets_list

	def filter_catalogrefs(self, proj_url, matcher):
		filtered = []

		content = urllib2.urlopen(proj_url)
		for event, cr in etree.iterparse(content, events=('end',), tag=catalog_ns + 'catalogRef'):
        		path = cr.get('{http://www.w3.org/1999/xlink}href')
                        if matcher in path:
                        	filtered.append(re.sub('catalog.xml', '', proj_url) + path)

		return filtered


	def get_catalogrefs(self, projects):
		catalogrefs = []

		for proj_url in projects:
			try:
        			content = urllib2.urlopen(proj_url)
			except:
				continue
		
			# Parsing catalogRef xml entries
			catalogrefs.extend(self.filter_catalogrefs(proj_url, '.fx.'))
                        if len(catalogrefs) == 0:
                                catalogrefs.extend(self.filter_catalogrefs(proj_url, '.mon.'))
                                if len(catalogrefs) == 0:
                                        catalogrefs.extend(self.filter_catalogrefs(proj_url, ''))

        	return catalogrefs

	def get_projects(self):
		projects = []
		main_url = "http://{0}/thredds/catalog/catalog.xml".format(self.data_node);

		try:
			content = urllib2.urlopen(main_url)
		except:
			return projects
			
                for event, cr in etree.iterparse(content, events=('end',), tag=catalog_ns + 'catalogRef'):
			path = cr.get('{http://www.w3.org/1999/xlink}href')
			# Exclude DatasetScans
			if 'thredds' not in path:
				projects.append(re.sub('catalog.xml', '', main_url) + path)

                return projects


	def get_endpoints(self):
		endpoints = []

		# Determining number of processes and chunks
		nb_chunks = multiprocessing.cpu_count() * 16

		# Getting projects href links from main catalog (http://data_node/thredds/catalog/catalog.xml)
		projects = self.get_projects()

		# Getting and chunking catalogrefs href links from project catalogs (ex: http://data_node/thredds/geomip/catalog.xml)
		catalogrefs = self.get_catalogrefs(projects)
		chunked_catalogrefs = self.chunk_it(catalogrefs, nb_chunks)
		
		# Starting multiprocessed work
		endpoints = self.map_processes(chunked_catalogrefs)
		
		return endpoints
