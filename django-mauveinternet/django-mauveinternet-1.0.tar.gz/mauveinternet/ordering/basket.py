from mauveinternet.ordering.order import OrderItemList

def get_basket(request):
    request.session.modified = True # baskets retrieved with get_basket are typically modified
    try:
        return request.session['BASKET']
    except KeyError:
        return new_basket(request)

def get_basket_if_exists(request):
    try:
        basket=request.session['BASKET']
        request.session.modified = True # baskets retrieved with get_basket_if_exists might be modified
        return basket
    except KeyError:
        return None

def add_to_basket(request, item):
    basket=get_basket(request)
    basket.add(item)

def clear_basket(request):
    try:
        del(request.session['BASKET'])
    except KeyError:
        pass

def new_basket(request):
    basket=OrderItemList()
    request.session['BASKET']=basket
    return basket
