from flask import (flash, redirect)
from flask_login import (login_required, current_user)
from .base import BaseView
from .._common.mixin import FormMixin


class BaseFormView(BaseView, FormMixin):
    success_message = None
    methods = ['GET', 'POST']
    decorators = [login_required]


class CreateView(BaseFormView):

    def dispatch_request(self, **kwargs):
        form = self.get_create_form(**kwargs)

        if form.validate_on_submit():
            model = self.get_model()
            item = model()

            for k, v in form.data.iteritems():
                setattr(item, k, v)

            if model.has_property('user_id'):
                item.user_id = current_user.id

            item.save()
            self.append_context('item', item)

            if self.success_message:
                flash(self.success_message, category='success')

            return redirect(self.get_next_url(**kwargs))

        self.append_context('form', form)
        return self.render(**self.context)


class UpdateView(BaseFormView):

    def dispatch_request(self, **kwargs):

        stmt = self.get_query(**kwargs)
        item = stmt.first_or_404()

        form = self.get_update_form(obj=item, **kwargs)

        if form.validate_on_submit():

            for k, v in form.data.iteritems():
                setattr(item, k, v)

            if item.has_property('user_id'):
                item.user_id = current_user.id

            item.save()
            self.append_context('item', item)

            if self.success_message:
                flash(self.success_message, category='success')

            return redirect(self.get_next_url(**kwargs))

        self.append_context('form', form)
        return self.render(**self.context)