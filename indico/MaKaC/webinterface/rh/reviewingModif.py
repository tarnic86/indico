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

import os

from MaKaC.errors import MaKaCError
from MaKaC.webinterface.pages.conferences import WPConferenceModificationClosed
from MaKaC.webinterface.pages.reviewing import WPConfModifReviewingPaperSetup
from MaKaC.webinterface.rh.conferenceBase import RHConferenceBase
from MaKaC.webinterface.rh.conferenceModif import RHConferenceModifBase,\
    RHConferenceModifKey
from MaKaC.webinterface.rh.conferenceDisplay import RHConferenceBaseDisplay
import MaKaC.webinterface.urlHandlers as urlHandlers
from MaKaC.common import Config
from MaKaC.i18n import _
from indico.util import json


class RCPaperReviewManager:
    @staticmethod
    def hasRights(request):
        """ Returns true if the user is a PRM of the conference
        """
        return request._conf.getConfPaperReview().isPaperReviewManager(request.getAW().getUser())


class RCReviewingStaff:
    @staticmethod
    def hasRights(request):
        """ Returns true if the user is a PRM, an AM, a referee, an editor, a reviewer or an abstract reviewer of the conference
        """
        return request._conf.getConfPaperReview().isInReviewingTeam(request.getAW().getUser())

class RCReferee:
    @staticmethod
    def hasRights(request):
        """ Returns true if the user is a referee of the conference
        """
        return request._conf.getConfPaperReview().isReferee(request.getAW().getUser())

class RCEditor:
    @staticmethod
    def hasRights(request):
        """ Returns true if the user is an editor of the conference
        """
        return request._conf.getConfPaperReview().isEditor(request.getAW().getUser())

class RCReviewer:
    @staticmethod
    def hasRights(request):
        """ Returns true if the user is a reviewer of the conference
        """
        return request._conf.getConfPaperReview().isReviewer(request.getAW().getUser())

class RHConfModifReviewingAccess(RHConferenceModifBase):
    """ Class used when the user clicks on the main 'Reviewing' tab
        Depending if the user is PRM or AM, etc. the user will be redirected
        to one of the subtabs of the reviewing tab.
        This is needed because depending on the role of the user,
        they cannot see some of the subtabs and then they need to be
        redirected to the appropiate subtab.
    """

    def _checkParams(self, params):
        RHConferenceModifBase._checkParams(self, params)
        self._isPRM = RCPaperReviewManager.hasRights(self)
        self._isReferee = RCReferee.hasRights(self)
        self._isReviewingStaff = RCReviewingStaff.hasRights(self)
        self._isEditor = RCEditor.hasRights(self)
        self._isReviewer = RCReviewer.hasRights(self)

    def _checkProtection(self):
        if not self._isReviewingStaff:
            RHConferenceModifBase._checkProtection(self)

    def _process( self ):

        if hasattr(self, "_redirectURL") and self._redirectURL != "":
            url = self._redirectURL
        elif self._isPRM:
            url = urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf )
        elif self._isReferee:
            url = urlHandlers.UHConfModifReviewingAssignContributionsList.getURL( self._conf )
        elif self._isReviewer:
            url = urlHandlers.UHConfModifListContribToJudgeAsReviewer.getURL( self._conf )
        elif self._isEditor:
            url = urlHandlers.UHConfModifListContribToJudgeAsEditor.getURL( self._conf )
        elif self._isReviewingStaff:
            url= urlHandlers.UHConfModifListContribToJudge.getURL( self._conf )

        else: #we leave this else just in case
            url = urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf )

        self._redirect( url )

class RHConfModifReviewingPRMBase (RHConferenceModifBase):
    """ Base class that allows only paper review managers to do this request.
        If user is not a paper review manager, they need to be a conference manager.
    """

    def _checkProtection(self):
        if self._target.hasEnabledSection("paperReviewing"):
            if not RCPaperReviewManager.hasRights(self):
                RHConferenceModifBase._checkProtection(self);
        else:
            raise MaKaCError(_("Paper Reviewing is not active for this conference"))


class RHConfModifReviewingPRMAMBase (RHConferenceModifBase):
    """ Base class that allows only paper review managers OR abstract managers to do this request.
        If user is not a paper review manager, they need to be a conference manager.
    """

    def _checkProtection(self):
        if self._target.hasEnabledSection("paperReviewing"):
            if not RCPaperReviewManager.hasRights(self):
                RHConferenceModifBase._checkProtection(self);
        else:
            raise MaKaCError(_("Paper Reviewing is not active for this conference"))



class RHConfModifReviewingPaperSetup( RHConfModifReviewingPRMBase ):
    """ Class used when the user clicks on the Paper Setup
        subtab of the Reviewing tab
    """
    _uh = urlHandlers.UHConfModifReviewingPaperSetup

    def _process( self ):
        if self._conf.isClosed():
            p = WPConferenceModificationClosed( self, self._target )
        else:
            p = WPConfModifReviewingPaperSetup( self, self._target)
        return p.display()



#################################### Start of old classes that are not used anymore ###############################
class RHChooseReviewing(RHConfModifReviewingPRMBase):
    _uh = urlHandlers.UHChooseReviewing

    def _checkParams( self, params ):
        RHConfModifReviewingPRMBase._checkParams( self, params )
        self._reviewing = int(params.get("reviewing"))

    def _process( self ):
        self._conf.getConfPaperReview().setChoice( self._reviewing )
        if self._reviewing == "No_reviewing":
            self._redirect(urlHandlers.UHConferenceModification.getURL(self._conf))
        else:
            self._redirect( urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ) )


class RHAddState(RHConfModifReviewingPRMBase):
    _uh = urlHandlers.UHAddState

    def _checkParams( self, params ):
        RHConfModifReviewingPRMBase._checkParams( self, params )
        self._state = params.get("state")

    def _process( self ):
        self._conf.getConfPaperReview().addState( self._state )
        self._redirect( urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ) )


class RHRemoveState(RHConfModifReviewingPRMBase):
    _uh = urlHandlers.UHRemoveState

    def _checkParams(self, params):
        RHConfModifReviewingPRMBase._checkParams(self, params)
        self._state = params.get("stateSelection")

    def _process(self):
        self._conf.getConfPaperReview().removeState(self._state)
        self._redirect( urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ) )

class RHAddQuestion(RHConfModifReviewingPRMBase):
    _uh = urlHandlers.UHAddQuestion

    def _checkParams( self, params ):
        RHConfModifReviewingPRMBase._checkParams( self, params )
        self._question = params.get("question")

    def _process( self ):
        self._conf.getConfPaperReview().addReviewingQuestion( self._question )
        self._redirect( urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ) )

class RHRemoveQuestion(RHConfModifReviewingPRMBase):
    _uh = urlHandlers.UHRemoveQuestion

    def _checkParams(self, params):
        RHConfModifReviewingPRMBase._checkParams(self, params)
        self._question = params.get("questionSelection")

    def _process(self):
        self._conf.getConfPaperReview().removeReviewingQuestion(self._question)
        self._redirect( urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ) )

class RHAddCriteria(RHConfModifReviewingPRMBase):
    _uh = urlHandlers.UHAddCriteria

    def _checkParams( self, params ):
        RHConfModifReviewingPRMBase._checkParams( self, params )
        self._criteria = params.get("criteria")

    def _process( self ):
        self._conf.getConfPaperReview().addLayoutCriteria( self._criteria )
        self._redirect( urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ) )

class RHRemoveCriteria(RHConfModifReviewingPRMBase):
    _uh = urlHandlers.UHRemoveCriteria

    def _checkParams(self, params):
        RHConfModifReviewingPRMBase._checkParams(self, params)
        self._criteria = params.get("criteriaSelection")

    def _process(self):
        self._conf.getConfPaperReview().removeLayoutCriteria(self._criteria)
        self._redirect( urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ) )

#################################### END of old classes that are not used anymore ###############################

class RHSetTemplate(RHConfModifReviewingPRMBase):
    _uh = urlHandlers.UHSetTemplate

    def _checkParams( self, params ):
        RHConfModifReviewingPRMBase._checkParams( self, params )
        self._name = params.get("name")
        self._description = params.get("description")
        self._templateId = params.get("temlId")
        if ("format" in params):
            self._format = params.get("format")
        else:
            self._format = params.get("formatOther")
        try:
            self._templatefd = params.get("file").file
        except AttributeError:
            raise MaKaCError("Problem when storing template file")
        self._ext = os.path.splitext(params.get("file").filename)[1] or '.template'

    def _process( self ):
        import random
        self._id = str(random.random()*random.randint(1,32768))
        if self._templatefd == None:
            return {'status': 'ERROR'}
        else:
            self._conf.getConfPaperReview().setTemplate(self._name, self._description, self._format, self._templatefd, self._id, self._ext)
            #self._redirect( urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ) )
            return json.dumps({
                'status': 'OK',
                'info': {
                    'name': self._name,
                    'description': self._description,
                    'format': self._format,
                    'id': self._id
                }
            }, textarea=True)

class RHDownloadTemplate(RHConferenceBaseDisplay):

    def _checkProtection(self):
        if self._target.hasEnabledSection("paperReviewing"):
            RHConferenceBaseDisplay._checkProtection(self)
        else:
            raise MaKaCError(_("Paper Reviewing is not active for this conference"))


    def _checkParams(self, params):
        RHConferenceBase._checkParams( self, params )
        self._templateId = params.get("reviewingTemplateId")

    def _process(self):
        template=self._target.getConfPaperReview().getTemplates()[self._templateId].getFile()
        self._req.headers_out["Content-Length"]="%s"%template.getSize()
        cfg=Config.getInstance()
        mimetype=cfg.getFileTypeMimeType(template.getFileType())
        self._req.content_type="""%s"""%(mimetype)
        self._req.headers_out["Content-Disposition"]="""inline; filename="%s\""""%template.getFileName()
        return template.readBin()

class RHDeleteTemplate(RHConfModifReviewingPRMBase):

    def _checkParams(self, params):
        RHConferenceBase._checkParams( self, params )
        self._templateId = params.get("reviewingTemplateId")

    def _process(self):
        self._conf.getConfPaperReview().deleteTemplate(self._templateId)
        self._redirect(urlHandlers.UHConfModifReviewingPaperSetup.getURL( self._conf ))
