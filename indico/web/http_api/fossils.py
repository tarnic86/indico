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

"""
Basic fossils for data export
"""

from indico.util.fossilize import IFossil, fossilize
from indico.util.fossilize.conversion import Conversion
from MaKaC.webinterface import urlHandlers
from MaKaC.webinterface.linking import RoomLinker
from MaKaC.fossils.conference import ISessionFossil


class IHTTPAPIErrorFossil(IFossil):
    def getMessage(self):
        pass


class IHTTPAPIResultFossil(IFossil):
    def getTS(self):
        pass
    getTS.name = 'ts'

    def getURL(self):
        pass
    getURL.name = 'url'

    def getResults(self):
        pass


class IHTTPAPIExportResultFossil(IHTTPAPIResultFossil):
    def getCount(self):
        pass

    def getComplete(self):
        pass

    def getAdditionalInfo(self):
        pass


class IPeriodFossil(IFossil):
    def startDT(self):
        pass
    startDT.convert = Conversion.datetime

    def endDT(self):
        pass
    endDT.convert = Conversion.datetime


class ICategoryMetadataFossil(IFossil):
    def getId(self):
        pass

    def getName(self):
        pass

    def getLocator(self):
        pass
    getLocator.convert = Conversion.url(urlHandlers.UHCategoryDisplay)
    getLocator.name = 'url'

class ICategoryProtectedMetadataFossil(ICategoryMetadataFossil):
    def getName(self):
        pass
    getName.produce = lambda x: None


class IConferenceChairMetadataFossil(IFossil):

    def getId(self):
        pass

    def getFullName(self):
        pass

    def getEmail(self):
        pass

    def getAffiliation(self):
        pass


class IContributionParticipationMetadataFossil(IFossil):

    def getId(self):
        pass

    def getFullName(self):
        pass

    def getEmail(self):
        pass

    def getAffiliation(self):
        pass


class IResourceMetadataFossil(IFossil):

    def getName(self):
        pass

class ILocalFileMetadataFossil(IResourceMetadataFossil):

    def getId(self):
        pass

    def getURL(self):
        pass
    getURL.produce = lambda s: str(urlHandlers.UHFileAccess.getURL(s))
    getURL.name = 'url'

    def getFileName(self):
        pass


class ILinkMetadataFossil(IResourceMetadataFossil):

    def getURL(self):
        pass
    getURL.name = 'url'

class IMaterialMetadataFossil(IFossil):

    def getId(self):
        pass

    def getTitle( self ):
        pass

    def getResourceList(self):
        pass
    getResourceList.result = {'MaKaC.conference.Link': ILinkMetadataFossil, 'MaKaC.conference.LocalFile': ILocalFileMetadataFossil}
    getResourceList.name = 'resources'
    getResourceList.filterBy = 'access'


class _IncludeMaterialFossil(IFossil):

    def getAllMaterialList(self):
        pass
    getAllMaterialList.name = 'material'
    getAllMaterialList.result = IMaterialMetadataFossil
    getAllMaterialList.filterBy = 'access'


class IConferenceMetadataFossil(_IncludeMaterialFossil, IFossil):

    def getId(self):
        pass

    def getStartDate(self):
        pass
    getStartDate.convert = Conversion.datetime

    def getEndDate(self):
        pass
    getEndDate.convert = Conversion.datetime

    def getTitle(self):
        pass

    def getDescription(self):
        pass

    def getType(self):
        pass

    def getOwner(self):
        pass
    getOwner.convert = lambda x: x.getTitle()
    getOwner.name = 'category'

    def getCategoryId(self):
        pass
    getCategoryId.produce = lambda x: x.getOwner().getId()

    def getTimezone(self):
        pass

    def getChairList(self):
        pass
    getChairList.name = 'chairs'
    getChairList.result = IConferenceChairMetadataFossil

    def getLocation(self):
        """ Location (CERN/...) """
    getLocation.convert = lambda l: l and l.getName()

    def getLocator(self):
        pass
    getLocator.convert = Conversion.url(urlHandlers.UHConferenceDisplay)
    getLocator.name = 'url'

    def getRoom(self):
        """ Room (inside location) """
    getRoom.convert = lambda r: r and r.getName()

    def getVisibility(self):
        pass
    getVisibility.name = 'visibility'
    getVisibility.produce = lambda x: Conversion.visibility(x)

    def hasAnyProtection(self):
        pass

    def getAddress(self):
        pass

    def getModificationDate(self):
        pass

    def getRoomMapURL(self):
        pass
    getRoomMapURL.produce = lambda x: RoomLinker().getURL(x.getRoom(), x.getLocation())


class IContributionMetadataFossil(_IncludeMaterialFossil, IFossil):

    def getId(self):
        pass

    def getTitle(self):
        pass

    def getLocation(self):
        pass
    getLocation.convert = lambda l: l and l.getName()

    def getRoom(self):
        pass
    getRoom.convert = lambda r: r and r.getName()

    def getStartDate(self):
        pass
    getStartDate.convert = Conversion.datetime

    def getEndDate(self):
        pass
    getEndDate.convert = Conversion.datetime

    def getDuration(self):
        pass
    getDuration.convert = Conversion.duration

    def getDescription(self):
        pass

    def getSpeakerList(self):
        pass
    getSpeakerList.name = 'speakers'
    getSpeakerList.result = IContributionParticipationMetadataFossil

    def getPrimaryAuthorList(self):
        pass
    getPrimaryAuthorList.name = 'primaryauthors'
    getPrimaryAuthorList.result = IContributionParticipationMetadataFossil

    def getCoAuthorList(self):
        pass
    getCoAuthorList.name = 'coauthors'
    getCoAuthorList.result = IContributionParticipationMetadataFossil

    def getTrack( self ):
        pass
    getTrack.convert = lambda t: t and t.getTitle()

    def getSession( self ):
        pass
    getSession.convert = lambda s: s and s.getTitle()

    def getType(self):
        pass
    getType.convert = lambda t: t and t.getName()

    def getLocator(self):
        pass
    getLocator.convert = Conversion.url(urlHandlers.UHContributionDisplay)
    getLocator.name = 'url'


class ISubContributionMetadataFossil(IFossil):

    def getId(self):
        pass

    def getTitle(self):
        pass

    def getDuration(self):
        pass
    getDuration.convert = Conversion.duration

    def getSpeakerList(self):
        pass
    getSpeakerList.name = 'speakers'
    getSpeakerList.result = IContributionParticipationMetadataFossil


class IContributionMetadataWithSubContribsFossil(IContributionMetadataFossil):

    def getSubContributionList(self):
        pass
    getSubContributionList.result = ISubContributionMetadataFossil
    getSubContributionList.name = 'subContributions'


class IConferenceMetadataWithContribsFossil(_IncludeMaterialFossil, IConferenceMetadataFossil):

    def getContributionList(self):
        pass
    getContributionList.result = IContributionMetadataFossil
    getContributionList.name = 'contributions'
    getContributionList.filterBy = 'access'


class IConferenceMetadataWithSubContribsFossil(_IncludeMaterialFossil, IConferenceMetadataFossil):

    def getContributionList(self):
        pass
    getContributionList.result = IContributionMetadataWithSubContribsFossil
    getContributionList.name = 'contributions'
    getContributionList.filterBy = 'access'


class ISessionMetadataFossil(ISessionFossil):

    def getContributionList(self):
        pass
    getContributionList.result = IContributionMetadataWithSubContribsFossil
    getContributionList.name = 'contributions'
    getContributionList.filterBy = 'access'


class ISessionMetadataWithContributionsFossil(ISessionFossil):

    def getContributionList(self):
        pass
    getContributionList.result = IContributionMetadataFossil
    getContributionList.name = 'contributions'
    getContributionList.filterBy = 'access'

class ISessionMetadataWithSubContribsFossil(ISessionFossil):

    def getContributionList(self):
        pass
    getContributionList.result = IContributionMetadataWithSubContribsFossil
    getContributionList.name = 'subcontributions'
    getContributionList.filterBy = 'access'

class IConferenceMetadataWithSessionsFossil(_IncludeMaterialFossil, IConferenceMetadataFossil):

    def getSessionList(self):
        pass
    getSessionList.result = ISessionMetadataFossil
    getSessionList.name = 'sessions'
    getSessionList.filterBy = 'access'

    def getContributionListWithoutSessions(self):
        pass
    getContributionListWithoutSessions.result = IContributionMetadataWithSubContribsFossil
    getContributionListWithoutSessions.name = 'contributions'
    getContributionListWithoutSessions.filterBy = 'access'


class IBasicConferenceMetadataFossil(IFossil):

    def getId(self):
        pass

    def getStartDate(self):
        pass
    getStartDate.convert = Conversion.datetime

    def getEndDate(self):
        pass
    getEndDate.convert = Conversion.datetime

    def getTitle(self):
        pass

    def getType(self):
        pass

    def getOwner(self):
        pass
    getOwner.convert = lambda x: x.getTitle()
    getOwner.name = 'category'

    def getCategoryId(self):
        pass
    getCategoryId.produce = lambda x: x.getOwner().getId()

    def getLocator(self):
        pass
    getLocator.convert = Conversion.url(urlHandlers.UHConferenceDisplay)
    getLocator.name = 'url'