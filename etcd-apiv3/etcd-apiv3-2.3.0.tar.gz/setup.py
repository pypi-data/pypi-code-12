from setuptools import setup

setup(
    name='etcd-apiv3',
    version='2.3.0',
    description='etcd apiv3 bindings for Python',
    maintainer='spyzalski@mirantis.com',
    packages=['etcd.snap', 'etcd.etcdserver', 'etcd.etcdserver.etcdserverpb', 'etcd.storage.storagepb', 'etcd.snap.snappb', 'etcd.auth.authpb', 'etcd.lease', 'etcd.storage', 'etcd.raft', 'etcd', 'etcd.wal.walpb', 'etcd.wal', 'etcd.raft.raftpb', 'etcd.lease.leasepb', 'etcd.auth', 'gogoproto'],
    install_requires=['grpcio'],
    classifiers=[
        'Topic :: Software Development :: Code Generators',
        'Topic :: Database',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
    ]
)
