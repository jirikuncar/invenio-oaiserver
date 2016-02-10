# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.

"""Query parser."""

import pypeg2
from elasticsearch_dsl import Search
from flask import current_app
from invenio_query_parser.walkers.match_unit import MatchUnit
from invenio_records.models import RecordMetadata
from invenio_search import Query as SearchQuery
from invenio_search import current_search_client
from werkzeug.utils import cached_property

from .utils import parser, query_walkers


class Query(SearchQuery):
    """Query object."""

    @cached_property
    def query(self):
        """Parse query string using given grammar."""
        tree = pypeg2.parse(self._query, parser(), whitespace='')
        for walker in query_walkers():
            tree = tree.accept(walker)
        return tree

    def match(self, record):
        """Return True if record match the query."""
        return self.query.accept(MatchUnit(record))


def get_records(**kwargs):
    """Get records."""
    page = kwargs.get('resumptionToken', {}).get('page', 1)
    size = current_app.config['OAISERVER_PAGE_SIZE']
    query = Search().using(current_search_client)
    # index=current_app.config['OAISERVER_RECORD_INDEX'],

    if 'set' in kwargs:
        query = query.query('match', **{'_oai.sets': kwargs['set']})

    time_range = {}
    if 'from_' in kwargs:
        time_range['gte'] = kwargs['from_']
    if 'until' in kwargs:
        time_range['lte'] = kwargs['until']
    if time_range:
        query = query.filter('range', **{'_oai.updated': time_range})

    query = query[(page-1)*size:page*size]

    current_app.logger.info(query.to_dict())

    response = query.execute()

    class Pagination(object):
        """Dummy pagination class."""

        @property
        def has_next(self):
            """Return True if there are more results."""
            return page*size <= response.hits.total

        @property
        def items(self):
            """Return iterator."""
            for result in response:
                yield {
                    'id': result.meta.id,
                    'json': result._d_,
                    'updated': RecordMetadata.query.filter_by(
                        id=result.meta.id).one().updated,
                }

    return Pagination()
