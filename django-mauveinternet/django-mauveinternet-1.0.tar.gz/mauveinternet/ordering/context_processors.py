def basket(request):
    variables={}

    if 'BASKET' in request.session:
        basket=request.session['BASKET']
        variables['basket']=request.session['BASKET']

    if 'messages' in request.session:
        variables['messages']=request.session['messages']
        del(request.session['messages'])

    return variables
