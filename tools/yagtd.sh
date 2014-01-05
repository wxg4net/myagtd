#! /bin/sh
#
# To-do list manager.
# Copyright (C) 2010 Max VOZELER
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

# Default path to your 'todo.txt' file.
TODOFILE=~/todo.txt
#TODOFILE=../tests/todo.txt

# Path to 'yagtd-cli.py' wrapper.
YAGTD_CLI=yagtd-cli.py
#YAGTD_CLI=./yagtd-cli.py

#
# Function given to trap built in command.
#
trapsignal() {
    echo "\nSignal received. Doing cleanup before ending...."
    exit 1;
}

#
# Print script usage.
#
usage() {
    echo "Usage: `basename $1` <cmd> <args>"
    echo ""
    echo "Provide way to run commands non-interactively."
    echo ""
    echo "  -v   verbose mode"
    echo "  -d   debug mode"
    echo "  -h   this help"
    echo ""
    echo "Ex:"
    echo "  `basename $1` add Text @work p:customer2"
    echo "  `basename $1` listall"
    echo "  `basename $1` search @home"
    echo ""
    echo "Return values :"
    echo "  0 => OK"
    echo "  1 => KO"
    echo "  2 => error in arguments"
}

# Trapping signals INT TERM
trap trapsignal INT TERM

# 
# Option parsing.
# 
ARGERROR=0

# Script with no option => print usage and exit
if [ $# -eq 0 ]
then
    usage ${0}
    exit 2
fi

while getopts :dvh opt
  do
  case ${opt} in
      h) usage ${0};exit 0;;
      d) set -x;;
      v) set -v;;
      \?) echo "Unknown option: ${OPTARG}";ARGERROR=1;; 
  esac
done
shift `expr $OPTIND - 1`

if [ ${ARGERROR} != 0 ]
then
    echo "Error(s) in option parsing. Aborting!"
    exit 2
fi

# Get <command> + <arguments>
if [ $# -gt 0 ]
then
    CMD=$1
    shift
    ARGS=$*
else
    echo "Error: missing arguments"
    exit 2
fi

# 
# Main
#
while true
do
    # Call yaGTD CLI
    echo "$YAGTD_CLI --$CMD \"$ARGS\" $TODOFILE"
    $YAGTD_CLI --$CMD "$ARGS" $TODOFILE
    if [ $? != 0 ]; then exit 1; fi
    break
done

exit 0
