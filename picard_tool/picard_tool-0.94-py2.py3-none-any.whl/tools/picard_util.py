import os

import pandas as pd

def picard_select_tsv_to_df(stats_path, select, logger):
    read_header = False
    data_dict = dict()
    if not os.path.exists(stats_path):
        logger.info('the stats file %s do not exist, so return None' % stats_path)
        return None
    logger.info('stats_path=%s' % stats_path)
    with open(stats_path, 'r') as stats_open:
        i = 0
        for line in stats_open:
            line = line.strip('\n')
            logger.info('line=\n%s' % line)
            if line.startswith('#'):
                continue
            line_split = line.split('\t')
            logger.info('len(line_split)=%s' % str(len(line_split)))
            if not read_header and len(line_split) > 1:
                if select == line_split[0]:
                    header = line_split
                    read_header = True
            elif read_header and len(line_split) == 1:
                df_index = list(range(len(data_dict)))
                df = pd.DataFrame.from_dict(data_dict, orient='index')
                logger.info('df=\n%s' % df)
                df.columns = header
                return df
            elif read_header and len(line_split) > 0:
                if len(line_split) == len(header):
                    logger.info('store line=\n%s' % line)
                    data_dict[i] = line_split
                    i += 1
            elif not read_header and len(line_split) == 1:
                continue
            else:
                logger.info('strange line: %s' % line)
                sys.exit(1)
    if not read_header:
        logger.info('bam file was probably too small to generate stats as header not read: %s' % stats_path)
        return None
    logger.debug('no data saved to df')
    sys.exit(1)
    return
