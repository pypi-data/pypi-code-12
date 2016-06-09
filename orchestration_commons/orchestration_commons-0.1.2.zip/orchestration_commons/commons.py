import requests


def get_users_data(ids, endpoint_url, profiles=True):
    """
    From a list of user_ids, extracts the profile and entity data for each of them.
    :param ids: List of ids
    :param endpoint_url: URL used to fetch data.
    :param profiles: True if the ids are profiles ids. False if they are entities ids.
    :return: dict where the values will have the structure {'profile': {...}, 'entity': {...}} and the
    keys will be the profiles ids if profile=True, and {'profiles': [{...}, ...], 'entity': {...}} and the keys will
    be the entities ids if profile=False
    """
    assert isinstance(ids, list) and all(isinstance(user_id, str) for user_id in ids), \
        "Input must be of type list(str)."

    # First, we ask for the profiles.
    ids = list(set(ids))  # We remove any duplicates
    r = requests.get(endpoint_url, params={'id': ids})

    if r.status_code == 200:
        results_data = r.json()['data']
        results_retrieved = len(results_data)
        number_of_expected_results = len(ids)

        if results_retrieved != number_of_expected_results:
            raise Exception("Expected %d results corresponding to %d input ids, but only received %d "
                            "results instead." % (number_of_expected_results, number_of_expected_results, results_retrieved))

        try:
            if profiles:
                results = {}

                for p in results_data:
                    entity = p['entity']
                    del p['entity']
                    profile = p
                    results[profile['_id']] = {'entity': entity, 'profile': profile}

                return results
            else:
                results = {}

                for e in results_data:
                    profiles = e['profiles']
                    del e['profiles']
                    entity = e
                    results[entity['_id']] = {'entity': entity, 'profiles': profiles}

                return results
        except Exception as e:
            message = """"
            An Exception happened trying to obtain the data for the following ids: %s

             Possible causes:
             - Bad endpoint: The endpoint provided is %s.
             - Trying to parse /profiles?ids=... response when profiles=False.
             - Trying to parse /entities?ids=...&profiles=true when profiles=True

             These are the input parameters:
             - ids: %s
             - endpoint_url: %s
             - profiles: %s

             Exception message:
                %s
            """ % (str(ids), endpoint_url, str(ids), endpoint_url, str(profiles), e)
            raise Exception(message)

    else:
        raise Exception('Server responded with status %d and message %s' % (r.status_code, r.json()['message']))


def perform_calculations(auction, calculations_url):
    """
    Performs calculations on an auction object.
    :param auction: Object to be decorated with calculations.
    :param calculations_url: URL used to ask for the calculations.
    """
    try:
        r = requests.post(calculations_url, json=auction)

        if r.status_code == 200:
                return r.json()['data']['auction']
        else:
            raise Exception("Server responded with status %d" % r.status_code)
    except Exception as e:
        message = """
             A problem occurred trying to calculate the auction.

             Possible causes:
             - Wrong structure of the auction.
             - Bad endpoint.

             Input parameters:
             - Auction: %s
             - Endpoint: %s

             Exception message:
             %s
            """ % (str(auction), calculations_url, e)
        raise Exception(message)

if __name__ == '__main__':

    auction = {
    "payerId": 2,
    "operativeChargesSeller": 10000,
    "invoices": [{
        "withholdingValueAddedTax": 9876,
        "fillingDate": 1461110400,
        "payerId": 2,
        "withholdingOthers": 987,
        "valueAddedTax": 8976,
        "withholdingSource": 897,
        "withholdingIncomeTax": 876,
        "grossValue": 9876987,
        "otherTaxes": 68,
        "sellerId": 1,
        "invoiceNumber": "0001",
        "issueDate": 1461110400,
        "dueDate": 1469836800,
        "withholdingIndustryCommerceTax": 9876
    }],
    "outlayDate": 1461456000,
    "operativeChargesInv": 10000,
    "realPaymentDate": None,
    "topYieldAuction": 0.175,
    "paymentDate": 1469836800,
    "payTransactions": [{
        "status": {
            "number": 7,
            "label": "Pre-Pagado"
        },
        "created": 1452020273,
        "pseTransaction": 1087366,
        "modified": 1452020310,
        "value": 77983868,
        "_id": 5
    }, {
        "status": {
            "number": 7,
            "label": "Pre-Pagado"
        },
        "created": 1452020273,
        "pseTransaction": 1087366,
        "modified": 1452020310,
        "value": 77983868,
        "_id": 5
    }, {
        "status": {
            "number": 7,
            "label": "Pre-Pagado"
        },
        "created": 1452020273,
        "pseTransaction": 1087366,
        "modified": 1452020310,
        "value": 77983868,
        "_id": 5
    }],
    "sellerId": 1,
    "status": {
        "number": 4,
        "label": ""
    },
    "description": "",
    "arrearsYield": 1,
    "minimumContribution": 85,
    "feeMesfix": 1,
    "mesfixCommission": 0.35,
    "auctionDueDate": 1461196800,
    "baseYieldAuction": 0.075,
    "bids": [{
        "investorId": 3,
        "inside": 8383991,
        "_id": 1,
        "value": 8383991,
        "annualYield": 0.175
    }, {
        "buyTransactions": [{
            "status": {
                "number": 7,
                "label": "Pre-Pagado"
            },
            "created": 1452020136,
            "pseTransaction": 1087362,
            "modified": 1452020174,
            "value": 6000000,
            "_id": 4
        }],
        "created": 1452016891,
        "inside": 2000000,
        "annualYield": 17.5,
        "paymentsHistory": [{
            "transactionId": 5,
            "percentageCovered": 9174572017789400.0,
            "value": 1.83491440355788e+22,
            "created": 1452020273
        }],
        "modified": 1452016891,
        "value": 2000000,
        "investorId": 1,
        "_id": 32
    }, {
        "buyTransactions": [{
            "status": {
                "number": 7,
                "label": "Pre-Pagado"
            },
            "created": 1452020136,
            "pseTransaction": 1087362,
            "modified": 1452020174,
            "value": 6000000,
            "_id": 4
        }],
        "created": 1452016891,
        "inside": 2000000,
        "annualYield": 17.5,
        "paymentsHistory": [{
            "transactionId": 5,
            "percentageCovered": 9174572017789400.0,
            "value": 1.83491440355788e+22,
            "created": 1452020273
        }],
        "modified": 1452016891,
        "value": 2000000,
        "investorId": 1,
        "_id": 33
    }, {
        "buyTransactions": [{
            "status": {
                "number": 7,
                "label": "Pre-Pagado"
            },
            "created": 1452020136,
            "pseTransaction": 1087362,
            "modified": 1452020174,
            "value": 6000000,
            "_id": 4
        }],
        "created": 1452016891,
        "inside": 2000000,
        "annualYield": 17.5,
        "paymentsHistory": [{
            "transactionId": 5,
            "percentageCovered": 9174572017789400.0,
            "value": 1.83491440355788e+22,
            "created": 1452020273
        }],
        "modified": 1452016891,
        "value": 2000000,
        "investorId": 1,
        "_id": 34
    }],
    "auctionBeginsDate": 1461110400,
    "feeMesfixRemainder": 1,
    "_id": 6
}

    import pprint
    r = perform_calculations(auction, "http://dev.mesfix.com:4001/get_auction_calculate")

    pprint.pprint(r)