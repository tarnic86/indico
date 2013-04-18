# -*- coding: utf-8 -*-
##
##
## This file is part of Indico.
## Copyright (C) 2002 - 2013 European Organization for Nuclear Research (CERN).
##
## Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico;if not, see <http://www.gnu.org/licenses/>.
from collections import OrderedDict
from indico.tests.python.unit.util import IndicoTestCase
import indico.util.redis.avatar_links as avatar_links


class MockEvent(object):
    def __init__(self, eid, start_date):
        self.id = str(eid)
        self.start_date = start_date

    def getId(self):
        return self.id

    def getUnixStartDate(self):
        return self.start_date


class MockAvatar(object):
    def __init__(self, aid):
        self.id = str(aid)
        self.linkedTo = {'conference': {'manager': [],
                                        'participant': []}}

    def getId(self):
        return self.id


class TestLinks(IndicoTestCase):
    _requires = ['redis.Redis']

    def _createDummies(self):
        self._avatar1 = MockAvatar(1)
        self._avatar2 = MockAvatar(2)
        self._event1 = MockEvent(1, 100000)
        self._event2 = MockEvent(2,  50000)
        self._event3 = MockEvent(3, 200000)
        self._event4 = MockEvent(4, 150000)

        self._avatar1.linkedTo['conference']['manager'] += [self._event3, self._event4]
        self._avatar1.linkedTo['conference']['participant'] += [self._event1, self._event2, self._event4]
        self._avatar2.linkedTo['conference']['manager'] += [self._event1, self._event3, self._event4]

    def testImport(self):
        self.assertFalse(self._redis.keys())
        self._createDummies()

        avatar_links.init_links(self._redis, self._avatar1)
        self.assertEqual(frozenset(self._redis.keys()),
                         frozenset(['avatar-event-links/avatar_events:1', 'avatar-event-links/event_avatars:2',
                                    'avatar-event-links/event_avatars:3', 'avatar-event-links/event_avatars:1',
                                    'avatar-event-links/event_avatars:4', 'avatar-event-links/avatar_event_roles:1:4',
                                    'avatar-event-links/avatar_event_roles:1:3',
                                    'avatar-event-links/avatar_event_roles:1:2',
                                    'avatar-event-links/avatar_event_roles:1:1']))

        avatar_links.init_links(self._redis, self._avatar2)
        self.assertEqual(frozenset(self._redis.keys()),
                         frozenset(['avatar-event-links/avatar_events:1', 'avatar-event-links/avatar_events:2',
                                    'avatar-event-links/event_avatars:2', 'avatar-event-links/event_avatars:3',
                                    'avatar-event-links/event_avatars:1', 'avatar-event-links/event_avatars:4',
                                    'avatar-event-links/avatar_event_roles:1:4',
                                    'avatar-event-links/avatar_event_roles:1:3',
                                    'avatar-event-links/avatar_event_roles:1:2',
                                    'avatar-event-links/avatar_event_roles:1:1',
                                    'avatar-event-links/avatar_event_roles:2:4',
                                    'avatar-event-links/avatar_event_roles:2:3',
                                    'avatar-event-links/avatar_event_roles:2:1']))

        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('1', set(['conference_participant'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))

        self.assertEqual(avatar_links.get_links(self._redis, self._avatar2),
                         OrderedDict([('1', set(['conference_manager'])),
                                      ('4', set(['conference_manager'])),
                                      ('3', set(['conference_manager']))]))

    def testLinkModificationsOnlyAffectCorrectAvatar(self):
        self._createDummies()
        avatar_links.init_links(self._redis, self._avatar1)
        avatar_links.init_links(self._redis, self._avatar2)

        # No change may touch other avatars
        links = avatar_links.get_links(self._redis, self._avatar2)
        avatar_links.add_link(self._redis, self._avatar1, self._event1, 'foo')
        self.assertEqual(links, avatar_links.get_links(self._redis, self._avatar2))
        avatar_links.del_link(self._redis, self._avatar1, self._event4, 'conference_manager')
        self.assertEqual(links, avatar_links.get_links(self._redis, self._avatar2))
        avatar_links.del_link(self._redis, self._avatar1, self._event4, 'conference_participant')
        self.assertEqual(links, avatar_links.get_links(self._redis, self._avatar2))
        avatar_links.delete_avatar(self._redis, self._avatar1)
        self.assertEqual(links, avatar_links.get_links(self._redis, self._avatar2))

    def testDeleteAvatar(self):
        self._createDummies()
        avatar_links.init_links(self._redis, self._avatar1)
        keys = frozenset(self._redis.keys())
        links = avatar_links.get_links(self._redis, self._avatar1)
        avatar_links.init_links(self._redis, self._avatar2)
        avatar_links.delete_avatar(self._redis, self._avatar2)
        self.assertEqual(keys, frozenset(self._redis.keys()))
        self.assertEqual(links, avatar_links.get_links(self._redis, self._avatar1))

    def testMergeAvatars(self):
        self._createDummies()
        avatar_links.init_links(self._redis, self._avatar1)
        keys = frozenset(self._redis.keys())
        avatar_links.init_links(self._redis, self._avatar2)
        avatar_links.merge_avatars(self._redis, self._avatar1, self._avatar2)
        self.assertEqual(keys, frozenset(self._redis.keys()))
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar2), OrderedDict())
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('1', set(['conference_manager', 'conference_participant'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))

    def testModifyLinks(self):
        self._createDummies()
        avatar_links.init_links(self._redis, self._avatar1)
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('1', set(['conference_participant'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))
        # Add a new role for an existing event
        avatar_links.add_link(self._redis, self._avatar1, self._event1, 'conference_manager')
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('1', set(['conference_manager', 'conference_participant'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))
        # Delete a role from an event with multiple roles
        avatar_links.del_link(self._redis, self._avatar1, self._event1, 'conference_participant')
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('1', set(['conference_manager'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))
        # Delete a role from an event with just one role
        avatar_links.del_link(self._redis, self._avatar1, self._event1, 'conference_manager')
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))
        # Add a role for a new event
        avatar_links.add_link(self._redis, self._avatar1, self._event1, 'conference_manager')
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('1', set(['conference_manager'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))

    def testModifyEvent(self):
        self._createDummies()
        avatar_links.init_links(self._redis, self._avatar1)
        avatar_links.init_links(self._redis, self._avatar2)

        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('1', set(['conference_participant'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar2),
                         OrderedDict([('1', set(['conference_manager'])),
                                      ('4', set(['conference_manager'])),
                                      ('3', set(['conference_manager']))]))

        # Delete whole event
        avatar_links.delete_event(self._redis, self._event1)
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('4', set(['conference_manager', 'conference_participant'])),
                                      ('3', set(['conference_manager']))]))
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar2),
                         OrderedDict([('4', set(['conference_manager'])),
                                      ('3', set(['conference_manager']))]))

        # Modify event start time so the order changes
        self._event4.start_date = self._event3.start_date + 10
        avatar_links.update_event_time(self._redis, self._event4)

        self.assertEqual(avatar_links.get_links(self._redis, self._avatar1),
                         OrderedDict([('2', set(['conference_participant'])),
                                      ('3', set(['conference_manager'])),
                                      ('4', set(['conference_manager', 'conference_participant']))]))
        self.assertEqual(avatar_links.get_links(self._redis, self._avatar2),
                         OrderedDict([('3', set(['conference_manager'])),
                                      ('4', set(['conference_manager']))]))