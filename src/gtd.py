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

"""

# Specific variables for pydoc
__author__ = "MiKael Navarro <klnavarro@gmail.com>"
__credits__ = """Thanks to Keith D. Martin for its original project pyGTD."""

# Include directives
import sys, re
import datetime, time
from math import sqrt, log

if __debug__: from pprint import pprint as pp

# Global variables
DAY_IN_HOURS  = 8
NUM_WORK_DAYS = 5
WEEK_IN_HOURS = NUM_WORK_DAYS * DAY_IN_HOURS

# Urgency on a logarithmic scale
TODAY        = 5
THIS_WEEK    = 4
THIS_MONTH   = 3
THIS_QUARTER = 2
THIS_YEAR    = 1
URGENCY=("undef", "this year", "this quarter", "this month", "this week", "today")

# Importance
CRUCIAL = 5
HIGH    = 4
NORMAL  = 3
LOW     = 2
SOMEDAY = 1
IMPORTANCE=("undef", "someday", "low", "normal", "high", "crucial")


#
# Task class (mapping);
# Used as a simple dictionary.
#
Dict = dict
class Task(Dict):
    """A simple task.
    Herited from dict class.
        
    Usage:
    >>> t = Task({'title': "Test"})
    >>> t
    {'id': 0, 'title': 'Test', 'description': '', 'context': [], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 3, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}
    >>> t['context'] = ['@home', '@online']
    >>> t
    {'id': 0, 'title': 'Test', 'description': '', 'context': ['@home', '@online'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 3, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}
    >>> t.priority()
    2.0493901531919194

    """
    
    # GTD attributes (cf. Getting Things Done from David Allen)
    attributes = { 'id': 0,
                   'title': "",
                   'description': "",  # additional notes (NYI)
                   'context': [],    # @context list (@everywhere, @anywhere)
                   'project': [],    # p:project list
                   'status': [],     # !statuses
                   'reference': [],  # Ref.erence
                   }

    # Additional properties from Stephen Covey (cf. Seven Habits of Highly Effective People)
    properties = { 'urgency': THIS_MONTH,  # urgency (U)
                   'importance': NORMAL,  # importance (I)
                   'time': datetime.timedelta(hours=1),  # time required (T)
                   'complete': 0,                        # percent complete (C)
                   'start': None,       # creation date (S)
                   'due': None,         # target date (D)
                   'end': None,         # closure date (E)
                   'recurrence': None,  # recurrence (R)
                   }

    attributes.update(properties)  # merge

    # Attributes list (ordered for display)
    attributes_list = ('id',
                       'title', 'description',
                       'context', 'project', 'status', 'reference',
                       'urgency', 'importance',
                       'time', 'complete',
                       'start', 'due', 'end', 'recurrence')

    #
    # Constructor.
    #

    def __init__(self, dict=None):
        Dict.__init__(self)

        # Add attributes (default values)
        for attribute, default in Task.attributes.iteritems():
            self.setdefault(attribute, default)

        if dict is not None:
            # Updt user's attributes
            self.update(dict)

    #
    # Accesses.
    #
    
    def keys(self):
        return [ attrib for attrib in Task.attributes.keys() if self.has_key(attrib) ]

    def values(self):
        return [ self[attrib] for attrib in Task.attributes.keys() if self.has_key(attrib) ]

    def items(self):
        return [ (attrib, self[attrib]) for attrib in Task.attributes.keys() if self.has_key(attrib) ]

    #
    # Updates.
    #
    
    def __setitem__(self, attribute, value):
        if attribute in Task.attributes.keys():
            Dict.__setitem__(self, attribute, value)
        else:
            raise KeyError, "attribute '%s' not permitted" % attribute

    def update(self, dict):
        for attribute, value in dict.items():
            if attribute in Task.attributes.keys():
                self[attribute] = value
            else:
                raise KeyError, "attribute '%s' not permitted" % attribute

    def add(self, **attribs):
        self.update(attribs)

    supp = Dict.__delitem__

    erase = Dict.clear

    #
    # Display.
    #
    
    def __repr__(self):
        s = ""
        for attrib in Task.attributes_list:
            if self.has_key(attrib):
                if s: s = s + ", "
                s = s + repr(attrib) + ": " + repr(self[attrib])
        return "{" + s + "}"

    #
    # Compute priority of the task:
    # From Keith Martin works.
    #

    def _needed_hours(self):
        """Compute (needed) time in hours."""

        T = self['time'].seconds / 60. / 60.
        
        #if __debug__: print "Time=", T
        return T

    def _effort(self):
        """Determine effort needed."""
        
        h = self._needed_hours()
        if h:
            E = max(1, log(h)/log(3)+1.0)
        else:
            E = 0

        #if __debug__: print "Effort=", E
        return E

    def _schedule_pressure(self):
        """Determine pressure from due date."""

        now = datetime.datetime.today()  # now

        if self['due']:
            # Compute delta from now and target date (- needed time)
            delta = (self['due'] - now) - self['time']
            #print "delta=", delta

            if delta < datetime.timedelta(0):  # overdue
                P = 6
            elif delta < datetime.timedelta(1):  # today
                P = 5
            elif delta < datetime.timedelta(3):  # within 3 days
                P = 4.5
            elif delta < datetime.timedelta(7):  # this week
                P = 4
            elif delta < datetime.timedelta(15):  # within 2 weeks
                P = 3.5
            elif delta < datetime.timedelta(30):  # this month
                P = 3
            elif delta < datetime.timedelta(90):  # this quarter
                P = 2
            elif delta < datetime.timedelta(180):  # this half year
                P = 1.5
            else:  # > 6 months
                P = 1
                
        else:  # == urgency
            P = self['urgency']

        #if __debug__: print "Pressure=", P
        return P

    def priority(self):
        """Compute priority."""

        if "someday" in self['status']:
            I = SOMEDAY  # min importance
        else:  # == importance (even for !waitingfor)
            I = self['importance']

        #P = min(self['urgency']+2, self._schedule_pressure())
        P = self._schedule_pressure()
        U = max(self['urgency'], P)

        E = self._effort()

        Prio = sqrt(2*U*U+2*I*I+E*E)/sqrt(5)
        
        #if __debug__: print "Piority=", Prio
        return Prio


#
# ToDo class (sequence);
# Used as a simple list.
#
List = list
class ToDo(List):
    """A todo list.
    Herited from list class.
        
    Usage:
    >>> todo = ToDo()
    >>> t1 = Task({'title': "Test 1", 'importance': NORMAL, 'context': ['@home', '@work']})
    >>> t2 = Task({'title': "Test 2", 'importance': HIGH, 'context': ['@work']})
    >>> todo.add(t1)
    1
    >>> todo.add(t2)
    2
    >>> todo
    [{'id': 1, 'title': 'Test 1', 'description': '', 'context': ['@home', '@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 3, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}, {'id': 2, 'title': 'Test 2', 'description': '', 'context': ['@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 4, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}]
    >>> todo[0].priority()
    2.0493901531919194
    >>> todo[1].priority()
    2.6457513110645907
    >>> todo.sort()
    [{'id': 2, 'title': 'Test 2', 'description': '', 'context': ['@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 4, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}, {'id': 1, 'title': 'Test 1', 'description': '', 'context': ['@home', '@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 3, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}]
    >>> todo.supp(1)
    >>> todo
    [{'id': 2, 'title': 'Test 2', 'description': '', 'context': ['@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 4, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}]
    >>> todo.add(t1)
    3
    >>> todo
    [{'id': 2, 'title': 'Test 2', 'description': '', 'context': ['@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 4, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}, {'id': 3, 'title': 'Test 1', 'description': '', 'context': ['@home', '@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 3, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}]
    >>> todo.order_by('context')
    {'@home': [{'id': 3, 'title': 'Test 1', 'description': '', 'context': ['@home', '@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 3, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}], '@work': [{'id': 2, 'title': 'Test 2', 'description': '', 'context': ['@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 4, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}, {'id': 3, 'title': 'Test 1', 'description': '', 'context': ['@home', '@work'], 'project': [], 'status': [], 'reference': [], 'urgency': 1, 'importance': 3, 'time': datetime.timedelta(0, 3600), 'complete': 0, 'start': None, 'due': None, 'end': None, 'recurrence': None}]}
    >>> todo.erase()
    >>> todo
    []
    
    """

    #
    # Constructor.
    #
    
    def __init__(self, list=None):
        List.__init__(self)

        if list is not None:
            self.append(list)

    #
    # Accesses.
    #
    
    def _last_id(self):
        """Return the last id of the to-do list."""
        
        idxes = [ t['id'] for t in self[:] ]  # list of indexes
        if idxes:
            return max(idxes)
        else:
            return 0

    def _cmp_prio(self, t1, t2):
        """Compare two task vs priority."""
        
        return cmp(t2.priority(), t1.priority())

    def _attr_list(self, attr):
        """Return the list of all 'attr' (remove redundancy)."""

        attr_lst = []
        for t in self:
            for a in t[attr]:
                if a not in attr_lst:
                    attr_lst.append(a)
        return attr_lst

    def search(self, regexp):
        """Return all tasks matching 'regexp'."""

        expr = re.compile(regexp, re.IGNORECASE)
        tasks = [ t for t in self if expr.search(t['title']) ]  # only into 'title'
        tasks.sort(self._cmp_prio)  # and sort by prio
        return tasks

    def find(self, attr, value):
        """Return all tasks into 'attr' matching 'value'."""

        if attr in ['context', 'project', 'status', 'reference']:
            # Return a list of tasks
            return [ t for t in self if value in t[attr] ]
        else:
            # Only one task must match!
            for t in self:
                if t[attr] == value:
                    return t
    find_into = find

    def sort(self):  # all by priority
        """Return all tasks sorted by priority."""
        
        tasks = self[:]
        tasks.sort(self._cmp_prio)
        return tasks

    def order(self, attr):
        """Return all tasks grouped by 'attr' (and sorted by priority)."""

        tasks = {}
        for a in self._attr_list(attr):
            tasks[a] = [ t for t in self.find(attr, a) ]
            tasks[a].sort(self._cmp_prio)  # and sort by prio
        return tasks

    order_by = order

    #
    # Updates.
    #
    
    def add(self, task):
        """Add a new task to the to-do list (automatically set the 'id')."""
        
        if not isinstance(task, Task):
            raise TypeError, "'%s' is not an instance of Task" % task
        task['id'] = self._last_id() + 1  # first, set task Id
        List.append(self, task)
        return task['id']  # added task Id

    def extend(self, tasks):
        """Add new tasks to the to-do list."""

        for t in tasks:
            task = Task(t)
            self.add(task)

    def supp(self, id):
        """Remove the task with 'id'."""

        # Frist, we need to find the task
        task = self.find('id', id)
        if task:
            self.remove(task)

    def erase(self):
        """Reset the to-do list."""
        
        self[:] = []

    #
    # Display.
    #
    
    def __repr__(self):
        s = ""
        for item in self:
            if s: s = s + ", "
            s = s + repr(item)
        return "[" + s + "]"


#
# Main test function.
#
def test():
    import doctest
    doctest.testmod(sys.modules[__name__])


#
# External entry point.
#
if __name__ == "__main__":
    test()
