# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Define forms for manipulation of OAI sets."""

from flask_babelex import gettext as _
from flask_wtf import Form
from invenio_db import db
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_alchemy import model_form_factory

from .models import OAISet

ModelForm = model_form_factory(Form)


class OAISetForm(ModelForm):
    """Form for creating and updating an OAISet."""

    @classmethod
    def get_session(self):
        """Get session."""
        return db.session

    class Meta:
        """Form configuration."""

        model = OAISet

    parent = QuerySelectField(
        query_factory=OAISet.query.all,
        get_pk=lambda a: a.spec,
        get_label=lambda a: a.name,
        allow_blank=True,
        blank_text=_('No parent set.'),
    )

__all__ = ('OAISetForm', )
