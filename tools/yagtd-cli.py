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
Copyright (C) 2006-2010 MiKael NAVARRO

A primitive Getting Things Done to-do list manager.
CLI version: allowing to run commands non-interactively.

"""

# Specific variables for pydoc
__author__ = "MiKael Navarro <klnavarro@gmail.com>"
__date__ = "July 2010"

# Include directives
import os
import sys
sys.path.append(os.path.join(sys.path[0], '../src'))  # add src dir
import inspect  # function inspect
import yagtd

#
# Subclass optparse.IndentedHelpFormatter in order
# to display correctly (with new lines) the help.
#
# TODO: use 'argparse' (new in Python version 2.7).
#
from optparse import IndentedHelpFormatter
import textwrap

class IndentedHelpFormatterWithNL(IndentedHelpFormatter):
    """IndentedHelpFormatter Subclass
    in order to display correctly (with new lines) the help.

    By Tim CHASE."""
    
    def format_description(self, description):
        """Return formatted program description."""
        
        if not description: return ""
        
        desc_width = self.width - self.current_indent
        indent = " "*self.current_indent
        
        # The above is still the same
        bits = [ line.strip() for line in description.split('\n') ]
        formatted_bits = [
            textwrap.fill(bit,
                          desc_width,
                          initial_indent=indent,
                          subsequent_indent=indent)
            for bit in bits ]
        
        return "\n".join(formatted_bits) + "\n"

    format_epilog = format_description

    def format_option(self, option):
        """Return formatted option description.
        
        The help for each option consists of two parts:
          * the opt strings and metavars
          eg. ("-x", or "-fFILENAME, --file=FILENAME")
          * the user-supplied help string
          eg. ("turn on expert mode", "read data from FILENAME")
        
        If possible, we write both of these on the same line:
          -x    turn on expert mode
        
        But if the opt string list is too long, we put the help
        string on a second line, indented to the same column it would
        start in if it fit on the first line.
          -fFILENAME, --file=FILENAME
              read data from FILENAME
        """
          
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else: # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        
        if option.help:
            help_text = self.expand_default(option)
            # Everything is the same up through here
            help_lines = []
            for para in [ line.strip().lower() for line in help_text.split("\n") ]:
                help_lines.extend(textwrap.wrap(para, self.help_width))
            # Everything is the same after here
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                           for line in help_lines[1:]])
        elif opts[-1] != "\n":
          result.append("\n")
          
        return "".join(result)

#
# External entry point.
#
if __name__ == "__main__":
    # First instanciate yaGTD object
    gtd_cli = yagtd.GTD()
    gtd_cli.intro = ""

    available_cmds = [ attr.replace("do_", "") for attr in dir(gtd_cli)
                       if attr.startswith('do_') and len(attr) > 4 and attr != 'do_help' ]
    #print available_cmds

    # Get options
    from optparse import OptionParser

    parser = OptionParser(usage="""python -O %prog [--cmd \"args\"] [--help] todo.txt""", 
                          description="""A primitive Getting Things Done to-do list manager.
                          CLI version: allowing to run commands non-interactively.""",
                          epilog="""
                          Ex.:
                          %prog --list \"5\" todo.txt
                          %prog --add \"Text @work p:customer\" --list \"\" todo.txt
                          %prog --status \"\" todo.txt
                          """.replace("%prog", sys.argv[0]),
                          formatter=IndentedHelpFormatterWithNL(),
                          conflict_handler="resolve")
                          
    # Loop on all available yaGTD commands
    # and add an option...
    for cmd in available_cmds:
        func_name = "do_"+cmd
        func = getattr(gtd_cli, func_name)  # function pointer
        func_arg = "_".join(inspect.getargspec(func).args[1:])
        parser.add_option("", "--"+cmd,
                          action="store", dest=cmd, 
                          default=None,
                          help=func.__doc__)

    (options, args) = parser.parse_args()

    # Needed argument
    if not args:
        parser.error("missing todo file argument")
    elif len(args) != 1:
        parser.error("incorrect number of arguments")
        
    # Process start here
    gtd_cli.do_load(args[0])

    # Determine which command are called?
    for cmd in available_cmds:
        cmd_opt = getattr(options, cmd)
        if cmd_opt != None:
            func = getattr(gtd_cli, "do_"+cmd)
            func(cmd_opt)  # execute

    # Automatically save at the end
    func = getattr(gtd_cli, "do_save")
    func("")
