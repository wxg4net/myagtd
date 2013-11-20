#!/usr/bin/env python2 
# -*- coding: utf-8 -*-

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient.discovery import build
import os
import httplib2

G_TASK_STATUS_COMPLETED = u'completed'
G_TASK_STATUS_ACTION = u'completed'

class GoogleGtasks():
  
    #~ task[status] = needsAction
    #~ task[kind] = tasks#task
    #~ task[title] = xxxx
    #~ task[updated] = 2013-11-18T05:49:44.000Z
    #~ task[due] = 2013-11-19T00:00:00.000Z
    #~ task[etag] = "zhaMOBt6ugsBcjvafbKQm19UaRg/LTEwNjcwNTA3ODc"
    #~ task[position] = 00000000000302284590
    #~ task[id] = MDU5MTA2MTMzMDM0MzE2Mzg5MzA6MDoxMzk5MDk5OTUy
    #~ task[selfLink]
    
  def __init__(self):
    self.credentials_file = os.getenv("HOME")+'/.yagtd/credentials.dat'
    self.client_secrets_file = os.getenv("HOME")+'/.yagtd/client_secrets.json'
    
    if not os.path.isfile(self.client_secrets_file):
        raise Exception('client_secrets.json not exits')
        
    self.storage = Storage(self.credentials_file)
    self.credentials = self.storage.get()
    
    #~ httplib2.debuglevel = 4
    self.http = httplib2.Http()
    
    if self.credentials is None or self.credentials.invalid:
      flow = flow_from_clientsecrets(self.client_secrets_file,
                                 scope='https://www.googleapis.com/auth/tasks',
                                 redirect_uri='urn:ietf:wg:oauth:2.0:oob')
      self.credentials = run(flow, self.storage)
      self.storage.put(self.credentials)
    self.http = self.credentials.authorize(self.http)
    self.service = build('tasks', 'v1', http=self.http)
    self.gtask = self.service.tasks()
    self.tasks = []
    
  def list(self):
    tasks = []
    try:
        result = self.gtask.list(tasklist='@default').execute()
    except:
        raise Exception('network error')
    tasks = result.get('items', [])
    return tasks

  def rsync(self):
    pass
    
  def get(self, task_id):
    task = service.tasks().get(tasklist='@default', task=task_id).execute()
    return task

  def update(self, task_id, task):
    service.tasks().update(tasklist='@default', task=task_id, body=task).execute()

  def delete(self, task_id):
    delete(tasklist='@default', task=task_id).execute()
    
  def insert(self, task):
    self.gtask.insert(tasklist='@default', body=task).execute()
    
    
def main():
  gt = GoogleGtasks()
  print gt.list()
  pass
  
if __name__ == "__main__":
  main()
 