import fields
import GenSettingDict
from django.db import models
from django.utils.translation import ugettext_lazy as _
from . import DEFAULTSETTINGS
from GenSettingDict import overlaysettings

'''
    in the project settings.py defaultsettings can be set
    DEFAULTSETTINGS.addsetting("user.notifications.sound", None, description="sound file")
    DEFAULTSETTINGS.addsetting("user.dashboard.msg_count", 5, description="message count")
    DEFAULTSETTINGS.addsetting("user.dashboard.task_count", 5, description="task count")
    ...

'''


#add new variable to the models
models.options.DEFAULT_NAMES += ('settings_predecessor_field', )


#as migrations dont support lambdas, replace with this function
def newSettingDict():
    return GenSettingDict.GenSettingDict


class SettingsMixin(models.Model):

    settings = fields.SettingsField(db_index=False, verbose_name=_('Settings'), editable=True, blank=True, default=newSettingDict)

    def getsetting(self, settingsnamestring, fallbackvalue=None):
        """
        returns the value of the given settingsname, fallbackvalue if setting not exists
        """

        overlayedsettings = self.getOverlayedSettings()
        value = overlayedsettings.getsetting(settingsnamestring)
        if not value:
            return fallbackvalue
        return value

    def getOverlayedSettings(self):
        """
        returns a settings dict with overlayed settings
        """

        if hasattr(self._meta, 'settings_predecessor_field'):
            try:
                spf = getattr(self, self._meta.settings_predecessor_field)
                x2 = spf.getOverlayedSettings()
                return overlaysettings(x2, self.settings)
            except AttributeError:
                    return None
        else:
            x = GenSettingDict.GenSettingDict()
            if DEFAULTSETTINGS:
                x = overlaysettings(x, DEFAULTSETTINGS)
            return overlaysettings(x, self.settings)

    def setsetting(self, settingsnamestring, value):
        """
        stores the value of the given settingsname, overwrite an existing value
        """
        # get the current settings, overlay them with the new setting and save them
        #pdb.set_trace()
        self.settings.setsetting(settingsnamestring, value)

    class Meta:
        abstract = True       #with this, inherance is in such way, that settings will be added to all other models in the same table
        settings_predecessor_field = None # if set, the predecessor settings will be overlayed with the settings of this class