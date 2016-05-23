import webapp2
from paste import httpserver
from koalaecommerce.paymentproviders import BACS, Cheque
import config


__author__ = 'Matt Badger'

REGISTRY_KEY = 'sagepay_data'
OFFLINE_REGISTRY_KEY = 'offline_data'


def update_sagepay_data_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    data = {
        'vpsprotocol': request.POST['vpsprotocol'],
        'txtype': request.POST['txtype'],
        'vendor': request.POST['vendor'],
        'crypt': request.POST['crypt'],
        'endpoint': request.POST['endpoint'],
    }
    app.registry[REGISTRY_KEY] = data
    return webapp2.Response().set_status(200, "Successfully saved SagePay data.")


def sagepay_form_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    sagepay_data = app.registry.get(REGISTRY_KEY)
    if not sagepay_data:
        webapp2.Response().set_status(500, "SagePay data not set; post to /update first.")

    vpsprotocol=sagepay_data['vpsprotocol']
    txtype=sagepay_data['txtype']
    vendor=sagepay_data['vendor']
    crypt=sagepay_data['crypt']
    endpoint=sagepay_data['endpoint']

    html_pay_form = u'<form id="form_payment_gateway" action="{endpoint}" method="post"> <input type="hidden" name="VPSProtocol" value="{vpsprotocol}" /> <input type="hidden" name="TxType" value="{txtype}" /> <input type="hidden" name="Vendor" value="{vendor}" /> <input type="hidden" name="Crypt" value="{crypt}" /> <button id="pay" name="pay" class="small" type="submit">Pay</button> </form>'.format(vpsprotocol=vpsprotocol, txtype=txtype, vendor=vendor, crypt=crypt, endpoint=endpoint)
    return webapp2.Response(html_pay_form)


def sagepay_success_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    app.registry['sagepay_response'] = request.query_string
    app.registry['response_handler'] = 'Success'
    return webapp2.redirect(uri='/result')


def sagepay_failure_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    sagepay_response = app.registry['sagepay_response'] = request.query_string
    app.registry['response_handler'] = 'Failure'
    return webapp2.redirect(uri='/result')


def sagepay_result_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    sagepay_response = app.registry.get('sagepay_response')
    status = app.registry.get('response_handler')
    return webapp2.Response(u'response:{}:{}'.format(status, sagepay_response))


def offline_update_data_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    data = {
        'vendor': request.POST['vendor'],
        'encrypted_payload': request.POST['encrypted_payload'],
        'endpoint': request.POST['endpoint'],
    }
    app.registry[OFFLINE_REGISTRY_KEY] = data
    return webapp2.Response().set_status(200, "Successfully saved Offline Payment data.")


def offline_form_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    sagepay_data = app.registry.get(OFFLINE_REGISTRY_KEY)
    if not sagepay_data:
        webapp2.Response().set_status(500, "Offline Payment data not set; post to /update/offline first.")

    vendor=sagepay_data['vendor']
    encrypted_payload=sagepay_data['encrypted_payload']
    endpoint=sagepay_data['endpoint']

    html_pay_form = u'<form id="form_payment_gateway" action="{endpoint}" method="post"> <input type="hidden" name="vendor" value="{vendor}" /> <input type="hidden" name="encrypted_payload" value="{encrypted_payload}" /> <button id="pay" name="pay" class="small" type="submit">Pay</button> </form>'.format(vendor=vendor, encrypted_payload=encrypted_payload, endpoint=endpoint)
    return webapp2.Response(html_pay_form)


def offline_success_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    app.registry['offline_response'] = request.query_string
    app.registry['response_handler'] = 'Success'
    return webapp2.redirect(uri='/result/offline')


def offline_failure_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    app.registry['offline_response'] = request.query_string
    app.registry['response_handler'] = 'Failure'
    return webapp2.redirect(uri='/result/offline')


def offline_result_handler(request, *args, **kwargs):
    app = webapp2.get_app()
    sagepay_response = app.registry.get('offline_response')
    status = app.registry.get('response_handler')
    return webapp2.Response(u'response:{}:{}'.format(status, sagepay_response))


def offline_payment_bacs_handler(request, *args, **kwargs):
    redirect_url = BACS.process(encrypted_payload=request.POST['encrypted_payload'], provider_config={'encryption_key': config.secrets.get('sagepay_vendor_key')})
    return webapp2.redirect(uri=redirect_url, request=request)


def offline_payment_cheque_handler(request, *args, **kwargs):
    redirect_url = BACS.process(encrypted_payload=request.POST['encrypted_payload'], provider_config={'encryption_key': config.secrets.get('sagepay_vendor_key')})
    return webapp2.redirect(uri=redirect_url, request=request)


def main():
    httpserver.serve(webapp2.WSGIApplication([('/payments/sagepay/success/callback', sagepay_success_handler),
                                              ('/payments/sagepay/failure/callback', sagepay_failure_handler),
                                              ('/result', sagepay_result_handler),
                                              ('/update', update_sagepay_data_handler),
                                              ('/pay', sagepay_form_handler),
                                              ('/payments/offline/success/callback', offline_success_handler),
                                              ('/payments/offline/failure/callback', offline_failure_handler),
                                              ('/result/offline', offline_result_handler),
                                              ('/update/offline', offline_update_data_handler),
                                              ('/pay/offline', offline_form_handler),
                                              ('/offlinepayment/bacs', offline_payment_bacs_handler),
                                              ('/offlinepayment/cheque', offline_payment_cheque_handler),
                                              ],
                                             debug=True), host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()
