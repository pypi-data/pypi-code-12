#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import metzoo_opc
import logging


def init_logger(log_name, log_filename):
    LOG_FORMAT = "%(asctime)-15s %(levelname)9s  %(filename)s:%(lineno)s %(message)s"
    logging.basicConfig(filename=log_filename, level=logging.INFO, format=LOG_FORMAT)

    logger = logging.getLogger(log_name)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    return logger


def init_opc(logger, config_filename):
    try:
        config = metzoo_opc.YAMLConfig(config_filename)
    except Exception as ex:
        logger.error("can't create yaml config: {}".format(ex))
        return None
    else:
        logger.debug("yaml config loaded from {}".format(config_filename))

    opc = None
    try:
        opc = metzoo_opc.MetzooOPC(config)
    except Exception as ex:
        logger.error("can't create opc: {}".format(ex))
    else:
        logger.debug("opc created with yaml config")

    return opc


def init_db(logger, db_filename, mapping):
    try:
        db = metzoo_opc.DB(db_filename, mapping)
    except Exception as ex:
        logger.error("can't connect to '{}' db: {}".format(db_filename, ex))
    else:
        logger.debug("connected to '{}' db".format(db_filename))

    return db


def opc_data(value):
    return metzoo_opc.OPCData(None, value[0], value[1], value[2], value[3])


def main(config_filename, db_filename, log_filename):
    logger = init_logger("MetzooOPC", log_filename)
    logger.debug("============================== start ==============================")

    opc = init_opc(logger, config_filename)
    if opc is None:
        sys.exit(-1)

    db = init_db(logger, db_filename, opc.mapping)
    if db is None:
        sys.exit(-2)

    read_data = opc.read()
    logger.debug("read data: {}".format(read_data))

    saved_data = db.load()
    logger.debug("saved data: {}".format(saved_data))

    all_data = saved_data[:]
    all_data.extend(read_data) 

    logger.debug("sending: {}".format(all_data))
    sent_data, error_data = opc.send(all_data)

    logger.debug("sent data: {}".format(sent_data))
    db.delete([data.data_id for data in sent_data if data.data_id is not None])

    logger.debug("error data: {}".format(error_data))
    for data in error_data:
        if data.data_id is None:
            db.save(data)


import argparse

if __name__ == "__main__":
    program = "metzoo_opc"
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("--config", type=str, default="{}.yaml".format(program),
                        help="YAML file to load as configuration")

    parser.add_argument("--db", type=str, default="{}.db".format(program),
                        help="Local sqlite3 database to save data that couldn't be sent")

    parser.add_argument("--log", type=str, default="{}.log".format(program),
                        help="Log file to append logs")

    args = parser.parse_args()
    main(args.config, args.db, args.log)
