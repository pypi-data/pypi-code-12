import numpy as np

class KptsController:
    def __init__(self, kpts, scheme='one'):
        self.kpts=kpts
        self.scheme=scheme

    def update(self):
        if self.scheme=='one':
            self.kpts= np.add(self.kpts, [1,1,1])

        return self.kpts
