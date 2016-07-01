# import asyncio
# import unittest
#
# from functools import wraps
#
#
# def run_until_complete(fun):
#     if not asyncio.iscoroutinefunction(fun):
#         fun = asyncio.coroutine(fun)
#
#     @wraps(fun)
#     def wrapper(test, *args, **kw):
#         loop = test.loop
#         ret = loop.run_until_complete(
#             asyncio.wait_for(fun(test, *args, **kw), 150, loop=loop))
#         return ret
#
#     return wrapper


# class BaseTest(unittest.TestCase):
#     """Base test case for unittests.
#     """
#
#     def setUp(self):
#         self.loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(None)
#
#     def tearDown(self):
#         self.loop.close()
#         del self.loop


# class TestBasicUsage(BaseTest):
#
#     # @run_until_complete
#     def test_put_object(self):
#
#         session = aiobotocore.get_session(loop=self.loop)
#         client = session.create_client(
#             's3', region_name='us-west-2')
#
#         data = b'\x01' * 1024
#         bucket = 'dataintake'
#         filename = 'dummy.bin'
#         folder = 'aiobotocore'
#         key = '{}/{}'.format(folder, filename)
#
#         resp = yield from client.put_object(Bucket=bucket,
#                                             Key=key,
#                                             Body=data)
#         print(resp)
#         # self.assertEqual(resp, None)
#
#         resp = yield from client.get_object_acl(Bucket=bucket,
#                                                 Key=key)
#         # self.assertEqual(resp, None)
#         print(resp)
#         resp = yield from client.delete_object(Bucket=bucket,
#                                                Key=key)
#         self.assertEqual(resp, None)
#
#     # @run_until_complete
#     def test_put_get_object(self):
#         session = aiobotocore.get_session(loop=self.loop)
#         client = session.create_client('s3', region_name='us-west-2')
#
#         data = b'\x01' * 10
#         bucket = 'dataintake'
#         filename = 'dummy.bin'
#         folder = 'aiobotocore'
#         key = '{}/{}'.format(folder, filename)
#
#         resp = yield from client.put_object(Bucket=bucket,
#                                             Key=key,
#                                             Body=data)
#         print(resp)
#         # self.assertEqual(resp, None)
#         import ipdb; ipdb.set_trace()
#         resp = yield from client.get_object(Bucket=bucket,
#                                             Key=key)
#         self.assertEqual(resp['Body'], data)
#         # self.assertEqual(resp, None)
#
#         print(resp)
#         resp = yield from client.delete_object(Bucket=bucket,
#                                                Key=key)
#         self.assertEqual(resp, None)
#
#     # @run_until_complete
#     def test_mutipart_upload(self):
#         # https://github.com/boto/boto3/issues/50#issuecomment-72079954
#         session = aiobotocore.get_session(loop=self.loop)
#         client = session.create_client(
#             's3', region_name='us-west-2',
#             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#             aws_access_key_id=AWS_ACCESS_KEY_ID)
#         data = b'\x01' * 1024 * 1024 * 6
#         bucket = 'dataintake'
#         filename = 'dummy.bin'
#         folder = 'aiobotocore'
#         key = '{}/{}'.format(folder, filename)
#
#         resp = yield from client.create_multipart_upload(
#             Bucket=bucket, Key=key)
#         upload_id = resp['UploadId']
#         print(upload_id)
#
#         try:
#             part_info = {'Parts': []}
#
#             for i in range(1, 4):
#                 resp = yield from client.upload_part(
#                     Bucket=bucket, Key=key, UploadId=upload_id, PartNumber=i,
#                     Body=data)
#                 part = {'PartNumber': i, 'ETag': resp['ETag']}
#                 part_info['Parts'].append(part)
#
#                 # self.assertEqual(resp, None)
#             resp = yield from client.complete_multipart_upload(
#                 Bucket=bucket, Key=key, UploadId=upload_id,
#                 MultipartUpload=part_info)
#             # self.assertEqual(resp, None)
#
#             resp = yield from client.delete_object(Bucket=bucket,
#                                                    Key=key)
#             # self.assertEqual(resp, None)
#         except Exception as e:
#             resp = yield from client.abort_multipart_upload(
#                 Bucket=bucket, Key=key, UploadId=upload_id)
#             print(resp)
#             raise e
