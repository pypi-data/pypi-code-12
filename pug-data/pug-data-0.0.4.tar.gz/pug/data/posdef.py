r"""Faulty positive semidefinite matrix generator

References:
  https://en.wikipedia.org/wiki/Positive-definite_matrix
  https://en.wikipedia.org/wiki/Random_matrix

Using a normally distributed random matrix it's pretty
rare that you'll get a semidefinite matrix from the product,
even for low dimensions. For 3 dimensions you have a ~7% yield

>>> np.random.seed(2)
>>> pos_semi_matrices = generate_positive_semidefinite_matrices(num_samples=1000)
  6.7% were positive semidefinite and not positive definite
 45.5% were positive definite
 52.2% were positive semidefinite
 47.8% were neither positive definite nor positive semidefinite
"""

import numpy as np


def generate_positive_semidefinite_matrices(num_dimensions=3, num_samples=1000):
    positive_semidefinite_matrices = []
    pos_semidef = np.zeros(num_samples).astype(bool)
    pos_def = np.zeros(num_samples).astype(bool)

    for i in range(num_samples):
        B = np.random.randn(num_dimensions - 1, num_dimensions)
        A = np.dot(B.T, B)
        eigvals = np.linalg.eigvals(A)
        # is it positive semidefinite?
        pos_semidef[i] = np.all(eigvals >= 0)
        pos_def[i] = np.all(eigvals > 0)
        if pos_semidef[i]:
            positive_semidefinite_matrices.append(A)

    num_samples = float(num_samples)

    print("{: 6.1%} were positive semidefinite and not positive definite".format(
          np.sum(~pos_def & pos_semidef) / num_samples))
    print("{: 6.1%} were positive definite".format(
          np.sum(pos_def) / num_samples))
    print("{: 6.1%} were positive semidefinite".format(
          np.sum(pos_semidef) / num_samples))
    print("{: 6.1%} were neither positive definite nor positive semidefinite".format(
          np.sum(~pos_semidef & ~pos_def) / num_samples))

    return positive_semidefinite_matrices, pos_semidef, pos_def

