# IPython log file

from cairo_helpers.surface import SurfaceManager, AlphaSurfaceManager, np_cairo_view, composite_surface
surface_manager = AlphaSurfaceManager(parent.canvas_slave.surfaces)
np_views = OrderedDict([(name, np_cairo_view(s)) for name, s in surface_manager.surfaces.iteritems()])
np_views['shapes'][:, :, [0, 3]] = 255
surface_manager['shapes'].mark_dirty()
parent.canvas_slave.draw_surface(surface_manager.flatten())
surface_manager.alphas['shapes']
surface_manager.alphas['shapes'] = .5
parent.canvas_slave.draw_surface(surface_manager.flatten())
parent.canvas_slave.draw_surface(surface_manager.flatten())
np_views['background'][:]
np_views['background'][:] = 255
parent.canvas_slave.draw_surface(surface_manager.flatten())
np_views['background'][:] = 255
np_views['connections']
np_views['connections'][:, :, 3] = 255
parent.canvas_slave.draw_surface(surface_manager.flatten())
surface_manager['connections'].mark_dirty()
parent.canvas_slave.draw_surface(surface_manager.flatten())
surface_manager.alphas['connections'] = .5
parent.canvas_slave.draw_surface(surface_manager.flatten())
parent.canvas_slave.draw_surface(surface_manager.flatten())
surface_manager.alphas['connections'] = .1
parent.canvas_slave.draw_surface(surface_manager.flatten())
parent.canvas_slave.draw_surface(surface_manager.flatten())
parent.canvas_slave.draw_surface(surface_manager.flatten())
parent.canvas_slave.draw_surface(surface_manager.flatten(['background']))
parent.canvas_slave.draw_surface(surface_manager.flatten(['background', 'connections']]))
parent.canvas_slave.draw_surface(surface_manager.flatten(['background', 'connections']))
parent.canvas_slave.draw_surface(surface_manager.flatten(['background', 'connections']))
from pygtkhelpers.ui.objectlist import get_tree_store, add_columns
import pandas as pd
pd.DataFrame(surface_manager.surfaces)
pd.DataFrame(surface_manager.surfaces.items())
pd.DataFrame(surface_manager.surfaces.items(), columns=['name', 'surface'])
pd.DataFrame(surface_manager.surfaces.items(), columns=['name', 'surface'])
get_ipython().magic(u'paste')
surfaces = pd.DataFrame(surface_manager.surfaces.items(), columns=['name', 'surface'])
get_tree_store(surfaces)
get_ipython().magic(u'paste')
get_tree_store(surfaces)
get_ipython().magic(u'paste')
get_ipython().magic(u'paste')
get_tree_store(surfaces)
get_ipython().magic(u'paste')
get_tree_store(surfaces)
get_ipython().magic(u'paste')
get_tree_store(surfaces)
get_ipython().magic(u'paste')
get_tree_store(surfaces)
tree_view = gtk.TreeView()
get_ipython().magic(u'pinfo add_columns')
add_columns(tree_view, _50[1], _50[0], column='name')
get_ipython().magic(u'paste')
add_columns(tree_view, _50[1], _50[['name']])
add_columns(tree_view, _50[1], _50['name'])
_50[0]
add_columns(tree_view, _50[1], _50[0][['name']])
tree_view.get_columns()
tree_view.show()
win2 = gtk.Window()
win2.add(tree_view)
win2.show_all()
tree_store = _50[1]
tree_store.get_iter()
tree_view.get_selection()
selection = tree_view.get_selection()
selection.get_selected()
selection.get_selected_rows()
list_store, iter = selection.get_selected()
list_store[iter]
list_store[iter][0]
list_store[iter][1]
list_store, iter = selection.get_selected(); name, surface = list_store[iter]
list_store, iter = selection.get_selected(); name, surface = list_store[iter]; name
list_store, iter = selection.get_selected(); name, surface = list_store[iter]; name, surface
tree_view.get_columns()
tree_view.get_columns()[0]
column = tree_view.get_columns()[0]
column.get_properties()
column.get_cell_renderers()
column.get_cell_renderers()[0]
cell_renderer = column.get_cell_renderers()[0]
#cell_renderer.connect('edited', cell_edited_callback)
import pprint
cell_renderer.connect('edited', lambda *args: pprint(args))
cell_renderer.set_property('editable', True)
def on_edited(*args):
    import pprint
    pprint.pprint(args)
    
cell_renderer.disconnect(220)
cell_renderer.connect('edited', on_edited)
list_store.get_path(0)
list_store.get_path('0')
list_store.get_iter_from_string('0')
list_store[list_store.get_iter_from_string('0')]
list_store['0']
list_store['0'][0]
surfaces = pd.DataFrame(surface_manager.surfaces.items(), columns=['name', 'surface'])
surfaces['alpha'] = [surface_manager.alphas[k] for k in surfaces['name']]
surfaces
py_dtypes, list_store = get_tree_store(surfaces)
win2 = gtk.Window()
tree_view = gtk.TreeView()
#add_columns(tree_view, list_store, py_dtypes[['name', 'alpha']])
py_dtypes
py_dtypes[['name', 'alpha']]
py_dtypes[['name', 'alpha']].reset_index()
py_dtypes.reset_index()
py_dtypes.reset_index().set_index('index')
py_dtypes.reset_index()
py_dtypes.reset_index().reset_index()
py_dtypes.reset_index().reset_index().set_index('index')
def get_py_dtypes(data_frame):
        def get_py_dtype(np_dtype):
                if np_dtype.type == np.object_:
                        return object
                elif hasattr(np_dtype.type(0), 'item'):
                        return type(np_dtype.type(0).item())
                else:
                        return type(np_dtype.type(0))
        
py_dtypes = data_frame.dtypes.map(get_py_dtype)
x')
.rename(columns={'level_0': 'index'}))
get_ipython().magic(u'paste')
get_py_dtypes(surfaces)
get_ipython().magic(u'paste')
get_py_dtypes(surfaces)
py_dtypes = get_py_dtypes(surfaces)
py_dtypes[['name', 'surface']]
py_dtypes
py_dtypes.ix[['name', 'surface']]
py_dtypes.ix[['name', 'alpha']]
get_ipython().magic(u'paste')
surfaces.dtypes.map(get_py_dtype)
surfaces.dtypes.map(get_py_dtype).to_frame()
dtypes = surfaces.dtypes.map(get_py_dtype)
get_ipython().magic(u'pinfo2 dtypes.to_frame')
surfaces.dtypes.map(get_py_dtype).to_frame('dtype')
py_dtypes = surfaces.dtypes.map(get_py_dtype).to_frame('dtype')
py_dtypes.insert(0, 'i', range(len(py_dtypes)))
py_dtypes
py_dtypes.index.name = 'column'
py_dtypes
py_dtypes
get_ipython().magic(u'paste')
add_columns(tree_view, list_store, py_dtypes.ix[['name', 'alpha']])
py_dtypes
surfaces
get_ipython().magic(u'paste')
py_dtypes = get_py_dtypes(surfaces)
get_ipython().magic(u'paste')
py_dtypes = get_py_dtypes(surfaces)
get_ipython().magic(u'paste')
py_dtypes = get_py_dtypes(surfaces)
py_dtypes
get_ipython().magic(u'paste')
py_dtypes
py_dtypes = get_py_dtypes(surfaces)
py_dtypes
add_columns(tree_view, list_store, py_dtypes.ix[['name', 'alpha']])
win2.show_all()
win2.add(tree_view)
win2.show_all()
tree_view.get_columns()
tree_view.get_columns()[-1].get_cell_renderers()
[r.set_property('editable', True) for r in tree_view.get_columns()[-1].get_cell_renderers()]
[r.set_property('editable', True) for r in tree_view.get_columns()[-1].get_cell_renderers()]
column = tree_view.get_columns()[1]
column
column.get_cells()
column.get_cell_renderers()
column.get_cell_renderers()[0]
cell_renderer = column.get_cell_renderers()[0]
cell_renderer.get_property('editable')
[r.set_property('editable', True) for r in tree_view.get_columns()[0].get_cell_renderers()]
adjustment = Gtk.Adjustment(0, 0, 100, 1, 10, 0)
#adjustment = Gtk.Adjustment(0, 0, 100, 1, 10, 0)
get_ipython().magic(u'pinfo gtk.Adjustment')
adjustment = gtk.Adjustment(0, 0, 1, .1, .1, 0)
cell_renderer = column.get_cell_renderers()[0]
cell_renderer
cell_renderer.set_property('adjustment', adjustment)
cell_renderer = column.get_cell_renderers()[0]
adjustment = gtk.Adjustment(1, 0, 1, .1, .1, 0)
cell_renderer.set_property('adjustment', adjustment)
cell_renderer.set_property('digits', 2)
cell_renderer.set_property('adjustment', adjustment)
cell_renderer.set_property('digits', 2)
cell_renderer.set_property('digits', 2)
get_ipython().magic(u'logstart test_tree_view.py')
