import json

from usergrid import UsergridQuery

url = 'https://test.api.tigo.com/appservices/v1/millicom/sportsappv1-test/users?ql=select *&client_id=b3U6XoEDqrO2EeOUWh9fnLtVQw&client_secret=b3U6LHXCUAOPfcJXS1rwZ1npatin2WY&limit=500'

match_uuids = ['9f23824a-a562-11e4-af4e-356c506e70e0']

q = UsergridQuery(url)

for e in q:
    if e.get('uuid') in match_uuids:
        print json.dumps(e, indent=2)
        break
