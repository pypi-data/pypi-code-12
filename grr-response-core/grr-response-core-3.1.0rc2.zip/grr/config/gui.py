#!/usr/bin/env python
"""Configuration parameters for the admin UI."""

from grr.lib import config_lib

# The Admin UI web application.
config_lib.DEFINE_integer("AdminUI.port", 8081, "port to listen on")

# Override this if you want to access admin ui extenally. Make sure it is
# secured (i.e. AdminUI.webauth_manager is not NullWebAuthManager)!
config_lib.DEFINE_string("AdminUI.bind", "127.0.0.1",
                         "interface to bind to.")

config_lib.DEFINE_string("AdminUI.document_root",
                         "%(grr/gui/static|resource)",
                         "The main path to the static HTML pages.")

config_lib.DEFINE_string("AdminUI.local_document_root",
                         "%(grr/gui/local/static|resource)",
                         "The main path to the localized static HTML pages.")

config_lib.DEFINE_string("AdminUI.help_root",
                         "%(docs|resource)",
                         "The main path to the static HTML pages.")

config_lib.DEFINE_string(
    "AdminUI.webauth_manager", "NullWebAuthManager",
    "The web auth manager for controlling access to the UI.")

config_lib.DEFINE_bool("AdminUI.django_debug", True,
                       "Turn on to add django debugging")

config_lib.DEFINE_string(
    "AdminUI.django_secret_key", "CHANGE_ME",
    "This is a secret key that should be set in the server "
    "config. It is used in XSRF and session protection.")

config_lib.DEFINE_list(
    "AdminUI.django_allowed_hosts", ["*"],
    "Set the django ALLOWED_HOSTS parameter. "
    "See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts")

config_lib.DEFINE_bool("AdminUI.enable_ssl", False,
                       "Turn on SSL. This needs AdminUI.ssl_cert to be set.")

config_lib.DEFINE_string("AdminUI.ssl_cert_file", "",
                         "The SSL certificate to use.")

config_lib.DEFINE_string(
    "AdminUI.ssl_key_file", None,
    "The SSL key to use. The key may also be part of the cert file, in which "
    "case this can be omitted.")

config_lib.DEFINE_string("AdminUI.url", "http://localhost:8000/",
                         "The direct external URL for the user interface.")

config_lib.DEFINE_bool("AdminUI.use_precompiled_js", False,
                       "If True - use Closure-compiled JS bundle. This flag "
                       "is experimental and is not properly supported yet.")

config_lib.DEFINE_string("AdminUI.export_command",
                         "/usr/bin/grr_export",
                         "Command to show in the fileview for downloading the "
                         "files from the command line.")

config_lib.DEFINE_string("AdminUI.page_title",
                         "GRR Admin Console",
                         "Page title of the Admin UI.")

config_lib.DEFINE_string("AdminUI.heading", "",
                         "Dashboard heading displayed in the Admin UI.")

config_lib.DEFINE_string("AdminUI.report_url",
                         "https://github.com/google/grr/issues",
                         "URL of the 'Report a problem' link.")

config_lib.DEFINE_string("AdminUI.help_url",
                         "/help/index.html",
                         "URL of the 'Help' link.")

config_lib.DEFINE_string("AdminUI.github_docs_location",
                         "https://github.com/google/grr-doc/blob/master",
                         "Base path for GitHub-hosted GRR documentation. ")

config_lib.DEFINE_string("AdminUI.new_hunt_wizard.default_output_plugin",
                         None,
                         "Output plugin that will be added by default in the "
                         "'New Hunt' wizard output plugins selection page.")

config_lib.DEFINE_bool("AdminUI.new_hunt_wizard.use_object_oriented_hunt_rules",
                       default=True,
                       help="If True, the hunt rules configuration UI will put "
                       "the rules into the 'client_rule_set' field of the "
                       "'huntRunnerArgs' variable, instead of using "
                       "'integerRules' and 'regexRules'.")

config_lib.DEFINE_bool("AdminUI.new_hunt_wizard."
                       "use_oo_hunt_rules_in_new_cron_job_wizard",
                       default=True,
                       help="This is the same as "
                       "AdminUI.new_hunt_wizard.use_object_oriented_hunt_rules,"
                       " but regarding the new cron job wizard.")
