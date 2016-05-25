import logging

from .models import (check_dominant, check_recessive)

logger = logging.getLogger(__name__)

def annotate_models(batch, families):
    """Annotate what patterns of inheritance that are followed for variants in
        vcf.
        
        Args:
            vcf (cyvcf2.VCF): An iterable with variants
            families (dict): A dictionary with families 
    """
    for variant in batch:
        inheritance_strings = []
        for family_id in families:
            models_followed = []
            
            if check_dominant(variant, families[family_id]):
                models_followed.append('AD')

            if check_recessive(variant, families[family_id]):
                models_followed.append('AR_hom')
            
            family_string = "{0}:{1}".format(
                    family_id, '|'.join(models_followed))
            
            if models_followed:
                inheritance_strings.append(family_string)
        
        if inheritance_strings:
            variant.INFO['GeneticModels'] = ','.join(inheritance_strings)
        
        yield variant
        
        