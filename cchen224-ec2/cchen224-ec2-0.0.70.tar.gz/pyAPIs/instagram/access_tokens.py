
access_tokens = [
    # '749251359.198dc17.54fcbd09891c43ccb1b76b5270ba0737',
    # '749251359.0fb3e12.ef6300e138b04878ba4a77945b383b45',
    # '749251359.bdf3906.cfea5882c3a94746909790f786e23209',
    # '749251359.e4af174.11544055c2384eb5ab1e3a21cd93664d',
    # '749251359.e4af174.11544055c2384eb5ab1e3a21cd93664d',
    '',
    '937212526.80bcce7.41f9aea947504150b418c4d60d159929',
    '937212526.d2aec0b.24b8d6c3940643a592b5c72512e42d4c',
    '937212526.5f06f7a.90966e83f9dd43eeb1fac3d135abed24',
    '937212526.35519fe.91c4ebdf62444231b36df3066a9a62e1',
    '937212526.d356296.1ec199e742b540b69017d1fdc0838404',
    '937280448.63a8f6e.f08c72c5df0a46099da1c17b2022b4ef',
    '937280448.09bccc4.d4c901f227464006a60b7367f92c023d',
    '937280448.948a325.347e49226f974a718765c8611720f780',
    '937280448.197d7e4.0ba69739bf02428782546dbdacc9337f',
    '937280448.5182a49.11af1a709c9c4fa7b9c96a4f6bb38ac7',
    '937358110.64ee73f.9ea27205a93d485a932fbbd771122574',
    '937358110.a358ce4.de1b7e677c86409ca93916e972c7d2d0',
    '937358110.7de18ec.01ef8f2c7591467b99285e0f8abb0b20',
    '937358110.38e9503.edb2757a445e48bb9cbf35a90ac60ede',
    '937358110.7781482.f19e57cac4cd455b8c3d68ed1c3d1462',
    '938075294.a594a2a.0924280c580147b5b43ba715a3f90052',
    '938075294.8576c14.dbd08371297f4956bc3f9142b4ba5944',
    '938075294.93b5a61.a03807e6e0c848e1adda4722f5aafc6d',
    '938075294.71ab8b9.97fbee0735a64f8c90dcbaeca7457f7e',
    '938075294.938bcc8.09a1241cf00e4a6fb899207704749a17'
]

#
# from instagram.client import InstagramAPI
# import instagram
# import httplib2
# import time
# solution = []
# for token in access_tokens:
#     api = InstagramAPI(access_token=token)
#     try:
#         g = api.user_followed_by('12864526', as_generator=True, max_pages=999999)
#         g.next()
#         solution.append(True)
#     except instagram.InstagramAPIError, e:
#         if str(e.status_code) == '429':
#             solution.append(True)
#         elif str(e.status_code) == '400':
#             solution.append(False)
#         else:
#             print e.status_code, e.error_message
#     except httplib2.ServerNotFoundError:
#         time.sleep(10)