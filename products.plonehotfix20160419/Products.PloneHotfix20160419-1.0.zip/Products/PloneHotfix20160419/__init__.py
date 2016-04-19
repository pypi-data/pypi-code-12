import logging
import pkg_resources

logger = logging.getLogger('Products.PloneHotfix20160419')

# General hotfixes for all.
hotfixes = [
    'publishing'
]
# Some hotfixes apply only when a specific package is available.
try:
    pkg_resources.get_distribution('plone.dexterity')
except pkg_resources.DistributionNotFound:
    pass
else:
    hotfixes.append('dexterity')
try:
    pkg_resources.get_distribution('five.pt')
except pkg_resources.DistributionNotFound:
    pass
else:
    hotfixes.append('five_pt')

# Apply the fixes
for hotfix in hotfixes:
    try:
        __import__('Products.PloneHotfix20160419.%s' % hotfix)
        logger.info('Applied %s patch' % hotfix)
    except:
        logger.warn('Could not apply %s' % hotfix)
if not hotfixes:
    logger.info('No hotfixes were needed.')
else:
    logger.info('Hotfix installed')
