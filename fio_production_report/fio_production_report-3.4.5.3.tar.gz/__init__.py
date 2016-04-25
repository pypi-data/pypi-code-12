# -*- coding: utf-8 -*-
from trytond.pool import Pool
from production import ProductionReport, ProductionScheduleReport, \
    ProductionScheduleReportWizardStart, ProductionScheduleReportWizard, \
    Production, BOMTreeReport


def register():
    Pool.register(
        ProductionReport,
        BOMTreeReport,
        ProductionScheduleReport,
        module='production_report', type_='report'
    )
    Pool.register(
        ProductionScheduleReportWizardStart,
        Production,
        module='production_report', type_='model'
    )
    Pool.register(
        ProductionScheduleReportWizard,
        module='production_report', type_='wizard'
    )
