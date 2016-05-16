# IPython log file

from cairo_helpers.surface import SurfaceManager, AlphaSurfaceManager, np_cairo_view, composite_surface
from pygtkhelpers.ui.objectlist import get_list_store, add_columns
import pandas as pd
surface_manager = AlphaSurfaceManager(parent.canvas_slave.surfaces)
surfaces = pd.DataFrame(surface_manager.surfaces.items(), columns=['name', 'surface'])
surfaces['alpha'] = [surface_manager.alphas[k] for k in surfaces['name']]
window = gtk.Window(); tree_view = gtk.TreeView(); window.add(tree_view); window.show_all()
df_py_dtypes, list_store = get_list_store(surfaces)
add_columns(tree_view, list_store, df_py_dtypes.ix[['name', 'alpha']])
column = tree_view.get_columns()[1]
column.get_name()
column.get_title()
df_py_dtypes.ix[column.get_title()]
df_py_dtypes.ix[column.get_title()].i
list_store[df_py_dtypes.ix[column.get_title()].i]
surfaces
#surfaces = pd.DataFrame(surface_manager.surfaces.items(), columns=['name', 'surface'])
surfaces = pd.DataFrame(surface_manager.surfaces.items(), columns=['name', 'surface'])
surfaces['alpha'] = [surface_manager.alphas[k] for k in surfaces['name']]
surfaces
surfaces
cell_renderer.connect('edited', dump, column)
column = tree_view.get_columns()[1]
cell_renderer = column.get_cell_renderers()[0]
cell_renderer.connect('edited', dump, column)
def dump(*args):
    import pprint
    pprint.pprint(args)
    
cell_renderer.connect('edited', dump, column)
cell_renderer.props.editable
cell_renderer.props.editable = True
adjustment = gtk.Adjustment(1, 0, 1, .1, .1, 0)
cell_renderer.props.editable = True
cell_renderer.props.adjustment = gtk.Adjustment(1, 0, 1, .1, .1, 0)
cell_renderer.props.digits = 2
cell_renderer.connect('edited', dump, column, list_store, df_py_dtypes, surfaces)
cell_renderer.disconnect_by_func(dump)
cell_renderer.disconnect_by_func(dump)
cell_renderer.disconnect_by_func(dump)
cell_renderer.connect('edited', dump, column, list_store, df_py_dtypes, surfaces)
data = {}
#cell_renderer.connect('edited', dump, column, list_store, df_py_dtypes, surfaces, data)
cell_renderer.disconnect_by_func(dump)
cell_renderer.disconnect_by_func(dump)
def dump(*args):
    import pprint
    args[-1]['result'] = args
    
cell_renderer.connect('edited', dump, column, list_store, df_py_dtypes, surfaces, data)
data['result']
column, list_store, df_py_dtypes, surfaces, result = data['result']
column, list_store, df_py_dtypes, surfaces = data['result']
cell_renderer, column, list_store, df_py_dtypes, surfaces, result = data['result']
cell_renderer, column, list_store, df_py_dtypes, surfaces, result = data['result']
len(data['result'])
cell_renderer, iter, column, list_store, df_py_dtypes, surfaces, result = data['result']
cell_renderer, iter, new_value, column, list_store, df_py_dtypes, surfaces, result = data['result']
new_value
cell_renderer, iter, new_value, column, list_store, df_py_dtypes, surfaces, result = data['result']
cell_renderer
list_store[iter]
list_store[iter][df_py_types.ix[column.get_name()]]
list_store[iter][df_py_dtypes.ix[column.get_name()]]
list_store[iter][df_py_dtypes.ix[column.get_name()].i]
list_store[iter][df_py_dtypes.ix[column.get_name()].i]
surfaces.iloc[int(iter)]
surfaces.iloc[int(iter)][column.get_name()]
surfaces.iloc[int(iter)][column.get_name()]
cell_renderer.disconnect_by_func(dump)
cell_renderer.disconnect_by_func(dump)
get_ipython().magic(u'doctest_mode')
def dump(*args):
    args[-1]['result'] = args
    
cell_renderer.connect('edited', dump, column, list_store, df_py_dtypes, surfaces, data)
cell_renderer, iter, new_value, column, list_store, df_py_dtypes, surfaces, result = data['result']
list_store[iter][df_py_dtypes.ix[column.get_name()].i]
surfaces.iloc[int(iter)][column.get_name()]
cell_renderer.disconnect_by_func(dump)
def on_edited(cell_renderer, iter, new_value, column, list_store, df_py_dtypes, df_data):
    list_store[iter][df_py_dtypes.ix[column.get_name()].i] = new_value
    surfaces.iloc[int(iter)][column.get_name()] = new_value
    
cell_renderer.connect('edited', dump, column, list_store, df_py_dtypes, surfaces)
cell_renderer.disconnect_by_func(dump)
cell_renderer.connect('edited', on_edited, column, list_store, df_py_dtypes, surfaces)
cell_renderer.disconnect_by_func(dump)
cell_renderer.disconnect_by_func(on_edited)
def on_edited(cell_renderer, iter, new_value, column, list_store, df_py_dtypes, df_data):
    column_name = column.get_name()
    dtype_row = df_py_dtypes.ix[column_name]
    list_store[iter][dtype_row.i] = dtype_row.dtype(new_value)
    df_data.iloc[int(iter)][column_name] = dtype_row.dtype(new_value)
    
cell_renderer.connect('edited', on_edited, column, list_store, df_py_dtypes, surfaces)
cell_renderer.disconnect_by_func(on_edited)
def on_edited(cell_renderer, iter, new_value, column, list_store, df_py_dtypes, df_data):
    column_name = column.get_name()
    i, dtype = df_py_dtypes.ix[column_name]
    list_store[iter][i] = dtype(new_value)
    df_data.iloc[int(iter)][column_name] = dtype(new_value)
    
cell_renderer.connect('edited', on_edited, column, list_store, df_py_dtypes, surfaces)
cell_renderer.disconnect_by_func(on_edited)
def on_edited(cell_renderer, iter, new_value, column, list_store, df_py_dtypes, df_data):
    column_name = column.get_name()
    i, dtype = df_py_dtypes.ix[column_name]
    list_store[iter][i] = dtype(new_value)
    df_data.iloc[int(iter), column_name] = dtype(new_value)
    
cell_renderer.connect('edited', on_edited, column, list_store, df_py_dtypes, surfaces)
cell_renderer.disconnect_by_func(on_edited)
def on_edited(cell_renderer, iter, new_value, column, list_store, df_py_dtypes, df_data):
    column_name = column.get_name()
    i, dtype = df_py_dtypes.ix[column_name]
    list_store[iter][i] = dtype(new_value)
    df_data.loc[int(iter):int(iter) + 1, column_name] = dtype(new_value)
    
cell_renderer.connect('edited', on_edited, column, list_store, df_py_dtypes, surfaces)
surfaces
surfaces
#def on_edited(cell_renderer, iter, new_value, column, list_store, df_py_dtypes, df_data):
cell_renderer.disconnect_by_func(on_edited)
cell_renderer.disconnect_by_func(on_edited)
def on_edited(cell_renderer, iter, new_value, column, list_store, df_py_dtypes, df_data):
    column_name = column.get_name()
    i, dtype = df_py_dtypes.ix[column_name]
    list_store[iter][i] = dtype(new_value)
    df_data.loc[int(iter), column_name] = dtype(new_value)
    
cell_renderer.connect('edited', on_edited, column, list_store, df_py_dtypes, surfaces)
surfaces
surfaces
surfaces
surfaces
#cell_renderer.connect('edited', on_edited, column, list_store, df_py_dtypes, surfaces)
surfaces
get_ipython().magic(u'logstart dataframe_editor.py')
get_ipython().magic(u'pwd ')
cell_renderer
