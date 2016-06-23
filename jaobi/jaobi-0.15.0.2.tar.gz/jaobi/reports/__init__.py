# -*- coding: utf-8 -*-

# The reports api
from tornado import gen
from jaobi.reports.reduced import (SiteConsumers, SiteConsumption,
                                   ThemeConsumers, ThemeConsumption,
                                   ContentConsumptionReport,
                                   ContentConsumersReport,
                                   ReferrerConsumption)


@gen.coroutine
def site_consumers(**kwargs):
    """Returns consolidated report about consumers on sites.

    :param kwargs: kwargs to SiteConsumers.get_sites_report."""

    r = yield SiteConsumers.get_sites_report(**kwargs)
    return r


@gen.coroutine
def site_consumers_history(**kwargs):
    """Returns history report about consumers on sites.

    :param kwargs: kwargs to SiteConsumers.get_sites_report_history.."""

    r = yield SiteConsumers.get_sites_report_history(**kwargs)
    return r


@gen.coroutine
def site_consumption(**kwargs):
    """Returns consolidated report about consumption on sites.

    :param kwargs: kwargs to SiteConsumption.get_sites_report."""

    r = yield SiteConsumption.get_sites_report(**kwargs)
    return r


@gen.coroutine
def site_consumption_history(**kwargs):
    """Returns history report about consumption on sites.

    :param kwargs: kwargs to SiteConsumption.get_sites_report_history."""

    r = yield SiteConsumption.get_sites_report_history(**kwargs)
    return r


@gen.coroutine
def theme_consumers(**kwargs):
    """Returns consolidated report about consumers on themes.

    :param kwargs: kwargs to ThemeConsumers.get_themes_report."""

    r = yield ThemeConsumers.get_themes_report(**kwargs)
    return r


@gen.coroutine
def theme_consumers_history(**kwargs):
    """Returns history report about consumers on themes.

    :param kwargs: kwargs to ThemeConsumers.get_themes_report_history."""

    r = yield ThemeConsumers.get_themes_report_history(**kwargs)
    return r


@gen.coroutine
def theme_consumption(**kwargs):
    """Returns consolidated report about consumers on themes.

    :param kwargs: kwargs to ThemeConsumption.get_themes_report."""

    r = yield ThemeConsumption.get_themes_report(**kwargs)
    return r


@gen.coroutine
def theme_consumption_history(**kwargs):
    """Returns history report about consumers on themes.

    :param kwargs: kwargs to ThemeConsumption.get_themes_report_history."""

    r = yield ThemeConsumption.get_themes_report_history(**kwargs)
    return r


@gen.coroutine
def content_consumers(**kwargs):
    """Returns consolidated report about consumers on content.

    :param kwargs: kwargs to ContentConsumersReport.get_content_report."""

    r = yield ContentConsumersReport.get_content_report(**kwargs)
    return r


@gen.coroutine
def content_consumption(**kwargs):
    """Returns consolidated report about consumption on content.

    :param kwargs: kwargs to ContentConsumptionReport.get_content_report.
    """

    r = yield ContentConsumptionReport.get_content_report(**kwargs)
    return r


@gen.coroutine
def referrer_consumption(**kwargs):
    """Returns consolidated report about consumption originated from referrer.

    :param kwargs: kwargs to ReferrerConsumption.get_referrer_report."""

    r = yield ReferrerConsumption.get_referrer_report(**kwargs)
    return r
