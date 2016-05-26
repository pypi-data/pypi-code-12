
"""
Contact Page
"""
from flask_magic import (Magic, set_meta, get_config, flash, abort,
                         register_package, redirect, request, url_for)
from flask_magic.decorators import (menu, template, route)
from flask_magic.ext import (mail, recaptcha)
import flask_magic.utils as utils
import logging

register_package(__package__)

def contact_page(view, **kwargs):
    """
    :param view: The view to copy to
    :param kwargs:
        - fa_icon
        - menu: The name of the menu
        - show_menu: bool - show/hide menu
        - menu_order: int - position of the menu
        - return_to
        - email_to
    :return:
    """
    endpoint_namespace = view.__name__ + ":%s"
    endpoint = endpoint_namespace % "ContactPage"

    template_dir = kwargs.pop("template_dir", "Magic/Plugin/ContactPage")
    template_page = template_dir + "/%s.html"

    return_to = kwargs.pop("return_to", endpoint)
    _menu = kwargs.get("menu", {})
    _menu.setdefault("title", "Contact")
    _menu.setdefault("extends", view)
    _menu.setdefault("visible", True)
    _menu.setdefault("order", 100)
    _menu.setdefault("")

    class ContactPage(object):

        @menu(endpoint=endpoint, **_menu)
        @template(template_page % "contact_page",
                  endpoint_namespace=endpoint_namespace)
        @route("contact", methods=["GET", "POST"], endpoint=endpoint)
        def contact_page(self):

            # Email to
            email_to = kwargs.pop("email_to", get_config("APPLICATION_CONTACT_EMAIL", None))

            if not mail.validated:

                abort("MailmanConfigurationError")
            elif not email_to:
                abort("ContactPageMissingEmailToError")

            if request.method == "POST":
                email = request.form.get("email")
                subject = request.form.get("subject")
                message = request.form.get("message")
                name = request.form.get("name")

                flash_message = "Message sent. Thank you!"
                flash_type = "success"

                if recaptcha.verify():

                    if not email or not subject or not message:
                        flash_message = "All fields are required"
                        flash_type = "error"
                    elif not utils.is_email_valid(email):
                        flash_message = "Invalid email address"
                        flash_type = "error"
                    else:
                        try:
                            mail.send(to=email_to,
                                      reply_to=email,
                                      mail_from=email,
                                      mail_subject=subject,
                                      mail_message=message,
                                      mail_name=name,
                                      template="contact-us.txt")
                        except Exception as ex:
                            logging.exception(ex)
                            abort("MailmanConfigurationError")
                else:
                    flash_message = "Security code is invalid"
                    flash_type = "error"

                flash(flash_message, flash_type)

                return redirect(url_for(return_to))

            set_meta(title="Contact Us")

            return None

    return ContactPage


