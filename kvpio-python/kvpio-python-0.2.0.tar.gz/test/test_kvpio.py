

import kvpio


kvpio.load_json = True


def test_valid_account(api_base, valid_api_key):
    kvpio.api_base = api_base
    kvpio.api_key = valid_api_key

    code, res = kvpio.Account().get()
    assert code == 200
    assert type(res) == dict
    assert res.get('api_key', None) == None

def test_invalid_account(api_base, invalid_api_key):
    kvpio.api_base = api_base
    kvpio.api_key = invalid_api_key

    code, res = kvpio.Account().get()
    assert code == 404

def test_bucket_list(api_base, valid_api_key):
    kvpio.api_base = api_base
    kvpio.api_key = valid_api_key

    code, res = kvpio.Bucket().list()
    assert code == 200
    assert type(res) == list

def test_bucket_set_get_del(api_base, valid_api_key, bucket_data):
    kvpio.api_base = api_base
    kvpio.api_key = valid_api_key

    bucket = kvpio.Bucket()
    key, val, access_key, expected_val = bucket_data

    code, res = bucket.set(key, val)
    assert code == 200
    assert res == ''

    code, res = bucket.get(access_key)
    assert code == 200
    assert res == expected_val

    code, res = bucket.delete(key)
    assert code == 200
    assert res == ''

    code, res = bucket.get(access_key)
    assert code == 200
    assert res == ''

def test_template_list(api_base, valid_api_key):
    kvpio.api_base = api_base
    kvpio.api_key = valid_api_key

    code, res = kvpio.Templates().list()
    assert code == 200
    assert type(res) == list

def test_template_set_get_del(api_base, valid_api_key, template_data):
    kvpio.api_base = api_base
    kvpio.api_key = valid_api_key

    template_key, template_val, bucket_key, bucket_val, result = template_data
    bucket = kvpio.Bucket()
    template = kvpio.Templates()

    code, res = bucket.set(bucket_key, bucket_val)
    assert code == 200
    assert res == ''

    code, res = template.set(template_key, template_val)
    assert code == 200
    assert res == ''

    code, res = template.get(template_key)
    assert code == 200
    assert res == result

    code, res = template.get(template_key, data={bucket_key: bucket_val})
    assert code == 200
    assert res == result

    code, res = template.get(template_key, raw=True)
    assert code == 200
    assert res == template_val

    bucket.delete(bucket_key)
    template.delete(template_key)
