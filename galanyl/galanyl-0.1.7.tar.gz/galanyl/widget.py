from __future__ import division

import glob
import h5py
import json

from ipywidgets import \
    Dropdown, \
    IntSlider, \
    HTML, \
    Image as ImageWidget, \
    HBox, \
    VBox

from collections import \
    OrderedDict, \
    defaultdict
import os
import six


def create_image(sim_name, plot_type, file_index, field_type, field_name):
    with h5py.File(sim_to_image_filenames[sim_name]) as image_storage:
        image = image_storage[plot_type][field_type][field_name][
            '%04d' % file_index][:].tostring()
    return image


def type_trait_callback(name, old_value, new_value):
    saved_value = field_dropdown.value
    possible_field_names = field_names_map[sim_control.value][new_value][
        field_type_dropdown.value]
    field_dropdown.options = OrderedDict((
        (override_field_names[k] or k.replace('-', ' ').title(), k)
        for k in possible_field_names))
    if saved_value in possible_field_names:
        field_dropdown.value = saved_value
    else:
        field_dropdown.value = possible_field_names[0]
    image_widget.value = \
        create_image(sim_control.value, new_value,
                     file_control.value, field_type_dropdown.value,
                     field_dropdown.value)


def slider_trait_callback(name, old_value, new_value):
    num_images = num_images_map[sim_control.value][type_control.value][
        field_type_dropdown.value][field_dropdown.value]
    file_control.max = num_images
    try:
        image = create_image(
            sim_control.value, type_control.value, new_value,
            field_type_dropdown.value, field_dropdown.value)
        slider_value = new_value
    except KeyError:
        image = create_image(new_value, type_control.value, num_images - 1,
                             field_type_dropdown.value, field_dropdown.value)
        slider_value = num_images - 1
    image_widget.value = image
    file_time_display.value = '%s Myr' % slider_value


def slider_displayed_callback(widget):
    image_widget.value = create_image(sim_control.value, type_control.value,
                                      widget.value, field_type_dropdown.value,
                                      field_dropdown.value)
    file_time_display.value = '%s Myr' % widget.value


def field_name_trait_callback(name, old_value, new_value):
    image_widget.value = \
        create_image(sim_control.value, type_control.value,
                     file_control.value, field_type_dropdown.value, new_value)


def field_type_trait_callback(name, old_value, new_value):
    saved_value = field_dropdown.value
    possible_field_names = field_names_map[sim_control.value][
        type_control.value][new_value]
    field_dropdown.options = OrderedDict((
        (override_field_names[k] or k.replace('-', ' ').title(), k)
        for k in possible_field_names))
    if saved_value in possible_field_names:
        field_dropdown.value = saved_value
    else:
        field_dropdown.value = possible_field_names[0]
    image_widget.value = \
        create_image(sim_control.value, type_control.value,
                     file_control.value, new_value, field_dropdown.value)


def sim_dropdown_trait_callback(name, old_value, new_value):
    num_images = num_images_map[new_value][type_control.value][
        field_type_dropdown.value][field_dropdown.value]
    try:
        image = create_image(new_value, type_control.value, file_control.value,
                             field_type_dropdown.value, field_dropdown.value)
    except KeyError:
        image = create_image(new_value, type_control.value, num_images - 1,
                             field_type_dropdown.value, field_dropdown.value)
    file_control.max = num_images
    image_widget.value = image

override_field_names = defaultdict(lambda: None)
override_field_names['c-eff'] = 'Effective Sound Speed'

field_type_names = OrderedDict(
    [
        ('gas', six.text_type('Gas')),
        ('star_formation', six.text_type('Star Formation')),
        ('stars', six.text_type('Stars')),
        ('formed_stars', six.text_type('Formed Stars')),
        ('young_stars', six.text_type('Young Stars')),
        ('rot', six.text_type('Rotation')),
    ]
)

fiducial_sim_name = 'feedback_20pc'


def get_image_index():

    image_filenames = glob.glob("data/*feedback*")

    sim_names = [os.path.basename(n)[:-10] for n in image_filenames]

    sim_to_image_filenames = {sn: imf for sn, imf in
                              zip(sim_names, image_filenames)}

    field_names_map = OrderedDict()
    num_images_map = OrderedDict()

    for sim_name in sim_names:
        field_names_map[sim_name] = OrderedDict()
        num_images_map[sim_name] = OrderedDict()
        for plot_type in ['image', 'radial-profile']:
            field_names_map[sim_name][plot_type] = OrderedDict()
            num_images_map[sim_name][plot_type] = OrderedDict()
            with h5py.File(image_filenames[sim_names.index(sim_name)]) as f:
                field_types = list(f[plot_type].keys())

                for field_type in field_types:
                    field_names = sorted(list(f[plot_type][field_type].keys()))

                    field_names_map[sim_name][plot_type][
                        field_type] = field_names
                    num_images_map[sim_name][plot_type][
                        field_type] = OrderedDict()

                    for field_name in field_names:
                        num_images = int(max(
                            f[plot_type][field_type][field_name].keys()))
                        num_images_map[sim_name][plot_type][field_type][
                            field_name] = num_images
    return num_images_map, field_types, sim_to_image_filenames, field_names_map

JSON_FILES = [
    'num_images_map.json',
    'field_types.json',
    'sim_to_image_filenames.json',
    'field_names_map.json',
]

if not all([os.path.exists(jf) for jf in JSON_FILES]):
    (num_images_map, field_types, sim_to_image_filenames,
     field_names_map) = get_image_index()
    with open('num_images_map.json', 'w') as json_file:
        json.dump(num_images_map, json_file)
    with open('field_types.json', 'w') as json_file:
        json.dump(field_types, json_file)
    with open('sim_to_image_filenames.json', 'w') as json_file:
        json.dump(sim_to_image_filenames, json_file)
    with open('field_names_map.json', 'w') as json_file:
        json.dump(field_names_map, json_file)
else:
    with open('num_images_map.json') as json_file:
        num_images_map = json.load(json_file, object_pairs_hook=OrderedDict)
    with open('field_types.json') as json_file:
        field_types = json.load(json_file, object_pairs_hook=OrderedDict)
    with open('sim_to_image_filenames.json') as json_file:
        sim_to_image_filenames = json.load(json_file,
                                           object_pairs_hook=OrderedDict)
    with open('field_names_map.json') as json_file:
        field_names_map = json.load(json_file, object_pairs_hook=OrderedDict)


sim_names = field_names_map.keys()

field_types = OrderedDict(((field_type_names[ft], ft) for ft in field_types))

field_type_dropdown = Dropdown(options=field_types, value='gas')
field_type_dropdown.margin = '8px'

type_control = Dropdown(options=OrderedDict(
    [('Image', 'image'), ('Radial Profile', 'radial-profile')]), value='image')
type_control.margin = '8px'

field_name_mapping = OrderedDict(
    ((override_field_names[fn] or fn.replace('-', ' ').title(), fn) for fn in
     field_names_map[fiducial_sim_name][type_control.value][
         field_type_dropdown.value]))

field_dropdown = Dropdown(options=field_name_mapping,
                          value=('surface-density'))
field_dropdown.margin = '8px'

sim_control = Dropdown(options=list(sim_names), value=fiducial_sim_name)
sim_control.margin = '8px'

top_buttons = HBox(children=[sim_control, type_control, field_type_dropdown, field_dropdown])
top_button_container = HBox(children=[top_buttons])

top_button_container.pack = 'center'
top_button_container.margin = 'auto'

image_widget = ImageWidget()
image_widget.width = '75%'
image_widget.margin = 'auto'

file_control = IntSlider(
    min=0, max=num_images_map[sim_control.value][type_control.value][
        field_type_dropdown.value][field_dropdown.value]-1, readout=False)
file_control.margin = '10px'

file_time_display = HTML(value='')
file_time_display.width = '100px'
file_time_display._dom_classes = ('file_time_display',)
file_time_display._css = (('.file_time_display', 'margin-top', '13px'),)

slider_container = HBox(children=[file_control, file_time_display])
bottom_button_container = HBox(children=[slider_container])

bottom_button_container.pack = 'center'
bottom_button_container.margin = 'auto'

galaxy_widget = VBox(
    children=[top_button_container, image_widget, bottom_button_container])
galaxy_widget.pack = 'center'

file_control.on_trait_change(slider_trait_callback, 'value')
file_control.on_displayed(slider_displayed_callback)

field_dropdown.on_trait_change(field_name_trait_callback, 'value')
field_type_dropdown.on_trait_change(field_type_trait_callback, 'value')

sim_control.on_trait_change(sim_dropdown_trait_callback, 'value')

type_control.on_trait_change(type_trait_callback, 'value')
