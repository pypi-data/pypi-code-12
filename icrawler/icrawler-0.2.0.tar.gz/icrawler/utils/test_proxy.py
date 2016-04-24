import sys
import logging
from proxy_pool import ProxyPool


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        level=logging.INFO, stream=sys.stderr)
    logging.getLogger('requests').setLevel(logging.WARNING)
    proxy_pool = ProxyPool()
    proxy_pool.default_scan('overseas', 10, val_thr_num=10, out_file='proxy_overseas.json')
