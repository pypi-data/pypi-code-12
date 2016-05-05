def enum(*vals, **enums):
    """
    Enum without third party libs and compatible with py2 and py3 versions.
    """
    enums.update(dict(zip(vals, vals)))
    return type('Enum', (), enums)


SCORING_TYPE = enum(validation='validation',
                    cross_validation='crossValidation')

VERBOSITY_LEVEL = enum(SILENT=0,
                       VERBOSE=2)

MODEL_JOB_STATUS = enum(
    QUEUE='queue',
    INPROGRESS='inprogress',
    ERROR='error',
    SETTINGS='settings')

QUEUE_STATUS = enum(QUEUE='queue',
                    INPROGRESS='inprogress',
                    ERROR='error')

AUTOPILOT_MODE = enum(
    FULL_AUTO='auto',
    SEMI_AUTO='semi',
    MANUAL='manual',
)

PROJECT_STAGE = enum(EMPTY='empty',
                     EDA='eda',
                     AIM='aim',
                     MODELING='modeling')

ASYNC_PROCESS_STATUS = enum(INITIALIZED='INITIALIZED',
                            RUNNING='RUNNING',
                            COMPLETED='COMPLETED',
                            ERROR='ERROR',
                            ABORTED='ABORTED')

LEADERBOARD_SORT_KEY = enum(PROJECT_METRIC='metric',
                            SAMPLE_PCT='samplePct')

PREDICT_JOB_STATUS = enum(
    QUEUE='queue',
    INPROGRESS='inprogress',
    ERROR='error',
    ABORTED='ABORTED')


JOB_TYPE = enum(
    MODEL='model',
    PREDICT='predict'
)
