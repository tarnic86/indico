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

from MaKaC.webinterface.rh import conferenceModif


def index( req, **params ):
    return conferenceModif.RHConfModifProgram( req ).process( params )


def addTrack( req, **params ):
    return conferenceModif.RHConfAddTrack( req ).process( params )


def performAddTrack( req, **params ):
    return conferenceModif.RHConfPerformAddTrack( req ).process( params )


def deleteTracks( req, **params ):
    return conferenceModif.RHConfDelTracks( req ).process( params )


def moveTrackUp(req,**params):
    return conferenceModif.RHProgramTrackUp( req ).process( params )


def moveTrackDown(req,**params):
    return conferenceModif.RHProgramTrackDown( req ).process( params )

def modifyDescription(req,**params):
    return conferenceModif.RHProgramDescription( req ).process( params )
