from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from .models import Transaction
from .transactions import get_interactive_result


def process_transaction(request, token, param_overrides={}):
    """Process a pxpay transaction using the result retrieved from dps, and
       redirect to the appropriate "success" or "failure" page.

       This view is 100% atomic; repeated requests should just redirect to the
       result page without hitting dps. """

    transaction = get_object_or_404(Transaction, secret=token)

    # Redirecting if the transaction is already processed
    if transaction.status in (Transaction.SUCCESSFUL, Transaction.FAILED):
        return redirect('dps_transaction_result', transaction.secret)

    # Don't process transactions that aren't at the correct stage
    if transaction.status != Transaction.PROCESSING:
        raise Http404

    # grab the dps result
    result_token = request.GET.get("result")
    if not result_token:
        return HttpResponseBadRequest('No result token supplied')
    result = get_interactive_result(result_token, param_overrides)

    # save transaction result in all cases
    transaction.result_dict = result
    transaction.save()

    success = result['Success'] == '1'

    # update transaction status according to success
    status_updated = transaction.complete_transaction(success)
    if not status_updated:
        # shouldn't ever get here, but there's a tiny race condition which
        # means it might, so raise the 404 that would normally happen above
        raise Http404

    if success:
        # if recurring payments are required, save the billing token
        content_object = transaction.content_object
        if content_object.is_recurring():
            content_object.set_billing_token(result["DpsBillingId"] or None)

    # call the callback if it exists
    callback_name = 'transaction_succeeded' if success else \
                    'transaction_failed'
    callback = getattr(transaction.content_object, callback_name, None)
    if callback:
        redirect_url = callback(transaction=transaction, interactive=True,
                                status_updated=status_updated)
    else:
        redirect_url = None

    return redirect(
        redirect_url or
        reverse('dps_transaction_result', args=(transaction.secret, )))


def transaction_result(request, token):
    transaction = get_object_or_404(Transaction, secret=token,
                                    status__in=[Transaction.SUCCESSFUL,
                                                Transaction.FAILED])
    return render_to_response("dps/transaction_result.html", {
        "request": request,
        "transaction": transaction,
        "success": (transaction.status == Transaction.SUCCESSFUL),
    })
