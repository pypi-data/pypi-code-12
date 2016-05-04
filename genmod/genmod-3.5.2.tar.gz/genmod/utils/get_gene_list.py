import logging

logger = logging.getLogger(__name__)

def get_gene_list(genes):
    """Get a set of genes
    
        Args:
            genes (iterable)
        
        Returns:
            gene_list (set): A set of gene ids
    """
    gene_list = set()
    nr_genes = 0
    if genes:
        for gene in genes:
            if not gene.startswith('#'):
                nr_genes += 1
                gene_id = gene.rstrip().split()[0]
                logger.debug("Adding gene {0} to gene list".format(gene_id))
                gene_list.add(gene_id)

        logger.info("Found {0} genes".format(nr_genes))
    
    return gene_list

