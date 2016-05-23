#!-*-coding:utf-8 -*-
#!/usr/bin/env

from scipy.io import arff
import sys

class MergeArff:
	def __init__(self, first_arff, second_arff, output):
		self.files = []
		self.attributes = {}
		self.data = []
		self.output = output

		print "Reading arff files"
		data, meta = arff.loadarff(open(first_arff))
		self.files.append({
			'data': data,
			'meta': meta
			})

		data, meta = arff.loadarff(open(second_arff))
		self.files.append({
			'data': data,
			'meta': meta
			})

		self.calculate_nominal_fields()
		self.merge_data_fields()
		self.save_as_arff()

	def calculate_nominal_fields(self):
		#Detect nominal fields
		for attribute in self.files[0]['meta']._attributes:
			attribute_type = self.files[0]['meta']._attributes[attribute][0]
			if attribute_type == 'nominal':
				self.attributes[attribute] = list(self.files[0]['meta']._attributes[attribute][1])

		#Merge nominal fields
		for attribute in self.attributes:
			merge_fields = list(self.files[1]['meta']._attributes[attribute][1])
			self.attributes[attribute] = list(set(self.attributes[attribute] + merge_fields))

	def merge_data_fields(self):
		self.data = []
		for row in self.files[0]['data'].tolist():
			row = list(row)
			for (i,value) in enumerate(row):
				row[i] = str(value)
			self.data.append(",".join(row))

		for row in self.files[1]['data'].tolist():
			row = list(row)
			for (i,value) in enumerate(row):
				row[i] = str(value)
			self.data.append(",".join(row))

	def save_as_arff(self):
		print "Writing new arff file"
		new_file = open(self.output, 'w')
		#Write relation
		new_file.write("@relation %s \n\n" % self.output)

		#Write attributes
		attributes = self.files[0]['meta']._attributes.keys()
		attributes.sort()

		for attribute in attributes:
			attribute_type = self.files[0]['meta']._attributes[attribute][0]
			if attribute_type == 'nominal':
				options = self.attributes[attribute]
				new_file.write("@attribute %s {%s}\n" % (attribute, ",".join(options)))
			else:
				new_file.write("@attribute %s %s\n" % (attribute, attribute_type))

		#Write data
		new_file.write('\n@data\n')
		new_file.write('\n'.join(self.data))
		new_file.close()

def main():
	MergeArff(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
	main()
	
