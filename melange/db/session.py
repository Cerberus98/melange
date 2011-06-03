# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

_ENGINE = None
_MAKER = None
_MODELS = None

import logging
import contextlib

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import exc
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker

from melange.common import config
from melange.db import mappers


def configure_db(options):
    global _ENGINE, _MODELS
    if not _ENGINE:
        debug = config.get_option(options,
                                  'debug', type='bool', default=False)
        verbose = config.get_option(options,
                                    'verbose', type='bool', default=False)
        timeout = config.get_option(options,
                                  'sql_idle_timeout', type='int', default=3600)
        _ENGINE = create_engine(options['sql_connection'],
                                pool_recycle=timeout)
        logger = logging.getLogger('sqlalchemy.engine')

        mappers.map(_ENGINE, options['models'])

        models = options['models']
        models['ip_nat_relation'] = mappers.IpNat

        _MODELS = models
        if debug:
            logger.setLevel(logging.DEBUG)
        elif verbose:
            logger.setLevel(logging.INFO)


def models():
    global _MODELS
    assert _MODELS
    return _MODELS


def get_session(autocommit=True, expire_on_commit=False):
        """Helper method to grab session"""
        global _MAKER, _ENGINE
        if not _MAKER:
            assert _ENGINE
            _MAKER = sessionmaker(bind=_ENGINE,
                                  autocommit=autocommit,
                                  expire_on_commit=expire_on_commit)
        return _MAKER()


def raw_query(model, autocommit=True, expire_on_commit=False):
    return get_session(autocommit, expire_on_commit).query(model)


def clean_db():
    global _ENGINE
    meta = MetaData()
    meta.reflect(bind=_ENGINE)
    with contextlib.closing(_ENGINE.connect()) as con:
        trans = con.begin()
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()