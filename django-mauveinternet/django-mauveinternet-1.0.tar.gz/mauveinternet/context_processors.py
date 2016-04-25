def messages(request):
    if 'messages' in request.session:
        msgs = request.session['messages']
        del(request.session['messages'])
        return {'messages': msgs}

    return {}
