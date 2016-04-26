import morepath
from webtest import TestApp as Client
from more.forwarded import ForwardedApp
import more.forwarded


def test_forwarded_app():
    morepath.scan(more.forwarded)

    class App(ForwardedApp):
        pass

    @App.path(path='foo')
    class Root(object):
        pass

    @App.view(model=Root)
    def root_default(self, request):
        return request.link(self)

    App.commit()

    c = Client(App())

    response = c.get('/foo',
                     headers={'Forwarded': 'host=www.example.com'})

    assert response.body == b'http://www.example.com/foo'
