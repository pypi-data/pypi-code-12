from revscoring.languages import english
from revscoring.scorers.rf import RFModel

from ..feature_lists.enwiki import wp10

wp10_random_forest = RFModel(wp10,
                             language=english,
                             n_estimators=501,
                             min_samples_leaf=8,
                             criterion='entropy')
"""
Based on work by Nettrom[1] and with a few improvements and extensions.

1. Warncke-Wang, M., Cosley, D., & Riedl, J. (2013, August). Tell me more: An
   actionable quality model for wikipedia. In Proceedings of the 9th
   International Symposium on Open Collaboration (p. 8). ACM.
   http://opensym.org/wsos2013/proceedings/p0202-warncke.pdf
"""
