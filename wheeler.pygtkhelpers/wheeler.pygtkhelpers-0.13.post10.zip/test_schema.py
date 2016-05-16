import pygtkhelpers as pg
#def create_form_view(form, values=None, use_markup=True):


if __name__ == '__main__':
    schema = {"type": "object",
              "properties": {"sampling_window_ms": {"type": "integer",
                                                    "default": 5,
                                                    "minimum": 0,
                                                    "index": 0},
                             "delay_between_windows_ms": {"type": "integer",
                                                          "default": 0,
                                                          "minimum": 0},
                             "use_rms": {"type": "boolean", "default": True, "index": 1},
                             "interleave_feedback_samples": {"type": "boolean", "default": True},
                             "string_test": {"type": "string", "default": ""},
                             "serial_port": {"type": "string", "enum": ["COM4", "COM5"],
                                             "default": "COM4"},
                             "baud_rate": {"type": "integer", "default": 115200, "minimum": 0},
                             "auto_atx_power_off": {"type": "boolean", "default": False},
                             "use_force_normalization": {"type": "boolean", "default": False},
                             "c_drop": {"type": "string", "default": "", 'private': True, "index": 2},
                             "c_filler": {"type": "string", "default": "", 'private': True}}}
    schema = {"type": "object",
              "properties": {"string_test": {"type": "string", "default": "test1",
                                             "pattern": "^[0-9]+(-[0-9]+)?(, *[0-9]+(-[0-9]+)?)* *$"}}}

    form_dialog = pg.schema.SchemaDialog(schema)
    form_dialog.run()
