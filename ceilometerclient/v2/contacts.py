#
# Copyright 2013 Red Hat, Inc
#
# Author:  Frankie Gu <guxf@chinanetcenter.com>

import warnings

from ceilometerclient.common import base
from ceilometerclient.common import utils
from ceilometerclient import exc
from ceilometerclient.v2 import options


UPDATABLE_ATTRIBUTES = [
     'contact_name',
     'contact_phone',
     'contact_email',
     'state',
]
CREATION_ATTRIBUTES = UPDATABLE_ATTRIBUTES + ['project_id', 'user_id',]


class Contact(base.Resource):
    def __repr__(self):
        return "<Contact %s>" % self._info

    def __getattr__(self, k):
        if k == 'id':
            return self.contact_id
        return super(Contact, self).__getattr__(k)

    def delete(self):
        return self.manager.delete(self.contact_id)

    def get_state(self):
        state = self.manager.get_state(self.contact_id)
        return state.get('contact')


class ContactManager(base.Manager):
    resource_class = Contact

    @staticmethod
    def _path(id=None):
        return '/v2/contacts/%s' % id if id else '/v2/contacts'

    def list(self, q=None):
        return self._list(options.build_url(self._path(), q))

    def get(self, contact_id):
        try:
            return self._list(self._path(contact_id), expect_single=True)[0]
        except IndexError:
            return None

        except exc.HTTPNotFound:
            # When we try to get deleted contact HTTPNotFound occurs
            # or when contact doesn't exists this exception don't must
            # go deeper because cleanUp() (method which remove all
            # created things like instance, contact, etc.) at scenario
            # tests doesn't know how to process it
            return None

    def create(self, **kwargs):
        new = dict((key, value) for (key, value) in kwargs.items()
                   if key in CREATION_ATTRIBUTES)
        return self._create(self._path(), new)

    def update(self, contact_id, **kwargs):
        contact = self.get(contact_id)
        if contact is None:
            raise exc.CommandError('Contact not found: %s' % contact_id)
        updated = contact.to_dict()
        kwargs = dict((k, v) for k, v in kwargs.items()
                      if k in updated and k in UPDATABLE_ATTRIBUTES)
        utils.merge_nested_dict(updated, kwargs, depth=1)
        return self._update(self._path(contact_id), updated)

    def delete(self, contact_id):
        return self._delete(self._path(contact_id))

    def set_state(self, contact_id, state):
        body = self.api.put("%s/state" % self._path(contact_id),
                            json=state).json()
        return body

    def get_state(self, contact_id):
        body = self.api.get("%s/state" % self._path(contact_id)).json()
        return body
