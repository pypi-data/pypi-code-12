"""
Here we define the yaml specification for komodo options

The specifications are responsible for sanitation, validation and normalisation.
"""
from input_algorithms.errors import BadSpecValue
from input_algorithms.meta import Meta
from input_algorithms.validators import regexed
from input_algorithms.spec_base import valid_string_spec, required, dictionary_spec
from input_algorithms.spec_base import string_spec as String, listof as List, dictof as Dict
from input_algorithms.dictobj import dictobj
from importlib import import_module

from komodo.formatter import MergedOptionStringFormatter

from komodo.core_modules.base import CheckBase
from komodo.widgets.base import Widget
from komodo.plugins.base import PluginBase


class Import(valid_string_spec):
    validators = [regexed("^(?P<module>[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*):(?P<class>[a-zA-Z_][a-zA-Z_0-9]*)$")]
    def setup(self, checked_class):
        self.checked_class = checked_class

    def normalise_filled(self, meta, val):
        # Run string & regex validator
        val = super(Import, self).normalise_filled(meta, val)

        # Now validate it is importable
        path = self.validators[0].regexes[0][1].match(val).groupdict()
        try:
            module = import_module(path['module'])
            val = getattr(module, path['class'])
            if not issubclass(val, self.checked_class):
                raise BadSpecValue(
                    "Wrong class type. {} is not a {}".format(
                          val.__name__
                        , self.checked_class.__name__
                    ),
                    meta=meta
                )
            return val
        except ImportError:
            raise BadSpecValue("Import not found", val=val, meta=meta)
        except AttributeError:
            raise BadSpecValue("Couldnt find class", val=val, meta=meta)

class ClassList(List):
    def normalise_filled(self, meta, val):
        # Do list_of stuff
        val = super(ClassList, self).normalise_filled(meta, val)

        # Now convert it to a dict of {kls.__name__: kls}
        return {kls.__name__: kls for kls in val}


class Slug(valid_string_spec):
    validators = [regexed('^[a-z][-a-z0-9]*$')]


class DashboardWidget(dictobj.Spec):
    type = dictobj.Field(
        String
    )

    data = dictobj.Field(
        String
    )

    options = dictobj.Field(
        dictionary_spec
    )

    def validate(self, installed_widgets, meta):
        if not self.type in installed_widgets:
            raise BadSpecValue("Widget '{}' not installed".format(self.type), meta=meta)



class Dashboard(dictobj.Spec):
    description = dictobj.Field(
          String
        , default = "{_key_name_1}"
        , formatted = True
        , help = "Description to show up in the index"
        )

    widgets = dictobj.Field(
          List(DashboardWidget.FieldSpec())
        , wrapper = required
        , help = "List of widgets to place in the dashboard"
        )


class Check(dictobj.Spec):
    import_path = dictobj.Field(
          Import(CheckBase)
        , formatted = True
        , wrapper = required
        , help = "Import path of the check class"
        )

    options = dictobj.Field(
          dictionary_spec
        , help = "Options to pass into the constructor"
        )

class Plugin(dictobj.Spec):
    import_path = dictobj.Field(
          Import(PluginBase)
        , formatted = True
        , wrapper = required
        , help = "Import path of the Plugin class"
        )

    options = dictobj.Field(
          dictionary_spec
        , help = "Options to pass into the constructor"
        )


class ConfigRoot(dictobj.Spec):
    dashboards = dictobj.Field(
        Dict(Slug(), Dashboard.FieldSpec(formatter=MergedOptionStringFormatter))
        , wrapper = required
    )

    checks = dictobj.Field(
        Dict(String(), Check.FieldSpec(formatter=MergedOptionStringFormatter))
        , wrapper = required
    )

    installed_widgets = dictobj.Field(
        ClassList(Import(Widget))
        , wrapper = required
    )

    plugins = dictobj.Field(
        List(Plugin.FieldSpec(formatter=MergedOptionStringFormatter))
    )

    def validate_widgets(self):
        for name, dashboard in self.dashboards.iteritems():
            for widget in dashboard['widgets']:
                widget.validate(self.installed_widgets, Meta(None, path=['dashboards', name, ]))