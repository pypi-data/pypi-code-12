import json
import cchardet as chardet
from .exceptions import Error
from .reader import VectorReader
from .convert import Converter

class EncodingError(Error):
    pass

def convert_to_geojson(filepath):
    filename = 'res.geojson'
    layers = []
    vr = VectorReader(filepath)
    converter = Converter('GeoJSON')
    for layer_num in range(len(vr)):
        tmp_dir = converter.convert_ds(vr.ds, filename, layer_num)
        layers.append(open(tmp_dir.file_list()[0]).read())
    return layers

def convert_to_geojson_data(filepath, encoding=None, unicode_errors='strict'):
    layers_geojson = []
    for json_str in convert_to_geojson(filepath):
        if encoding:
            try:
                json_str = unicode(json_str, encoding=encoding)
            except UnicodeDecodeError:
                raise EncodingError('could not decode file via specified encoding')
        else:
            try:
                json_str = unicode(json_str)
            except UnicodeDecodeError:
                detect = chardet.detect(json_str)
                if detect:
                    try:
                        json_str = unicode(json_str, encoding=detect.get('encoding'), errors=unicode_errors)
                    except UnicodeDecodeError:
                        raise EncodingError('file has unknown encoding')
        
        try:
            '''
            Decode one more time if we have double encoded utf-8 string. This may produced by utf-8 encoded shapefile w/o .cpg file.
            OGR default encoding for shapefile is ascii, so output geojson-file contains double utf-8 encoded string
            '''
            ascii = json_str.encode('latin1')
            detect = chardet.detect(ascii)
            if detect and detect.get('encoding').lower() == 'utf-8':
                json_str = ascii.decode('utf-8', errors=unicode_errors)
        except UnicodeEncodeError:
            pass
        
        layers_geojson.append(json.loads(json_str))
    return layers_geojson

def convert_to_merged_geojson_data(filepath):
    layers = convert_to_geojson_data(filepath)
    result = layers[0]
    for layer in layers[1:]:
        result['features'] = result['features'] + layer['features']
    return result
