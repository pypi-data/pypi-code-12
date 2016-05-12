from __future__ import unicode_literals
from .base import APIClient


# Antenna services
class antenna(object):
    _application_name = 'Antenna'
    antenna = APIClient(application=_application_name,
                        service_uri='Antenna/')


# App Manager Services
class app_manager(object):
    _application_name = 'AppManager'
    app = APIClient(application=_application_name,
                    service_uri='App/')
    app_menu = APIClient(application=_application_name,
                         service_uri='App/{idApp}/MenuItem/')
    menu_item_user = APIClient(application=_application_name,
                               service_uri='MenuItem/User/{idUser}/')
    app_member = APIClient(application=_application_name,
                           service_uri='App/{idApp}/Member/')


# Contacts Services
class contacts(object):
    _application_name = 'Contacts'
    campaign = APIClient(application=_application_name,
                         service_uri='Campaign/')
    group = APIClient(application=_application_name,
                      service_uri='Group/')
    contact = APIClient(application=_application_name,
                        service_uri='Contact/')
    campaign_contact = APIClient(
        application=_application_name,
        service_uri='Campaign/{idCampaign}/Contact/')
    group_contact = APIClient(
        application=_application_name,
        service_uri='Group/{idGroup}/Contact/')
    opportunity = APIClient(application=_application_name,
                            service_uri='Opportunity/')
    opportunity_history = APIClient(
        application=_application_name,
        service_uri='Opportunity/{idOpportunity}/History/')
    opportunity_contact = APIClient(
        application=_application_name,
        service_uri='Opportunity/{idOpportunity}/Contact/')
    activity_type = APIClient(application=_application_name,
                              service_uri='ActivityType/')
    activity = APIClient(
        application=_application_name,
        service_uri='ActivityType/{idActivityType}/Activity/')
    campaign_activity = APIClient(
        application=_application_name,
        service_uri='Campaign/{idCampaign}/Activity/')


# DNS Services
class dns(object):
    _application_name = 'DNS'
    asn = APIClient(application=_application_name,
                    service_uri='ASN/')
    allocation = APIClient(application=_application_name,
                           service_uri='Allocation/')
    subnet = APIClient(application=_application_name,
                       service_uri='Subnet/')
    subnet_space = APIClient(
        application=_application_name,
        service_uri='Allocation/{idAllocation}/Subnet_space/')
    ipaddress = APIClient(application=_application_name,
                          service_uri='IPAddress/')
    recordptr = APIClient(application=_application_name,
                          service_uri='RecordPTR/')
    domain = APIClient(application=_application_name,
                       service_uri='Domain/')
    record = APIClient(application=_application_name,
                       service_uri='Record/')
    aggregated_blacklist = APIClient(application=_application_name,
                                     service_uri='AggregatedBlacklist/')
    blacklist = APIClient(application=_application_name,
                          service_uri='CIXBlacklist/')
    whitelist = APIClient(application=_application_name,
                          service_uri='CIXWhitelist/')
    blacklist_source = APIClient(application=_application_name,
                                 service_uri='BlacklistSource/')


# Documentation Services
class documentation(object):
    _application_name = 'Documentation'
    application = APIClient(application=_application_name,
                            service_uri='Application/')


# HelpDesk
class helpdesk(object):
    _application_name = 'HelpDesk'
    ticket = APIClient(application=_application_name,
                       service_uri='Ticket/{idTransactionType}/')
    ticket_history = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/'
                    '{transactionSequenceNumber}/History/')
    status = APIClient(application=_application_name,
                       service_uri='Status/')
    reason_for_return = APIClient(application=_application_name,
                                  service_uri='ReasonForReturn/')
    reason_for_return_translation = APIClient(
        application=_application_name,
        service_uri='ReasonForReturn/{idReasonForReturn}/Translation/')
    ticket_question = APIClient(application=_application_name,
                                service_uri='TicketQuestion/')
    ticket_type = APIClient(application=_application_name,
                            service_uri='TicketType/')
    ticket_type_question = APIClient(
        application=_application_name,
        service_uri='TicketType/{id}/TicketQuestion/')
    iris_condition = APIClient(application=_application_name,
                               service_uri='IRISCondition/')
    iris_extended_condition = APIClient(application=_application_name,
                                        service_uri='IRISExtendedCondition/')
    iris_defect = APIClient(application=_application_name,
                            service_uri='IRISDefect/')
    iris_ntf = APIClient(application=_application_name,
                         service_uri='IRISNTF/')
    iris_repair = APIClient(application=_application_name,
                            service_uri='IRISRepair/')
    iris_section = APIClient(application=_application_name,
                             service_uri='IRISSection/')
    iris_symptom = APIClient(application=_application_name,
                             service_uri='IRISSymptom/')
    item_status = APIClient(application=_application_name,
                            service_uri='ItemStatus/')
    item = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/{transactionSequenceNumber}/Item/')
    item_history = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/{transactionSequenceNumber}/Item/{idItem}/History/')
    item_part_used = APIClient(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/{transactionSequenceNumber}/Item/{idItem}/PartUsed/')
    warrantor_logic = APIClient(
        application=_application_name,
        service_uri='WarrantorLogic/')
    service_centre_logic = APIClient(
        application=_application_name,
        service_uri='ServiceCentreLogic/')
    warrantor_service_centre = APIClient(
        application=_application_name,
        service_uri='Warrantor/{idAddress}/ServiceCentre/')
    service_centre_warrantor = APIClient(
        application=_application_name,
        service_uri='ServiceCentre/{idAddress}/Warrantor/')


# Membership
class membership(object):
    _application_name = 'Membership'
    address = APIClient(application=_application_name,
                        service_uri='Address/')
    address_link = APIClient(application=_application_name,
                             service_uri='Address/{idAddress}/Link/')
    country = APIClient(application=_application_name,
                        service_uri='Country/')
    currency = APIClient(application=_application_name,
                         service_uri='Currency/')
    department = APIClient(application=_application_name,
                           service_uri='Member/{idMember}/Department/')
    language = APIClient(application=_application_name,
                         service_uri='Language/')
    member = APIClient(application=_application_name,
                       service_uri='Member/')
    member_link = APIClient(application=_application_name,
                            service_uri='Member/{idMember}/Link/')
    notification = APIClient(application=_application_name,
                             service_uri='Address/{idAddress}/Notification/')
    profile = APIClient(application=_application_name,
                        service_uri='Member/{idMember}/Profile/')
    subdivision = APIClient(application=_application_name,
                            service_uri='Country/{idCountry}/Subdivision/')
    team = APIClient(application=_application_name,
                     service_uri='Member/{idMember}/Team/')
    territory = APIClient(application=_application_name,
                          service_uri='Member/{idMember}/Territory/')
    timezone = APIClient(application=_application_name,
                         service_uri='Timezone/')
    transaction_type = APIClient(application=_application_name,
                                 service_uri='TransactionType/')
    user = APIClient(application=_application_name,
                     service_uri='User/')


# Reporting
class reporting(object):
    _application_name = 'Reporting'
    report = APIClient(application=_application_name,
                       service_uri='Report/')
    report_template = APIClient(application=_application_name,
                                service_uri='ReportTemplate/')
    package = APIClient(application=_application_name,
                        service_uri='Package/')
    export = APIClient(application=_application_name,
                       service_uri='Export/')


# SCM
class scm(object):
    _application_name = 'SCM'
    brand = APIClient(application=_application_name,
                      service_uri='Brand/')
    # idSKUComponent should be passed as pk to resource methods
    critical_bom = APIClient(application=_application_name,
                             service_uri='SKU/{idSKU}/BOM/')
    # CriticalBOM for member returns all BOM records for the idMember
    # doing the request
    critical_bom_for_member = APIClient(application=_application_name,
                                        service_uri='SKU/BOM/')
    manufactured_item = APIClient(application=_application_name,
                                  service_uri='ManufacturedItem/')
    return_question = APIClient(application=_application_name,
                                service_uri='ReturnQuestion/')
    return_question_field_type = APIClient(
        application=_application_name, service_uri='ReturnQuestionFieldType/')
    service_group = APIClient(application=_application_name,
                              service_uri='ServiceGroup/')
    sku = APIClient(application=_application_name, service_uri='SKU/')
    sku_stock = APIClient(application=_application_name,
                          service_uri='SKU/{idSKU}/Stock/')
    sku_value = APIClient(application=_application_name,
                          service_uri='SKU/{idSKU}/Value/')
    sku_category = APIClient(application=_application_name,
                             service_uri='SKUCategory/')
    sku_category_return_question = APIClient(
        application=_application_name,
        service_uri='SKUCategory/{idSKUCategory}/ReturnQuestion/')


# Scheduler
class scheduler(object):
    _application_name = 'Scheduler'
    task = APIClient(application=_application_name,
                     service_uri='Task/')
    task_log = APIClient(application=_application_name,
                         service_uri='TaskLog/')
    execute_task = APIClient(application=_application_name,
                             service_uri='Task/{idTask}/execute/')


# Support Framework Services
class support_framework(object):
    _application_name = 'SupportFramework'
    member = APIClient(application=_application_name,
                       service_uri='Member/')
    application = APIClient(application=_application_name,
                            service_uri='Member/{idMember}/Application/')
    service = APIClient(application=_application_name,
                        service_uri='Member/{idMember}/Application/{idApplication}/Service/')
    method = APIClient(application=_application_name,
                       service_uri='Member/{idMember}/Application/{idApplication}/Service/{idService}/Method/')
    method_parameter = APIClient(application=_application_name,
                                 service_uri='Member/{idMember}/Application/{idApplication}/Service/{idService}/Method/{idMethod}/Parameter/')
    dto = APIClient(application=_application_name,
                    service_uri='DTO/')
    dto_parameter = APIClient(application=_application_name,
                              service_uri='DTO/{idDTO}/Parameter/')
    exception_code = APIClient(application=_application_name,
                               service_uri='ExceptionCode/')
    language_exception_code = APIClient(application=_application_name,
                                        service_uri='ExceptionCode/{exception_code}/Language/')


# Training
class training(object):
    _application_name = 'Training'
    syllabus = APIClient(application=_application_name,
                         service_uri='Syllabus/')
    cls = APIClient(application=_application_name,
                    service_uri='Class/')
    student = APIClient(application=_application_name,
                        service_uri='Student/')


# Security
class security(object):
  _application_name = 'Security'
  security_event = APIClient(application=_application_name,
                             service_uri='SecurityEvent/')
  security_event_logout = APIClient(
      application=_application_name,
      service_uri='SecurityEvent/{idUser}/Logout/')


# Asset
class asset(object):
  _application_name = 'Asset'
  asset = APIClient(application=_application_name,
                    service_uri='Asset/')
  asset_transaction = APIClient(application=application_name,
                                service_uri='Asset/{idAsset}/Transaction/')
  depreciation_type = APIClient(application=application_name,
                                service_uri='DepreciationType/')


# Import Engine (BETA)
class import_engine(object):
    _application_name = 'Import'
    application = APIClient(application=_application_name,
                            service_uri='Application/')
    model = APIClient(application=_application_name,
                      service_uri='Application/{idApplication}/Model/')
    import_service = APIClient(application=_application_name,
                               service_uri='Import/')
