#!/usr/bin/env python
"""Configuration parser."""

import json
import re


def parse(json_string):
    """Returns a dictionary with settings from the configuration data."""
    # parse the JSON data
    conf = {}
    try:
        data = json.loads(json_string)
    except ValueError:
        raise ValueError("conf file is not valid JSON")

    # parse the certificates data
    conf["ca"] = parse_ca(data)
    check_unique_nicknames(conf)

    # check logging
    conf["logging"] = parse_logging(data)
    return conf


def find_profile(cnf, profile_nickname):
    """Returns the conf dictionary for the profile in cnf or None if not found."""
    for ca in cnf["ca"]:
        if ca["nickname"] == profile_nickname:
            return ca

        if "subca" in ca:
            for subca in ca["subca"]:
                if subca["nickname"] == profile_nickname:
                    return subca

                if "cert" in subca:
                    for cert in subca["cert"]:
                        if cert["nickname"] == profile_nickname:
                            return cert

        if "cert" in ca:
            for cert in ca["cert"]:
                if cert["nickname"] == profile_nickname:
                    return cert
    return None


def find_issuer_cert(cnf, cert_nickname):
    """Returns (issuer_conf, cert_conf) for cert_nickname or (None, None) otherwise."""
    for ca in cnf["ca"]:
        # check if the cert is under a ca
        if "cert" in ca:
            for cert in ca["cert"]:
                if cert["nickname"] == cert_nickname:
                    return (ca, cert)

        # check if the cert is under a subca
        # this code has the limitation that a subca under a subca would not work
        if "subca" in ca:
            for subca in ca["subca"]:
                if "cert" in subca:
                    for cert in subca["cert"]:
                        if cert["nickname"] == cert_nickname:
                            return (subca, cert)

    # if we loop through all the issuer and make it here, then we did not find it
    return (None, None)


def find_issuers(cnf):
    """Returns a list of all CA and SubCA in the cnf."""
    results = []
    for ca in cnf["ca"]:
        results.append(ca)
        if "subca" in ca:
            for subca in ca["subca"]:
                results.append(subca)
    return results


def find_issuer(cnf, profile_nickname):
    """Returns the conf dictionary for the CA or SubCA in cnf or None if not found."""
    for ca in cnf["ca"]:
        if ca["nickname"] == profile_nickname:
            return ca

        if "subca" in ca:
            for subca in ca["subca"]:
                if subca["nickname"] == profile_nickname:
                    return subca
    return None


def parse_ca(data):
    """Returns a list of CA data from the conf data."""
    ca = []

    # check for ca data
    if not "ca" in data:
        raise ValueError("missing ca data")

    if not type(data["ca"]) is list:
        raise ValueError("ca data is not a list")

    if len(data["ca"]) < 1:
        raise ValueError("ca data is missing at least one ca")

    # make sure every ca has at least a nickname and common name
    for ca_data in data["ca"]:
        ca_entry = {}

        # check nickname
        if not "nickname" in ca_data:
            raise ValueError("ca is missing nickname")
        elif not valid_nickname(ca_data["nickname"]):
            raise ValueError("ca nickname '{}' has invalid characters".format(ca_data["nickname"]))
        else:
            ca_entry["nickname"] = ca_data["nickname"]

        # check cn
        if not "cn" in ca_data:
            raise ValueError("ca is missing common name (cn)")
        else:
            ca_entry["cn"] = ca_data["cn"]

        # check rest of the name
        if "o" in ca_data:
            ca_entry["o"] = ca_data["o"]

        if "ou" in ca_data:
            ca_entry["ou"] = ca_data["ou"]

        # check for validity
        if "validity" in ca_data:
            if ca_data["validity"] < 1:
                raise ValueError("ca validity of '{}' is not at least 1 day".format(ca_data["validity"]))
            else:
                ca_entry["validity"] = ca_data["validity"]
        else:
            ca_entry["validity"] = 365 * 5

        # check for crl validity
        if "crl_validity" in ca_data:
            if ca_data["crl_validity"] < 1:
                raise ValueError("ca crl validity of '{}' is not at least 1 day".format(ca_data["crl_validity"]))
            else:
                ca_entry["crl_validity"] = ca_data["crl_validity"]
        else:
            ca_entry["crl_validity"] = 365

        # check for keysize
        if "keysize" in ca_data:
            if not ca_data["keysize"] in (2048, 4096):
                raise ValueError("ca keysize of '{}' is not valid".format(ca_data["keysize"]))
            else:
                ca_entry["keysize"] = ca_data["keysize"]
        else:
            ca_entry["keysize"] = 4096

        # check for subca
        subca = parse_subca(ca_data)
        if subca:
            ca_entry["subca"] = subca

        # check for cert
        cert = parse_cert(ca_data)
        if cert:
            ca_entry["cert"] = cert

        ca.append(ca_entry)

    return ca


def parse_subca(data):
    """Returns a list of Sub CA data from the CA entry data."""
    sub = []

    # check for subca data
    if not "subca" in data:
        return None

    if not type(data["subca"]) is list:
        raise ValueError("sub ca in '{}' is not a list".format(data["nickname"]))

    if len(data["subca"]) < 1:
        return None

    # make sure every Sub ca has at least a nickname and a common name
    for sub_data in data["subca"]:
        sub_entry = {}

        # check nickname
        if not "nickname" in sub_data:
            raise ValueError("sub ca in '{}' is missing nickname".format(data["nickname"]))
        elif not valid_nickname(sub_data["nickname"]):
            raise ValueError("sub ca nickname '{}' has invalid characters".format(sub_data["nickname"]))
        else:
            sub_entry["nickname"] = sub_data["nickname"]

        # check cn
        if not "cn" in sub_data:
            raise ValueError("sub ca in '{}' is missing common name (cn)".format(data["nickname"]))
        else:
            sub_entry["cn"] = sub_data["cn"]

        # check rest
        if "o" in sub_data:
            sub_entry["o"] = sub_data["o"]

        if "ou" in sub_data:
            sub_entry["ou"] = sub_data["ou"]

        # check for validity
        if "validity" in sub_data:
            if sub_data["validity"] < 1:
                raise ValueError("sub ca validity of '{}' is not at least 1 day".format(sub_data["validity"]))
            else:
                sub_entry["validity"] = sub_data["validity"]
        else:
            sub_entry["validity"] = 365 * 5

        # check for crl validity
        if "crl_validity" in sub_data:
            if sub_data["crl_validity"] < 1:
                raise ValueError("sub ca crl validity '{}' is not at least 1 day".format(sub_data["crl_validity"]))
            else:
                sub_entry["crl_validity"] = sub_data["crl_validity"]
        else:
            sub_entry["crl_validity"] = 365

        # check for keysize
        if "keysize" in sub_data:
            if not sub_data["keysize"] in (2048, 4096):
                raise ValueError("sub ca keysize of '{}' is not valid".format(sub_data["keysize"]))
            else:
                sub_entry["keysize"] = sub_data["keysize"]
        else:
            sub_entry["keysize"] = 4096

        # check for cert
        cert = parse_cert(sub_data)
        if cert:
            sub_entry["cert"] = cert

        sub.append(sub_entry)

    return sub


def parse_cert(data):
    """Returns a list of cert data from the conf data."""
    entities = []

    # check for cert data
    if not "cert" in data:
        return None

    if not type(data["cert"]) is list:
        raise ValueError("cert within '{}' is not a list".format(data["nickname"]))

    if len(data["cert"]) < 1:
        return None

    # make sure every cert has at least a nickname
    for cert_data in data["cert"]:
        cert_entry = {}

        # check nickname
        if not "nickname" in cert_data:
            raise ValueError("cert within '{}' is missing nickname".format(data["nickname"]))
        elif not valid_nickname(cert_data["nickname"]):
            raise ValueError("cert nickname '{}' has invalid characters".format(cert_data["nickname"]))
        else:
            cert_entry["nickname"] = cert_data["nickname"]

        # check rest
        if "o" in cert_data:
            cert_entry["o"] = cert_data["o"]

        if "ou" in cert_data:
            cert_entry["ou"] = cert_data["ou"]

        # check for validity
        if "validity" in cert_data:
            if cert_data["validity"] < 1:
                raise ValueError("cert validity of '{}' is not at least 1 day".format(cert_data["validity"]))
            else:
                cert_entry["validity"] = cert_data["validity"]
        else:
            cert_entry["validity"] = 365

        # check for keysize
        if "keysize" in cert_data:
            if not cert_data["keysize"] in (2048, 4096):
                raise ValueError("cert keysize of '{}' is not valid".format(cert_data["keysize"]))
            else:
                cert_entry["keysize"] = cert_data["keysize"]
        else:
            cert_entry["keysize"] = 4096

        entities.append(cert_entry)

    return entities


def parse_logging(data):
    """Returns a logging dict from conf data."""
    logging = {}

    # check for logging data
    if "logging" in data:
        # check if level is specified and valid
        if "level" in data["logging"]:
            if not data["logging"]["level"] in ["debug", "info", "warning", "error"]:
                raise ValueError("logging level '{}' is invalid".format(data["logging"]["level"]))
            else:
                logging["level"] = data["logging"]["level"]
        # use default level
        else:
            logging["level"] = "error"

        # check if handler is specified and valid
        if "handler" in data["logging"]:
            if not data["logging"]["handler"] in ["file", "syslog"]:
                raise ValueError("logging handler '{}' is invalid".format(data["logging"]["handler"]))
            else:
                logging["handler"] = data["logging"]["handler"]
        # use default handler
        else:
            logging["handler"] = "syslog"

        # check filename for file handler
        if "file" in logging["handler"]:
            if not "filename" in data["logging"]:
                raise ValueError("log filename is missing")
            else:
                logging["filename"] = data["logging"]["filename"]

    # set default logging
    else:
        logging = {"level": "error", "handler": "syslog"}

    return logging


def check_unique_nicknames(conf):
    """Raises a ValueError if any nickname is used more than once."""
    nicks = []

    for ca in conf["ca"]:
        # check the ca level
        if ca["nickname"] in nicks:
            raise ValueError("nickname '{}' is used more than once".format(ca["nickname"]))
        else:
            nicks.append(ca["nickname"])

        # check cert under ca
        if "cert" in ca:
            for cert in ca["cert"]:
                if cert["nickname"] in nicks:
                    raise ValueError("nickname '{}' is used more than once".format(ca["nickname"]))
                else:
                    nicks.append(cert["nickname"])

        # check the subca level
        if "subca" in ca:
            for sub in ca["subca"]:
                if sub["nickname"] in nicks:
                    raise ValueError("nickname '{}' is used more than once".format(sub["nickname"]))
                else:
                    nicks.append(sub["nickname"])

                # check cert under subca
                if "cert" in sub:
                    for cert in sub["cert"]:
                        if cert["nickname"] in nicks:
                            raise ValueError("nickname '{}' is used more than once".format(ca["nickname"]))
                        else:
                            nicks.append(cert["nickname"])

    # if we get here, no exceptions were raised so just carry on
    return None


def valid_nickname(nickname):
    """Returns True iff the nickname is valid."""
    # __tracked__ is a reserved profile name
    if nickname == "__tracked__":
        return False
    else:
        return re.search(r"^[a-zA-Z0-9_]+$", nickname)
