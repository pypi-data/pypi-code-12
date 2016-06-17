""" third-party """
from enum import Enum


class ResourceType(Enum):
    """ """
    # misc
    # ATTRIBUTES = 10
    # DNS_RESOLUTIONS = 20
    OWNERS = 30
    # OWNER_MINE = 32
    OWNER_MEMBERS = 34
    OWNER_METRICS = 36
    BULK = 40

    # groups
    ADVERSARIES = 115
    DOCUMENTS = 125
    EMAILS = 135
    # FILE_OCCURRENCES = 145
    GROUPS = 150
    INCIDENTS = 165
    # SECURITY_LABELS = 175
    SIGNATURES = 185
    TAGS = 195
    TASKS = 200
    THREATS = 205

    # indicators
    INDICATORS = 505
    ADDRESSES = 515
    EMAIL_ADDRESSES = 525
    FILES = 535
    HOSTS = 545
    URLS = 555

    # victims
    VICTIMS = 905

    # victims
    VICTIM_ASSETS = 1005
    VICTIM_EMAIL_ADDRESSES = 1015
    VICTIM_NETWORK_ACCOUNTS = 1025
    VICTIM_PHONES = 1035
    VICTIM_SOCIAL_NETWORKS = 1045
    VICTIM_WEBSITES = 1055

    # batch jobs
    BATCH_JOBS = 1075

    DNS_RESOLUTIONS = 1080
