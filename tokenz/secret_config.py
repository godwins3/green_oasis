from configparser import ConfigParser
import os
from datetime import datetime


def secret_config(filename=os.path.dirname(os.path.abspath(__file__)) + '/tok_config.ini', section='tok'):
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:

        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db


def quickgen_secret_config(filename=os.path.dirname(os.path.abspath(__file__)) + '/tok_config.ini', section='quickgen'):
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:

        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db


def client_id_config(filename=os.path.dirname(os.path.abspath(__file__)) + '/tok_config.ini',
                     section='google_client_id'):
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:

        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db


