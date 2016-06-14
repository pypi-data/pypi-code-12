from django.core.management.base import BaseCommand
from elasticsearch_dsl.connections import connections

from ievv_opensource import ievv_elasticsearch2
from ievv_opensource.demo.elasticsearch2demo.doctypes import CompanyDocType, EmployeeDocType
from ievv_opensource.demo.elasticsearch2demo.models import Company, Employee
from ievv_opensource.ievv_batchframework import batchregistry


class Command(BaseCommand):
    help = 'Tullball.'

    def handle(self, *args, **options):
        connections.get_connection().indices.delete('_all')
        CompanyDocType.init()
        EmployeeDocType.init()

        company, created = Company.objects.get_or_create(name='test')
        company.save()

        employee1, created = Employee.objects.get_or_create(name='Jane Doe', company=company)
        employee2, created = Employee.objects.get_or_create(name='Joe Doe', company=company)
        executioninfo = batchregistry.Registry.get_instance().run(
            actiongroup_name='elasticsearch2demo_employee_update',
            # context_object=company,
            ids=[employee1.id, employee2.id]
        )

        connections.get_connection().indices.flush('_all')

        for match in ievv_elasticsearch2.Search().query('match_all').execute():
            print(match.to_dict())
