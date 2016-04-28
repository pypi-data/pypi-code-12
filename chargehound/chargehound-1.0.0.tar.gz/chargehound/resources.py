from chargehound.api_requestor import APIRequestor


class Disputes(object):

    """
    Retrieve a dispute
    This method will return a single dispute.

    :param str dispute_id: A dispute id (required)
    :param callback function: The callback function
        to handle the response. (optional)
    :return: Dispute
    """
    @classmethod
    def retrieve(klass, dispute_id, callback=None):
        requestor = APIRequestor()
        return requestor.request('get', 'disputes/{0}'.format(dispute_id),
                                 callback=callback)

    """
    A list of disputes
    This method will list all the disputes that we have synced from Stripe.
    By default the disputes will be ordered by `created`
    with the most recent dispute first.
    `has_more` will be `true` if more results are available.

    :param int limit: Maximum number of disputes to return.
        Default is 20, maximum is 100. (optional)
    :param str starting_after: A dispute id.
        Fetch disputes created after this dispute. (optional)
    :param str ending_before: A dispute id.
        Fetch disputes created before this dispute. (optional)
    :param callback function: The callback function
        to handle the response. (optional)
    :return: Disputes
    """
    @classmethod
    def list(klass, **kwargs):
        callback = kwargs.pop('callback', None)
        list_params = kwargs

        requestor = APIRequestor()
        return requestor.request('get', 'disputes',
                                 params=list_params,
                                 callback=callback)

    """
    Submitting a dispute
    You will want to submit the dispute through Chargehound after you recieve
    a notification from Stripe of a new dispute.
    With one `POST` request you can update a dispute with the
    evidence fields and send the generated response to Stripe.
    The response will have a `201` status if the submit was successful.
    The dispute will also be in the submitted state.

    :param str dispute_id: A dispute id (required)
    :param str template: Set the template for this dispute. (optional)
    :param object fields:
        Key value pairs to hydrate the template's evidence fields. (optional)
    :param str customer_name: Update the customer name.
        Will also update the customer name in the evidence fields. (optional)
    :param str customer_email:
        Update the customer email. Will also update the customer email
        in the evidence fields. Must be a valid email address. (optional)
    :param callback function: The callback function
        to handle the response. (optional)
    :return: Dispute
    """
    @classmethod
    def submit(klass, dispute_id, **kwargs):
        callback = kwargs.pop('callback', None)
        update = kwargs

        requestor = APIRequestor()
        return requestor.request('post',
                                 'disputes/{0}/submit'.format(dispute_id),
                                 data=update,
                                 callback=callback)

    """
    Updating a dispute
    You can update the template and the fields on a dispute.

    :param str dispute_id: A dispute id (required)
    :param str template: Set the template for this dispute. (optional)
    :param object fields:
        Key value pairs to hydrate the template's evidence fields. (optional)
    :param str customer_name: Update the customer name.
        Will also update the customer name in the evidence fields. (optional)
    :param str customer_email:
        Update the customer email. Will also update the customer email
        in the evidence fields. Must be a valid email address. (optional)
    :param callback function: The callback function
        to handle the response. (optional)
    :return: Dispute
    """
    @classmethod
    def update(klass, dispute_id, **kwargs):
        callback = kwargs.pop('callback', None)
        update = kwargs

        requestor = APIRequestor()
        return requestor.request('post', 'disputes/{0}'.format(dispute_id),
                                 data=update,
                                 callback=callback)
