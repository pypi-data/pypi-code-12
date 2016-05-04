from .run_sql_script import RunSqlScript
from .deploy_ticket import DeployTicket, RemoveTicket
from .deploy_package import DeployPackage, RemovePackage
from .create import CreateProject, CreateTicket, CreatePackage, AddTicketToPackage
from .filter import CleanZip, SmudgeZip
import os

commands = {
    'run-sql-script': RunSqlScript,
    'deploy-ticket': DeployTicket,
    'remove-ticket': RemoveTicket,
    'deploy-package': DeployPackage,
    'remove-package': RemovePackage,
    'init': CreateProject,
    'create-ticket': CreateTicket,
    'create-package': CreatePackage,
    'add-t2p': AddTicketToPackage,
    'smudge-zip': SmudgeZip,
    'clean-zip': CleanZip,
}

if os.name == 'nt':
    from .abw_service import (
        StartService, StopService, RestartService, ServiceStatus)

    commands['start-service'] = StartService
    commands['stop-service'] = StopService
    commands['restart-service'] = RestartService
    commands['service-status'] = ServiceStatus
