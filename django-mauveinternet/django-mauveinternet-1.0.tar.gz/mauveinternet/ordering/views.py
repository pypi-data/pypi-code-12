from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required, permission_required

from mauveinternet.shortcuts import template

from mauveinternet.ordering.models import get_order_model, OrderStatusChange
from mauveinternet.ordering.forms import *
from mauveinternet.ordering.card import *
from mauveinternet.ordering.lockbox import *
from mauveinternet.ordering.basket import get_basket, clear_basket, get_basket_if_exists

def basket(request):
    if request.method == 'POST':
        basket=get_basket(request)
        for item in basket:
            if hasattr(item, 'set_quantity'):
                try:
                    qty=int(request.POST.get('%d__qty'%item.list_id, 1))
                except ValueError:
                    qty=1

                item.set_quantity(qty)

            # this strange-looking test is to deal with Internet Explorer's handling of image buttons
            if 'remove-item-%d.x'%item.list_id in request.POST:
                item_id=int(request.POST.get('remove_item', 0))
                item=basket.remove_item(item.list_id)

                if basket.is_empty():
                    clear_basket(request)

                request.user.write_message(u'%s removed from basket.'%item.name)

        if 'next' in request.POST:
            return HttpResponseRedirect(request.POST['next'])

    return template(request, 'view_basket.html')


def view_basket_item(request):
    if 'item' not in request.GET:
        return HttpResponseRedirect('/basket/')

    basket=get_basket_if_exists(request)
    if basket is None:
        return HttpResponseRedirect('/')

    try:
        item=basket.get_item(int(request.GET['item']))
    except ValueError:
        return HttpResponseRedirect('/basket/')

    if not hasattr(item, 'item_view'):
        raise Http404()

    return item.item_view(request)


@login_required
def checkout(request):
    basket=get_basket_if_exists(request)
    if not basket or basket.is_empty():
        return template(request, 'error_basket_empty.html')

    if request.method == 'POST':
        form=CheckoutForm(request.POST)
        if form.is_valid():
            order=form.save(commit=False)
            order.customer = request.user
            order.items = basket

            order.subtotal=basket.get_subtotal()
            order.total=basket.get_total()
            if hasattr(basket, 'vat_number'):
                order.vat_number = basket.vat_number

            card = Card(
                    pan=form.cleaned_data['card_number'],
                    name_on_card=form.cleaned_data['name_on_card'],
                    card_type=form.cleaned_data['card_type'],
                    expiry_date=form.cleaned_data['card_expiry_date'],
                    start_date=form.cleaned_data['card_start_date'],
                    issue_number=form.cleaned_data['card_issue_number'],
                    cv2=form.cleaned_data['card_cv2_number'],
                    billing_address=form.cleaned_data['billing_address'],
                    billing_postcode=form.cleaned_data['billing_postcode'],
            )

            key, data = symmetric_encrypt(card)

            request.session['order'] = order
            request.session['card_key'] = key

            # we provide card to the template but it shouldn't be used to display anything too sensitive
            return template(request, 'ordering/confirm_order.html', order=order, card=card, order_data=data)
    else:
        form=CheckoutForm()

    return template(request, 'checkout.html', form=form)


@login_required
def place_order(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    if 'order' not in request.POST:
        return template(request, 'order_expired.html')

    order = request.session['order']
    key = request.session['card_key']
    card = symmetric_decrypt(key, request.POST['order_data'])

    # prevent resubmitted orders
    clear_basket(request)
    del(request.session['order'])
    del(request.session['card_key'])

    # save order
    order.save()
    order.orderstatuschange_set.create(previous_status='-', message=u'Order placed by customer')

    # attempt to take payment
    payment_module = __import__(settings.PAYMENT_MODULE, {}, {}, ['confirm_payment'])

    return payment_module.confirm_payment(request, order, card)


@permission_required('ordering.can_view_orders')
def orders_new(request):
    Order = get_order_model()
    return template(request, 'ordering/orders.html', filter='New', orders=Order.objects.new())


@permission_required('ordering.can_view_orders')
def orders_all(request):
    Order = get_order_model()
    return template(request, 'ordering/orders.html', filter='All', orders=Order.objects.all())


@permission_required('ordering.can_view_orders')
def view_order(request, code):
    Order = get_order_model()
    try:
        order = Order.objects.for_order_number(code)
    except Order.DoesNotExist:
        raise Http404()

    if request.method == 'POST' and 'order_status' in request.POST:
        statusform = OrderStatusForm(request.POST, instance=order)
        if statusform.is_valid():
            order.set_status(statusform.cleaned_data['order_status'], statusform.cleaned_data['message'])
            if statusform.cleaned_data['order_status'] == 'P':
                order.items.fulfil()
                order.set_status('C', u'Order fulfilled by system.')
            return HttpResponseRedirect('/admin/orders/%s/'%order.order_number())
    else:
        statusform = OrderStatusForm(initial={'order_status': order.status})

    return template(request, 'ordering/view_order.html', order=order, statusform=statusform)


@permission_required('ordering.can_view_orders')
def view_order_item(request, code):
    code=int(code)-settings.ORDER_NUMBER_BASE
    order=get_object_or_404(get_order_model(), id=code)

    try:
        item=order.items.get_item(int(request.GET['item']))
    except (ValueError, KeyError):
        return HttpResponseRedirect('/admin/orders/%s/'%order.order_number())

    if not hasattr(item, 'item_view'):
        return HttpResponseRedirect('/admin/orders/%s/'%order.order_number())

    return item.item_view(request, order)


def alternate_payment(request):
    """Displays a confirmation page for the order; if placed, redirect to information about how to pay
    by alternate methods."""

    basket=get_basket_if_exists(request)
    if not basket or basket.is_empty():
        return template(request, 'error_basket_empty.html')

    if request.method == 'POST':
        form = AlternatePaymentForm(request.POST)
        if form.is_valid():
            order=form.save(commit=False)
            order.customer = request.user
            order.items = basket

            order.subtotal=basket.get_subtotal()
            order.total=basket.get_total()
            if hasattr(basket, 'vat_number'):
                order.vat_number = basket.vat_number

            order.save()
            return HttpResponseRedirect('/alternate-payment-complete')
    else:
        form = AlternatePaymentForm()

    return template(request, 'alternate_payment.html', form=form, basket=basket)
