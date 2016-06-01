from django import template

from zebra.conf import options

register = template.Library()


def _set_up_zebra_form(context):
    if not "zebra_form" in context:
        if "form" in context:
            context["zebra_form"] = context["form"]
        else:
            raise KeyError("Missing stripe form.")
    context["STRIPE_PUBLISHABLE"] = options.STRIPE_PUBLISHABLE
    return context


@register.inclusion_tag('zebra/_stripe_js_and_set_stripe_key.html', takes_context=True)
def zebra_head_and_stripe_key(context):
    return _set_up_zebra_form(context)


@register.inclusion_tag('zebra/_basic_card_form.html', takes_context=True)
def zebra_card_form(context):
    return _set_up_zebra_form(context)
