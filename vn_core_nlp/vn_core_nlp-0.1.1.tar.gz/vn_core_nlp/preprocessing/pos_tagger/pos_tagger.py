from subprocess import Popen
import os


path = os.path.dirname(os.path.realpath(__file__)) + '/vn.hus.nlp.tagger-4.2.0-bin'


class POSTagger(object):
    def pos_tagger(self, input_dir, output_dir, output_type='', underscore=''):
        Popen(['chmod', '-R', '777', './vnTagger.sh'], cwd=path)
        Popen(['./vnTagger.sh', '-i',  input_dir, '-o', output_dir, output_type, underscore], cwd=path).communicate()
