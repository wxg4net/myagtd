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

"""yaGTD
Copyright (C) 2006-2009 MiKael NAVARRO

A primitive Getting Things Done to-do list manager.
S60 version: line oriented command interpreters for pyS60.

"""

# Specific variables for pydoc
__author__ = "MiKael Navarro <klnavarro@gmail.com>"
__date__ = "February 2010"

# Include directives
import os
import sys
sys.path.append('e:\\python')  # add pyS60 install dir
import yagtd


#
# External entry point.
#
if __name__ == "__main__":
    # Customizations
    options = None
    yagtd.FORMATTED_DISPLAY = False  # deactivate detailled display
    yagtd.USE_SHORTCUTS = True  # activate shortcuts

    # Process start here
    yagtd.main(options, "e:\\priv/todo.txt")
