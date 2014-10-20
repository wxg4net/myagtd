#! /usr/bin/python -O
# -*- coding: utf-8 -*-
#
# To-do list manager.
# Copyright (C) 2006-2010 MiKael NAVARRO
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


# Specific variables for pydoc
__author__ = "wxg <wxg4dev@gmail.com>"
__date__ = "July 2013"

import os
import sys
import imp
yagtd = imp.load_source('yagtd', '/usr/bin/myagtd.py')

if __name__ == "__main__":
    # First instanciate yaGTD object
    gtd_cli = yagtd.GTD()
    if len(sys.argv) < 2:
        sys.exit('missing args') 
    gtd_cli.do_load(os.sep.join([os.getenv("HOME"), 'work/archiving/todo']))
    cmd = sys.argv[1]
    func = getattr(gtd_cli, "do_"+cmd)
    func() 


