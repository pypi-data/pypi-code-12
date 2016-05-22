import abc
import falcon

SKIP = 'skip'
TAKE = 'take'


class CreateResource(abc.ABC):  # pragma: no cover

    def on_post(self, req, res):
        self.validation_schema.load(req.context['data'])
        req.context['result'] = self.create_item(data=req.context['data'])
        res.status = falcon.HTTP_CREATED

    @abc.abstractproperty
    def validation_schema(self):
        """
        This should be an instance of Marshmallow schema
        """
        pass

    @abc.abstractmethod
    def create_item(self, data):
        """
        data: validated request body as dict (req.context['data'])

        This method should return a dict for the response body, or None if there is no body.
        You can also raise a falcon exception if any database constraints are violated.
        """
        pass


class ListResource(abc.ABC):  # pragma: no cover

    def on_get(self, req, res):
        skip = req.get_param_as_int(SKIP, min=0)
        skip = skip if skip else 0

        take = req.get_param_as_int(TAKE, min=1, max=100)
        take = take if take else 10

        other_params = {k: v for k, v in req.params.items() if k not in (SKIP, TAKE)}

        req.context['result'] = self.get_items(skip=skip, take=take, **other_params)
        res.status = falcon.HTTP_OK

    @abc.abstractmethod
    def get_items(self, skip, take, **kwargs):
        """
        skip:       number of records to skip for pagination, int > 0
        take:       number of records to take for pagination, int between 1-100
        **kwargs:   all remaining query parameters
        This method should return a dict for the response body
        """
        pass


class ReadResource(abc.ABC):  # pragma: no cover

    def on_get(self, req, res, **kwargs):
        item = self.get_item(**kwargs)
        if item is None:
            raise falcon.HTTPNotFound()
        req.context['result'] = item
        res.status = falcon.HTTP_OK

    @abc.abstractmethod
    def get_item(self, **kwargs):  # pragma: no cover
        """
        This method should return a dict for the response body, or None if no record was found.
        """
        pass


class UpdateResource(abc.ABC):  # pragma: no cover

    def on_put(self, req, res, **kwargs):
        self.validation_schema.load(req.context['data'])
        item = self.update_item(data=req.context['data'], **kwargs)
        if item is None:
            raise falcon.HTTPNotFound()
        req.context['result'] = item
        res.status = falcon.HTTP_OK

    @abc.abstractproperty
    def validation_schema(self):
        """
        This should be an instance of Marshmallow schema
        """
        pass

    @abc.abstractmethod
    def update_item(self, data, **kwargs):  # pragma: no cover
        """
        This method should return a dict for the response body, or None if no record was found.
        """
        pass


class DeleteResource(abc.ABC):  # pragma: no cover

    def on_delete(self, req, res, **kwargs):
        found = self.delete_item(**kwargs)
        if not found:
            raise falcon.HTTPNotFound()
        res.status = falcon.HTTP_NO_CONTENT

    @abc.abstractmethod
    def delete_item(self, **kwargs):  # pragma: no cover
        """
        This method should return a bool, True if found, False if not found
        """
        pass
