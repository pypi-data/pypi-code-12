from __future__ import print_function

import csv as csv_module
import datetime
import traceback
from crispy_forms.helper import FormHelper

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, InvalidPage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext, Context
from django.utils.datastructures import SortedDict
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist
from django.template import Template
from django.core.urlresolvers import reverse, NoReverseMatch

from six.moves import cStringIO
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from .models import QueryReport
from timelib import strtodatetime


@staff_member_required
def report_index(request, template_name="query_reports/index.html"):

    reports = QueryReport.objects.all()

    return render_to_response(template_name,
        locals(), context_instance=RequestContext(request))


class ShowReportView(DetailView):
    template_name = "query_reports/show.html"
    model = QueryReport

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShowReportView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self, fields):
        return type('ReportVarForm', (forms.BaseForm,), {'base_fields': fields})

    def get_form(self, form_class, initial):
        if "SUBMIT" in self.request.GET:
            form = form_class(self.request.GET, initial=initial)
        else:
            form = form_class(initial=initial)

        helper = FormHelper()
        helper.form_tag = False
        helper.label_class = "col-xs-4"
        helper.field_class = "col-xs-8"
        helper.add_layout(helper.build_default_layout(form))

        form.helper = helper

        return form

    def get(self, request, slug=None):

        self.object = self.get_object()
        csv = request.REQUEST.get("csv")
        error = None
        query = None
        page = None
        headers = None
        dataset = None
        alignment = None
        data = None
        fks = None

        fields, initial, has_required = self.get_fields()
        self.form = self.get_form(self.get_form_class(fields), initial)

        try:

            params = {}
            if self.form.is_bound:
                if self.form.is_valid():
                    params = self.form.cleaned_data
            else:
                params = initial

            if has_required and not self.form.is_valid():
                dataset = ([], [], [])
            else:
                for variable in self.object.variables.all():
                    if variable.type == "date":

                        date_str = params[variable.name]
                        if isinstance(date_str, datetime.date):
                            if getattr(date_str, "date", None):
                                date_str = date_str.date()
                        else:
                            date_str = strtodatetime(date_str or "").date()
                        params[variable.name] = date_str
                dataset = self.object.build_queryset(params, link_fks=not csv)

            headers, dataset, fks = dataset

            try:
                from django.db import connections
                query = connections['default'].queries[-1]["sql"]
            except:
                pass

            if not csv:
                paginator = Paginator(dataset, params.get("rows_per_page", 100))
                try:
                    page = paginator.page(request.GET.get("page", 1))
                except InvalidPage:
                    page = paginator.page(1)

                object_list = page.object_list
            else:
                object_list = dataset

            # format table
            data = []
            formats = [None] * len(headers)
            alignment = ["left"] * len(headers)

            for format in self.object.columns.exclude(format=""):
                formats[headers.index(format.name)] = format.format

            for align in self.object.columns.exclude(alignment="left"):
                alignment[headers.index(align.name)] = align.alignment

            # build table
            for row in object_list:
                items = []
                for idx, item in enumerate(row):
                    if not csv and fks[idx]:

                        # customizable object format
                        format = "{{ object }}"
                        if formats[idx]:
                            format = formats[idx]

                        try:
                            obj = fks[idx].objects.get(pk=item)
                            item = Template(format).render(Context(dict(object=obj)))

                            # link to the admin
                            try:
                                url = reverse("admin:%s_%s_change" % (
                                        obj._meta.app_label,
                                        obj._meta.object_name.lower()), args=[obj.id])
                                if url:
                                    item = "<a href='%s'>%s</a>" % (url, item)
                            except NoReverseMatch:
                                pass
                        except ObjectDoesNotExist:
                            pass

                    elif formats[idx]:
                        try:
                            if isinstance(item, datetime.date):
                                item = item.strftime(formats[idx])
                            else:
                                try:
                                    item = formats[idx] % item
                                except:
                                    item = formats[idx] % {"value": item}
                        except:
                            pass
                    item = mark_safe(u"%s" % item)
                    items.append(item)
                data.append(items)

            # gather totals
            rollup_columns = self.object.columns.filter(rollup=True)
            totals = [""] * len(headers)
            for rollup in rollup_columns:
                totals[headers.index(rollup.name)] = 0
            if rollup_columns.count() > 0:
                for row in object_list:
                    for rollup in rollup_columns:
                        idx = headers.index(rollup.name)
                        totals[idx] += row[idx]

            # format totals
            for rollup in rollup_columns:
                idx = headers.index(rollup.name)
                if formats[idx]:
                    totals[idx] = formats[idx] % totals[idx]

            if csv:
                string = cStringIO()
                file = csv_module.writer(string)
                file.writerow(headers)
                file.writerows([[unicode(item).encode("ascii", "ignore") for item in row] for row in data])
                file.writerow(totals)

                response = HttpResponse(string.getvalue(), content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename="%s.csv"' % self.object.name

                return response

        except Exception as ex:
            error = traceback.format_exc()

        return self.render_to_response(self.get_context_data(
            error=error,
            headers=headers,
            dataset=dataset,
            alignment=alignment,
            data=data,
            query=query,
            fks=fks,
            page=page,
        ))

    def get_fields(self):

        # create form from variables
        fields = SortedDict()
        fields["rows_per_page"] = forms.IntegerField(label="Rows per page")
        fields["csv"] = forms.BooleanField(
            required=False, label="Download all rows in a CSV file")

        initial = {
            "rows_per_page": 25,
            "csv": False
        }

        # build the form
        has_required = False
        for variable in self.object.variables.all():

            if variable.required:
                modifiers = {"required": True}

                # notify if the form must be filled
                if not variable.initial:
                    has_required = True
            else:
                modifiers = {"required": False}

            field_class = {
                'value':forms.CharField,
                'date': forms.DateField
            }[variable.type]

            if variable.type == "date":
                modifiers['widget'] = forms.TextInput(attrs={"class": "datefield"})

            # fill out the initial data
            if variable.initial:

                if variable.initial.startswith("@now"):
                    now = datetime.datetime.now()
                    if ":" in variable.initial:
                        tag = variable.initial.split(":")[1]
                        if tag == "first":
                            now = datetime.datetime(now.year, now.month, 1)
                        elif tag == "nextfirst":
                            month = (now.month + 1) % 13
                            year = now.year + int(month == 1)
                            now = datetime.datetime(year, month, 1)

                    initial[variable.name] = now
                else:
                    initial[variable.name] = variable.initial

            fields[variable.name] = field_class(**modifiers)

        return fields, initial, has_required

    def get_context_data(self, **kwargs):
        return super(ShowReportView, self).get_context_data(
            report=self.object,
            form=self.form,
            reports=QueryReport.objects.all(),
            **kwargs
        )

