import logging
from flask import Blueprint, jsonify, request, abort, g
from .models import *
from .challenge import *
from .authentication import id_required

textpass = Blueprint('textpass', __name__, url_prefix='/textpass')


@textpass.route("/request_challenge", methods=['POST'])
def challenge():
    try:
        phone = request.form['phone']
        u = request_challenge(phone)
    except IndexError, e:
        return jsonify({'error': e.message}), 500
    except ValueError, e:
        logging.error('Bad phone number %s', e)
        return jsonify({'error': e.message}), 400
    except Exception, e:
        logging.error('Problem storing challenge %s', e)
        return jsonify({'error': e.message}), 400
    return jsonify(u.serialize()), 201


@textpass.route("/answer_challenge", methods=['POST'])
def answer_challenge():
    try:
        answer = request.form['answer']
        phone = request.form['phone']
    except KeyError, e:
        logging.error('Missing parameter: %s', e)
        return e, 400
    try:
        token = verify_answer(phone, answer)
    except KeyError as e:
        return jsonify({'error': e}), 400
    except IndexError as e:
        return jsonify({'error': e}), 400
    return jsonify({'token': token})


@textpass.route("/test_resource", methods=['GET', 'POST'])
@id_required
def resource():
    return 'It worked!'
