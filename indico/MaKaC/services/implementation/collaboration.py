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

from pytz import timezone
from datetime import timedelta, date, time, datetime
from MaKaC.services.implementation.base import ParameterManager, AdminService
from MaKaC.services.interface.rpc.common import NoReportError
from MaKaC.services.implementation.conference import ConferenceModifBase
from MaKaC.plugins.Collaboration.base import CollaborationException, CollaborationServiceException
from MaKaC.webinterface.rh.collaboration import RCCollaborationAdmin,\
    RCCollaborationPluginAdmin, RCVideoServicesManager, RCVideoServicesUser
from MaKaC.i18n import _
from MaKaC.common.indexes import IndexesHolder
from MaKaC.plugins import PluginsHolder
from MaKaC.common.timezoneUtils import nowutc, setAdjustedDate
from MaKaC.common.utils import parseDateTime
from MaKaC.plugins.Collaboration.collaborationTools import CollaborationTools
from MaKaC.webinterface.user import UserListModificationBase,\
    UserModificationBase
from MaKaC.common.fossilize import fossilize



## Base classes
class CollaborationBase(ConferenceModifBase):
    """ This base class stores the _CSBookingManager attribute
        so that inheriting classes can use it.
    """
    def _checkParams(self):
        ConferenceModifBase._checkParams(self) #sets self._target = self._conf = the Conference object
        self._checkCollaborationEnabled()
        self._CSBookingManager = self._conf.getCSBookingManager()

    def _checkCollaborationEnabled(self):
        """ Checks if the Collaboration plugin system is active
        """
        if not PluginsHolder().hasPluginType("Collaboration"):
            raise CollaborationServiceException("Collaboration plugin system is not active")

    def _checkCanManagePlugin(self, plugin):
        isAdminOnlyPlugin = CollaborationTools.isAdminOnlyPlugin(plugin)

        hasAdminRights = RCCollaborationAdmin.hasRights(self) or \
                         RCCollaborationPluginAdmin.hasRights(self, None, [plugin])

        if not hasAdminRights and isAdminOnlyPlugin:
            raise CollaborationException(_("Cannot acces service of admin-only plugin if user is not admin, for event: ") + str(self._conf.getId()) + _(" with the service ") + str(self.__class__) )

        elif not hasAdminRights and not RCVideoServicesManager.hasRights(self, [plugin]):
            #we check if it's an event creator / manager (this will call ConferenceModifBase._checkProtection)
            CollaborationBase._checkProtection(self)

    def process(self):
        try:
            return ConferenceModifBase.process(self)
        except CollaborationException, e:
            raise CollaborationServiceException(e.getMsg(), str(e.getInner()))

class CollaborationBookingModifBase(CollaborationBase):
    """ Base class for services that are passed a booking id.
        It is stored in self._bookingId
    """
    def _checkParams(self):
        CollaborationBase._checkParams(self)
        if self._params.has_key('bookingId'):
            self._bookingId = self._params['bookingId']
            self._booking = self._CSBookingManager.getBooking(self._bookingId)
            if self._booking == None:
                raise NoReportError(_("The booking that you are trying to modify does not exist. Maybe it was already deleted, please refresh the page."))

            self._bookingType = self._booking.getType()
            self._bookingPlugin = self._booking.getPlugin()
            self._pm = ParameterManager(self._params)
        else:
            raise CollaborationException(_("Booking id not set when trying to modify a booking on meeting ") + str(self._conf.getId()) + _(" with the service ") + str(self.__class__) )

    def _checkProtection(self):
        CollaborationBase._checkCanManagePlugin(self, self._bookingType)

class CollaborationAdminBookingModifBase(CollaborationBookingModifBase):
    """ Base class for services on booking objects that can only be requested by Server Admins,
        Video Services Admins, or Plugin admins, such as accept or reject a request, etc.
    """

    def _checkProtection(self):
        if not RCCollaborationAdmin.hasRights(self) and not RCCollaborationPluginAdmin.hasRights(self, None, [self._bookingPlugin]):
            raise CollaborationException(_("You don't have the rights to perform this operation on this booking"))

class AdminCollaborationBase(AdminService):
    """ Base class for admin services in the Video Services Overview page, not directed towards a specific booking.
    """

    def _checkParams(self):
        AdminService._checkParams(self)
        if not PluginsHolder().hasPluginType("Collaboration"):
            raise CollaborationServiceException(_("Collaboration plugin system is not active"))

    def _checkProtection(self):
        if not RCCollaborationAdmin.hasRights(self, None):
            AdminService._checkProtection(self)

##! End of base classes

class CollaborationBookingModif(CollaborationBookingModifBase):
    """ Specific to check the authorised users and groups creating, editing and removing.
        It is different to CollaborationBookingModifBase because:
        * CollaborationBookingModif: people that can create, edit, remove
        * CollaborationBookingModifBase: people that can start, stop, sync, etc
    """
    def _checkProtection(self):
        CollaborationBookingModifBase._checkProtection(self)
        if not RCVideoServicesUser.hasRights(self, None, self._bookingType):
            raise CollaborationException(_("You dot have access to modify a %s booking")%self._bookingType)

class CollaborationCreateCSBookingBase(CollaborationBase, CollaborationBookingModif):
    def _checkParams(self):
        CollaborationBase._checkParams(self)

        if 'type' in self._params:
            self._bookingType = self._params['type']
        else:
            raise CollaborationException(_("type parameter not set when trying to create a booking on meeting ") + str(self._conf.getId() ))

        if 'bookingParams' in self._params:
            pm = ParameterManager(self._params)
            self._bookingParams = pm.extract("bookingParams", pType=dict, allowEmpty = True)
        else:
            raise CollaborationException(_("Custom parameters for plugin ") + str(self._type) + _(" not set when trying to create a booking on meeting ") + str(self._conf.getId() ))

    def _checkProtection(self):
        CollaborationBookingModif._checkProtection(self)

class CollaborationCreateCSBooking(CollaborationCreateCSBookingBase):
    """ Adds a new booking
    """

    def _getAnswer(self):
        return fossilize(self._CSBookingManager.createBooking(self._bookingType, bookingParams = self._bookingParams),
                         None, tz = self._conf.getTimezone())

class CollaborationAttachCSBooking(CollaborationCreateCSBookingBase):
    """ Attach an new booking
    """

    def _getAnswer(self):
        return fossilize(self._CSBookingManager.attachBooking(self._bookingType, bookingParams = self._bookingParams),
                         None, tz = self._conf.getTimezone())

class CollaborationRemoveCSBooking(CollaborationBookingModif):
    """ Removes a booking
    """

    def _getAnswer(self):
        return fossilize(self._CSBookingManager.removeBooking(self._bookingId),
                         None, tz = self._conf.getTimezone())


class CollaborationEditCSBooking(CollaborationBookingModif):
    """ Edits a booking
    """
    def _checkParams(self):
        CollaborationBookingModif._checkParams(self)

        if self._params.has_key('bookingParams'):
            pm = ParameterManager(self._params)
            self._bookingParams = pm.extract("bookingParams", pType=dict, allowEmpty = True)
        else:
            raise CollaborationException(_("Custom parameters for booking ") + str(self._bookingId) + _(" not set when trying to edit a booking on meeting ") + str(self._conf.getId() ))

    def _getAnswer(self):
        return fossilize(self._CSBookingManager.changeBooking(self._bookingId, self._bookingParams),
                         None, tz = self._conf.getTimezone())


class CollaborationStartCSBooking(CollaborationBookingModifBase):
    """ Performs server-side actions when a booking is started
    """
    def _getAnswer(self):
        return fossilize(self._CSBookingManager.startBooking(self._bookingId),
                         None, tz = self._conf.getTimezone())

class CollaborationStopCSBooking(CollaborationBookingModifBase):
    """ Performs server-side actions when a booking is stopped
    """
    def _getAnswer(self):
        return fossilize(self._CSBookingManager.stopBooking(self._bookingId),
                                  timezone = self._conf.getTimezone())

class CollaborationCheckCSBookingStatus(CollaborationBookingModifBase):
    """ Performs server-side actions when a booking's status is checked
    """
    def _getAnswer(self):
        return fossilize(self._CSBookingManager.checkBookingStatus(self._bookingId),
                         None, tz = self._conf.getTimezone())

class CollaborationAcceptCSBooking(CollaborationAdminBookingModifBase):
    """ Performs server-side actions when a booking / request is accepted
    """
    def _getAnswer(self):
        return fossilize(self._CSBookingManager.acceptBooking(self._bookingId, self.getAW().getUser()),
                                  None, tz = self._conf.getTimezone())

class CollaborationRejectCSBooking(CollaborationAdminBookingModifBase):
    """ Performs server-side actions when a booking / request is rejected
    """
    def _checkParams(self):
        CollaborationAdminBookingModifBase._checkParams(self)
        self._reason = self._params.get("reason", "")

    def _getAnswer(self):
        return fossilize(self._CSBookingManager.rejectBooking(self._bookingId, self._reason),
                                  None, tz = self._conf.getTimezone())

class CollaborationChangePluginManagersBase(CollaborationBase):
    """ Base class for adding and removing plugin managers in an event
        self._plugin will be a string with the plugin name.
    """

    def _checkParams(self):
        CollaborationBase._checkParams(self)
        if self._params.has_key('plugin'):
            self._plugin = self._params['plugin']
        else:
            raise CollaborationException(_("Plugin name not set when trying to add or remove a manager on event: ") + str(self._conf.getId()) + _(" with the service ") + str(self.__class__) )

        if CollaborationTools.getCollaborationPluginType().hasPlugin(self._plugin) and CollaborationTools.isAdminOnlyPlugin(self._plugin):
            raise CollaborationException(_("Tried to add or remove a manager for an admin-only plugin on event : ") + str(self._conf.getId()) + _(" with the service ") + str(self.__class__) )

    def _checkProtection(self):
        if not RCVideoServicesManager.hasRights(self):
            CollaborationBase._checkProtection(self)

class CollaborationAddPluginManager(CollaborationChangePluginManagersBase, UserListModificationBase):
    """ Adds a user as Plugin Manager for an event and plugin
    """

    def _checkParams(self):
        CollaborationChangePluginManagersBase._checkParams(self)
        UserListModificationBase._checkParams(self)

    def _getAnswer(self):
        existingManagerIds = set([u.getId() for u in self._CSBookingManager.getPluginManagers(self._plugin)])
        for u in self._avatars:
            if not u.getId() in existingManagerIds:
                self._CSBookingManager.addPluginManager(self._plugin, u)

        return True


class CollaborationRemovePluginManager(CollaborationChangePluginManagersBase, UserModificationBase):
    """ Removes a user as Plugin Manager for an event and plugin
    """

    def _checkParams(self):
        CollaborationChangePluginManagersBase._checkParams(self)
        UserModificationBase._checkParams(self)

    def _getAnswer(self):
        self._CSBookingManager.removePluginManager(self._plugin, self._targetUser)
        return True


class CollaborationBookingIndexQuery(AdminCollaborationBase):
    """ Performs a query to the Collaboration index of bookings / request objects.
    """

    def _checkProtection(self):
        if not RCCollaborationPluginAdmin.hasRights(self, None, "any"):
            AdminCollaborationBase._checkProtection(self)

    def _checkParams(self):
        AdminCollaborationBase._checkParams(self)
        user = self.getAW().getUser()
        pm = ParameterManager(self._params)

        if user: #someone is logged in. if not, AdminCollaborationBase's _checkProtection will take care of it
            self._tz = user.getTimezone()

            try:
                self._page = self._params.get("page", None)
                self._resultsPerPage = self._params.get("resultsPerPage", None)
                self._indexName = self._params['indexName']
                self._viewBy = self._params['viewBy']
                self._orderBy = self._params['orderBy']

                if self._indexName in ['RecordingRequest', 'WebcastRequest', 'All Requests'] and self._viewBy == 'startDate':
                    self._viewBy = 'instanceDate'

                minKey = None
                maxKey = None

                if self._params['sinceDate']:
                    minKey = timezone(self._tz).localize(datetime.combine(pm.extract("sinceDate", pType=date, allowEmpty=True), time(0, 0)))
                if self._params['toDate']:
                    maxKey = timezone(self._tz).localize(datetime.combine(pm.extract("toDate", pType=date, allowEmpty=True), time(23, 59, 59)))
                if self._params['fromTitle']:
                    minKey = self._params['fromTitle'].strip()
                if self._params['toTitle']:
                    maxKey = self._params['toTitle'].strip()

                """ For relative dates, create a diff timedelta for resetting to
                    00:00 at the start of range and 23:59 at the end.
                """
                if self._params['fromDays']:
                    try:
                        fromDays = int(self._params['fromDays'])
                    except ValueError, e:
                        raise CollaborationException(_("Parameter 'fromDays' is not an integer"), inner = e)
                    midnight = nowutc().replace(hour=0, minute=0, second=0)
                    minKey = midnight - timedelta(days = fromDays)
                if self._params['toDays']:
                    try:
                        toDays = int(self._params['toDays'])
                    except ValueError, e:
                        raise CollaborationException(_("Parameter 'toDays' is not an integer"), inner = e)
                    midnight_1 = nowutc().replace(hour=23, minute=59, second=59)
                    maxKey = midnight_1 + timedelta(days = toDays)

                self._minKey = minKey
                self._maxKey = maxKey

                self._onlyPending = self._params['onlyPending']
                categoryId = self._params['categoryId'].strip()
                if categoryId:
                    self._categoryId = categoryId
                else:
                    self._categoryId = None
                conferenceId = self._params['conferenceId'].strip()
                if conferenceId:
                    self._conferenceId = conferenceId
                else:
                    self._conferenceId = None

            except KeyError, e:
                raise CollaborationException(_("One of the necessary parameters to query the booking index is missing"), inner = e)

    def _getAnswer(self):
        ci = IndexesHolder().getById('collaboration')
        return ci.getBookings(self._indexName,
                              self._viewBy,
                              self._orderBy,
                              self._minKey,
                              self._maxKey,
                              tz = self._tz,
                              onlyPending = self._onlyPending,
                              conferenceId = self._conferenceId,
                              categoryId = self._categoryId,
                              pickle = True,
                              dateFormat='%a %d %b %Y',
                              page = self._page,
                              resultsPerPage = self._resultsPerPage,
                              grouped=True)

class CollaborationCustomPluginService(CollaborationBase):
    """ Class to support plugin-defined services.
        Plugins have to call 'collaboration.pluginService' and
        specify a 'plugin' and 'service' arguments.
        Then they have to create a class that inherits from
        CollaborationPluginServiceBase with the same name
        as the 'service' argument, plus 'Service' at the end.
        The classes can have _checkParams, _checkProtetion methods,
        and must have a _getAnswer method.
        They will have the following attributes available:
        _params, _aw, _conf, _target, _CSBookingManager.
    """

    def _checkParams(self):
        CollaborationBase._checkParams(self)

        self._pluginName = self._params.get('plugin', None)
        if not self._pluginName:
            raise CollaborationException(_("No 'plugin' paramater in CollaborationPluginService"))

        serviceName = self._params.get('service', None)
        if not serviceName:
            raise CollaborationException(_("No 'service' paramater in CollaborationPluginService"))

        self._serviceClass = CollaborationTools.getServiceClass(self._pluginName, serviceName)
        if not self._serviceClass:
            raise CollaborationException(_("Service " + str(serviceName) + _("Service not found for plugin ") + str(self._pluginName) + _("in CollaborationPluginService")))

    def _checkProtection(self):
        CollaborationBase._checkCanManagePlugin(self, self._pluginName)

    def _getAnswer(self):
        serviceObject = self._serviceClass(self._params, self._aw)
        serviceObject._checkParams()
        serviceObject._checkProtection()
        return serviceObject._getAnswer()


class CollaborationPluginServiceBase(CollaborationBase):
    """ Base class that plugin-defined services need to inherit from.
        The _params and _aw attributes will be available for them,
        and also _target and _conf and _CSBookingManager from CollaborationBase.
        If they implement a _checkParams method, they need to call
        their parent's (this class's) method first.
        This class _checkParam method calls CollaborationBase's
    """

    def __init__(self, params, aw):
        self._params = params
        self._aw = aw

    def _checkParams(self):
        CollaborationBase._checkParams(self)

    def _checkProtection(self):
        pass

    def _getAnswer(self):
        raise CollaborationException("No answer was returned")

class CollaborationPluginServiceBookingModifBase(CollaborationPluginServiceBase):

    def __init__(self, params, aw):
        CollaborationPluginServiceBase.__init__(self, params, aw)
        self._booking = None

    def _checkParams(self):
        CollaborationPluginServiceBase._checkParams(self)
        bookingId = self._params.get("booking", None)
        if bookingId:
            self._booking = self._CSBookingManager.getBooking(bookingId)
        else:
            raise CollaborationException(_("Service " + str(self.__class__.__name__) + _(" was called without a 'booking' parameter ")))


class CollaborationCreateTestCSBooking(CollaborationCreateCSBooking):
    """ Service that creates a 'test' booking for performance test.
        Avoids to use any of the plugins except DummyPlugin
    """
    def _checkParams(self):
        CollaborationBase._checkParams(self)

        if 'bookingParams' in self._params:
            pm = ParameterManager(self._params)
            self._bookingParams = pm.extract("bookingParams", pType=dict, allowEmpty = True)
        else:
            raise CollaborationException(_("Custom parameters for plugin ") + str(self._type) + _(" not set when trying to create a booking on meeting ") + str(self._conf.getId() ))

    def _getAnswer(self):
        return fossilize(self._CSBookingManager.createTestBooking(bookingParams = self._bookingParams),
                         None, tz = self._conf.getTimezone())

class CollaborationMakeMeModeratorCSBooking(CollaborationBookingModifBase):
    """ Service that creates a 'test' booking for performance test.
        Avoids to use any of the plugins except DummyPlugin
    """
    def _getAnswer(self):
        return fossilize(self._CSBookingManager.makeMeModeratorBooking(self._bookingId, fossilize(self.getAW().getUser())),
                                  None, tz = self._conf.getTimezone())


methodMap = {
    "createCSBooking": CollaborationCreateCSBooking,
    "attachCSBooking": CollaborationAttachCSBooking,
    "removeCSBooking": CollaborationRemoveCSBooking,
    "editCSBooking": CollaborationEditCSBooking,
    "startCSBooking": CollaborationStartCSBooking,
    "stopCSBooking": CollaborationStopCSBooking,
    "checkCSBookingStatus": CollaborationCheckCSBookingStatus,
    "acceptCSBooking": CollaborationAcceptCSBooking,
    "rejectCSBooking": CollaborationRejectCSBooking,
    "bookingIndexQuery": CollaborationBookingIndexQuery,
    "addPluginManager": CollaborationAddPluginManager,
    "removePluginManager": CollaborationRemovePluginManager,
    "pluginService": CollaborationCustomPluginService,
    "makeMeModerator": CollaborationMakeMeModeratorCSBooking
}
