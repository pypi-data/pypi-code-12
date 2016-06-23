#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from sys import exit
from metzoo import lib


def init_logger(name, filename):
    LOG_FORMAT = "%(asctime)-15s %(levelname)9s  %(filename)s:%(lineno)s %(message)s"
    logging.basicConfig(filename=filename, level=logging.DEBUG, format=LOG_FORMAT)

    logger = logging.getLogger(name)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    return logger


def validate_config(name, config_dict, logger, properties):
    for p in properties:
        if lib.config.get(config_dict, p) is None:
            logger.error("invalid configuration for '{}': '{}' property not found".format(name, p))
            exit(-4)


def init_config(filename, logger):
    logger.debug("initializing configuration '{}'".format(filename))
    config_dict = None
    try:
        config_dict = lib.config.load_yaml_dict(filename)
    except IOError as e:
        logger.error("can't load '{}': {}".format(filename, e))
        exit(-3)

    validate_config(filename, config_dict, logger, ["metzoo", "metzoo.customer_key", "metzoo.url"])

    logger.debug("configuration loaded")
    return config_dict


def init_db(filename, logger):
    logger.debug("initializing db '{}'".format(filename))
    try:
        db = lib.DB(filename)
    except Exception as ex:
        logger.error("can't connect to '{}' db: {}".format(filename, ex))
        exit(-2)
    else:
        logger.debug("connected to '{}' db".format(filename))

    return db


def send(data_list, config_dict, logger):
    customer_key = lib.config.get(config_dict, "metzoo.customer_key")
    url = lib.config.get(config_dict, "metzoo.url")

    # sort by timestamp
    data_list = sorted(data_list, key=lambda x: x.timestamp)

    grouped_data = dict()
    for data in data_list:
        # group by (agent, timestamp) or (timestamp, agent) [is the same]
        key = (data.agent, data.timestamp)
        try:
            grouped_data[key].append(data)
        except KeyError:
            grouped_data[key] = [data]

    for agent_name, timestamp in grouped_data:
        try:
            agent = lib.Agent(customer_key, agent_name, url)
        except Exception as e:
            logger.warn("can't create agent '{}' for '{}' at '{}' because: {}".format(agent_name, customer_key, url, e))
        else:
            d = dict()
            agent_data = grouped_data[(agent_name, timestamp)]
            for data in agent_data:
                d[data.metric] = data.value
            try:
                response = agent.send(d, timestamp)
            except Exception as e:
                logger.warn("can't send data '{}' for '{}' at '{}' because: {} :: '{}'".format(d, agent, timestamp, type(e), e))
            else:
                yield agent_data


def write(config_file, db_file, log):
    logger = init_logger("metzoo-writer", log)
    logger.debug("============================== start ==============================")

    config_dict = init_config(config_file, logger)
    db = init_db(db_file, logger)

    saved_data = db.load()

    logger.debug("sending: {}".format(saved_data))
    for data_set in send(saved_data, config_dict, logger):
        db.delete([data.data_id for data in data_set])

    logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ end ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


def main():
    program = "metzoo-writer"

    import argparse
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("--config", type=str, default="{}.yaml".format(program),
                        help="YAML file to load as configuration")

    parser.add_argument("--db", type=str, default="{}.db".format(program),
                        help="Local sqlite3 database to save data that couldn't be sent")

    parser.add_argument("--log", type=str, default="{}.log".format(program),
                        help="Log file to append logs")

    args = parser.parse_args()
    write(args.config, args.db, args.log)

if __name__ == "__main__":
    main()
