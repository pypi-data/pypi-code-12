__author__ = 'dcortes'

from schematics.types import StringType, IntType
from schematics.types.compound import ModelType

from dexma_api_v3.factory.bases.base_entity_str import BaseEntityStr
from dexma_api_v3.factory.bases.base_entity import BaseEntity
from dexma_api_v3.factory.bases.base_cost_concept import BaseCostConcept


class PriceElectrical(BaseEntityStr):

    type = StringType(required=True)
    account = ModelType(BaseEntity, required=True)
    name = StringType(required=True)
    num_of_periods = IntType(required=True)
    tariff_structure = ModelType(BaseEntity, required=True)
    consumption = ModelType(BaseCostConcept, required=True)
    contracted_demand = ModelType(BaseCostConcept, required=True)
    demand_excess_penalty = ModelType(BaseCostConcept, required=True)
    reactive_penalty = ModelType(BaseCostConcept, required=True)