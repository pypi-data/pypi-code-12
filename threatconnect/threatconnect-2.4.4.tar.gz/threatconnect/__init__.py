__author__ = 'ThreatConnect (support@threatconnect.com)'
__version__ = '2.4.4'
__license__ = 'ASL'
__url__ = 'https://github.com/ThreatConnect-Inc/threatconnect-python'


from ThreatConnect import ThreatConnect, create_tc_arg_parser
from Resources.Adversaries import (Adversaries, AdversaryFilterObject)
from Resources.Emails import (Emails, EmailFilterObject)
from Resources.Groups import (Groups, GroupFilterObject)
from Resources.Incidents import (Incidents, IncidentFilterObject)
from Resources.Indicators import IndicatorFilterObject
from Resources import Indicators
from Resources.Owners import (Owners, OwnerFilterObject)
from Resources.Signatures import (Signatures, SignatureFilterObject)
from Resources.Threats import (Threats, ThreatFilterObject)
from Resources.Victims import (Victims, VictimFilterObject)
from Config.ResourceType import *
from Config.FilterOperator import *
