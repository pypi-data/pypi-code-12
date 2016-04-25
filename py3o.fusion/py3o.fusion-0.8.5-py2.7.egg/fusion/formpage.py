import traceback
import socket
from py3o.fusion.log import logging

import os
import cgi
import json
import copy

from twisted.web.template import Element, renderer
from twisted.internet.threads import deferToThread
from twisted.web.template import flatten
from twisted.web.server import NOT_DONE_YET
from twisted.web.resource import Resource

from pyjon.utils import get_secure_filename
from py3o.template import Template
from py3o.renderclient import RenderClient
from py3o.formats import Formats
from py3o.types import Py3oTypeConfig
from py3o.types.json import Py3oJSONDecoder

from py3o.fusion.autodestroy import FileAutoDestroy
from py3o.fusion.template import tloader

formats = Formats()
all_formats = formats.get_known_format_names()
# native formats mean formats we don't need to send
# to any renderserver to obtain the final file
native_formats = formats.get_known_format_names(nativeonly=True)
extended_formats = list(set(all_formats).difference(set(native_formats)))


class FormElement(Element):

    cssurls = [
        "/static/bootstrap/css/bootstrap.min.css",
    ]

    loader = tloader('form.xml')
    header_loader = tloader('header.xml')
    scripts_loader = tloader('scripts.xml')

    @renderer
    def csslinks(self, request, tag):
        for cssurl in self.cssurls:
            yield tag.clone().fillSlots(cssurl=cssurl)

    @renderer
    def scripts(self, request, tag):
        return self.scripts_loader.load()

    @renderer
    def header(self, request, tag):
        return self.header_loader.load()

    @renderer
    def title(self, request, tag):
        return tag('py3o.fusion test form')

    @renderer
    def formats(self, request, tag):
        return tag(", ".join(request.allowed_formats))


class FormPage(Resource):

    def __init__(self, render_server, render_port, clientdebug=False):
        Resource.__init__(self)

        self.allowed_formats = copy.copy(native_formats)
        self.render_server = render_server
        self.render_port = render_port
        self.clientdebug = clientdebug

        if render_server:
            # user specified a render server... we'll add extended formats to
            # allowed formats
            self.allowed_formats.extend(extended_formats)

    def flattened(self, output, request):
        # output should be None and ignored because flatten has streamed data
        # to the connection as soon as it could
        request.write('<!-- End of flow -->')
        request.finish()

    def render_GET(self, request):
        request.write('<!DOCTYPE html>\n')
        request.allowed_formats = self.allowed_formats
        d = flatten(request, FormElement(), request.write)
        d.addCallback(self.flattened, request)
        return NOT_DONE_YET

    def render_POST(self, request):
        logging.info("Request received launching thread")

        headers = request.getAllHeaders()
        form = cgi.FieldStorage(
            fp=request.content,
            headers=headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': headers['content-type'],
            }
        )

        if "skipfusion" in form:
            targetformat, error, reasons = self.get_target_format(form, [])
            fname, error, reasons = self.serialize_template(
                form, error, reasons
            )

            res = {
                'request': request,
                'outname': fname,
                'error': error,
                'reasons': reasons,
                'targetformat': targetformat,
                'outmime': formats.get_format(targetformat).mimetype
            }

            d = deferToThread(self.rendertarget, res)
            d.addCallback(self.rendered)
            d.addErrback(self.error)

        else:

            # defer blocking work to a thread and tell client to wait for it
            d = deferToThread(self.fusion, request, form)
            d.addCallback(self.fusionned)
            d.addErrback(self.error)

        request.notifyFinish().addErrback(self._cancelled, d)
        return NOT_DONE_YET

    def _cancelled(self, failure, deferred):
        deferred.cancel()
        logging.info("Client closed connection before end of request")

    def rendertarget(self, res):
        """this is a blocking method called into a thread...
        """
        newres = copy.copy(res)

        if not self.render_port or not self.render_server:
            newres['error'] = True
            newres['reasons'].append(
                "Renderserver missing config '%s:%s'" % (
                    self.render_server, self.render_port
                )
            )

        else:
            client = RenderClient(self.render_server, self.render_port)

            # TODO: when auth is actually implemented on the render server
            # we'll need to implement the command line options...
            client.login('toto', 'plouf')

            newres['outname'] = get_secure_filename()
            targetformat = res.get('targetformat')

            try:
                client.render(
                    res['outname'],
                    newres['outname'],
                    targetformat,
                )
                newres['outmime'] = formats.get_format(targetformat).mimetype

            # TODO: catch all other errors?
            except socket.error, e:
                tb_string = traceback.format_exc()
                newres['error'] = True
                newres['reasons'].append("Renderserver error: %s" % repr(e))
                if self.clientdebug:
                    newres['reasons'].append(
                        "Renderserver traceback: %s" % tb_string
                    )
                print tb_string
                logging.critical("Traceback in thread: %s" % tb_string)

            except Exception, e:
                newres['error'] = True
                newres['reasons'].append("Renderserver error: %s" % repr(e))

            finally:
                # remove intermediate file after rendering
                os.unlink(res['outname'])

        return newres

    def rendered(self, res):
        logging.info(
            "rendering thread finished for target %s" % res['targetformat']
        )

        if res.get('error', False):
            self.reply_error(res)

        else:
            self.reply_success(res)

    def fusionned(self, res):
        """will be called by twisted when thread with ODT processing
        will be finished
        """
        logging.info("fusion thread finished")

        if res.get('error', False):
            self.reply_error(res)

        else:
            if not res.get('targetformat') in native_formats:
                # we need to transform it to the asked format...
                d = deferToThread(self.rendertarget, res)
                d.addCallback(self.rendered)
                d.addErrback(self.error)
                return NOT_DONE_YET

            else:
                # we already have the desired format at hand
                # just return it
                self.reply_success(res)

    def reply_error(self, res):
        request = res.get('request')

        # bad request syntax...
        request.setResponseCode(400)
        # we got an error here... return something different from the ODT
        reasons = res.get('reasons', [])
        logging.info("Errors sent to client --> %s" % reasons)
        request.write(json.dumps({"error": True, "reasons": reasons}))
        request.finish()

    def reply_success(self, res):
        request = res.get('request')

        logging.info("returning autodestroy file resource")

        fileres = FileAutoDestroy(
            res['outname'],
            defaultType=res['outmime'],
        )
        # the FileAutoDestroy is a subclass of t.w.s.File and will
        # automatically call request.finish() for us at the end of
        # the file streaming
        return fileres.render_GET(request)

    def error(self, error):
        """if some client cancels the connection don't fret!
        """
        logging.error(error)

    def get_target_format(self, form, reasons):
        """helper function called by our thread
        """
        error = False
        if 'targetformat' in form and form["targetformat"].value:
            targetformat = form["targetformat"].value
        else:
            # if the user did not give give a target format...
            error = True
            reasons.append("targetformat must be specified")
            targetformat = "None given"

        # here we lower the requested format so that we compare with our
        # known formats which are always lower case. This allows old clients
        # to continue requesting upper case formats without knowing we changed
        if targetformat.lower() not in self.allowed_formats:
            error = True
            reasons.append(
                "target format: '{}' not supported by this server".format(
                    targetformat
                )
            )

        return targetformat, error, reasons

    def get_image_mapping(self, form, error, reasons):
        """helper function called by our thread
        """
        image_mapping = {}
        if "image_mapping" in form and form["image_mapping"].value:
            try:
                image_mapping = json.loads(
                    form["image_mapping"].value
                )
            except ValueError, e:
                error = True
                reasons.append("JSON parse error for image_mapping: %s" % e)

        else:
            error = True
            reasons.append("Image mapping must be given")

        return image_mapping, error, reasons

    def get_datadict(self, form, error, reasons, decoder=None):
        """helper function called by our thread
        """
        # if the user did not give a datadict... we assume it is empty
        datadict = {}
        if 'datadict' in form and form["datadict"].value:
            value = form["datadict"].value
            try:
                if decoder is None:
                    datadict = json.loads(value)
                else:
                    datadict = decoder.decode(value)
            except ValueError, e:
                error = True
                reasons.append("JSON parse error for datadict: %s" % e)

        return datadict, error, reasons

    def serialize_template(self, form, error, reasons):
        """helper function called by our thread
        """
        # grab file from POST into a local secure temp file
        fname = get_secure_filename()
        infile = open(fname, "wb")

        if 'tmpl_file' in form and form["tmpl_file"].value:
            infile.write(form["tmpl_file"].value)

        else:
            # caller did not provide a py3o.template... this is a clear cut
            # case where we must error & abort
            error = True
            reasons.append("No py3o template uploaded")

        infile.close()

        return fname, error, reasons

    def serialize_images(self, t, image_mapping, form, error, reasons):
        tempimages = []

        for imagename, imagevariable in image_mapping.iteritems():
            imname = get_secure_filename()
            infile = open(imname, "wb")
            if imagename in form:
                image_data = form[imagename].value

            else:
                image_data = None

            if not image_data:
                error = True
                reasons.append("Image %s was not uploaded" % imagename)
            else:
                infile.write(form[imagename].value)

            infile.close()
            tempimages.append(imname)

            if not error:
                t.set_image_path(imagevariable, imname)

        return tempimages, error, reasons

    def fusion(self, request, form):
        """WARNING, this method is called inside a thread...
        """
        error = False
        reasons = []

        targetformat, error, reasons = self.get_target_format(form, reasons)
        image_mapping, error, reasons = self.get_image_mapping(
            form, error, reasons
        )

        fname, error, reasons = self.serialize_template(form, error, reasons)
        config = Py3oTypeConfig.from_odf_file(fname)
        decoder = Py3oJSONDecoder(config=config)

        datadict, error, reasons = self.get_datadict(
            form, error, reasons, decoder=decoder
        )

        # then fusion it with our py3o.template call
        outname = get_secure_filename()

        if error:
            os.unlink(fname)
            return {
                'request': request,
                'outname': outname,
                'error': error,
                'reasons': reasons,
                'targetformat': targetformat,
            }

        t = Template(fname, outname)

        tempimages, error, reasons = self.serialize_images(
            t, image_mapping, form, error, reasons
        )

        try:
            t.render(datadict)

        except ValueError, e:
            error = True
            # TODO: the repr is not perfect for image errors
            reasons.append(repr(e))

        except Exception, e:
            # unknow exceptions must be reported to client...
            error = True
            reasons.append(repr(e))

        # remove the input files after rendering
        os.unlink(fname)
        for tmpname in tempimages:
            os.unlink(tmpname)

        # then return the output result
        return {
            'request': request,
            'outname': outname,
            'error': error,
            'reasons': reasons,
            'targetformat': targetformat,
            'outmime': formats.get_format(targetformat).mimetype
        }
