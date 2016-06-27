import Pyro4.core
import updb


class PrimeServer(updb.UPdb_mixin):
    def next_prime(self, p):
        """
        Naive, flaky and slow way to get the next
        prime number after that given.
        """
        if p < 2:
            # return first prime: 2
            return 2
        i = p  # start where we left off
        while True:
            i += 1
            probe = 2
            while True:
                if i % probe == 0:
                    # i is composite
                    break
                if probe >= p:
                    # i is co-prime to integers up to p.
                    return i
                probe += 1


def main():
    daemon = Pyro4.core.Daemon(port=7766)
    daemon.register(PrimeServer(), "rpc")
    daemon.requestLoop()

if __name__ == '__main__':
    main()
