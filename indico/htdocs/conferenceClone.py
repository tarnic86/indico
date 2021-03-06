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

from MaKaC.common.general import *

from MaKaC.webinterface import pages

if DEVELOPMENT:
    pages = reload(pages)




def index(req, **params):
    p = pages.WPConferenceClone(req)
    params["cloneOnce"] = "conferenceClone.py/cloneOnce"
    params["cloneInterval"] = "conferenceClone.py/cloneInterval"
    params["cloneday"] = "conferenceClone.py/cloneday"
    return p.display(params)


def cloneOnce(req, **args):
    p = pages.WPConferenceClone(req)
    str = p.cloneOnce(args)
    return str

def cloneInterval(req, **args):
    p = pages.WPConferenceClone(req)
    str = p.cloneInterval(args)
    return str

def cloneday(req, **args):
    p = pages.WPConferenceClone(req)
    str = p.cloneday(args)
    return str


