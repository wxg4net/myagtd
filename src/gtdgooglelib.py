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
    
  def __init__(self, use_goagent=False):
    self.user_data_dir = os.sep.join([os.getenv("HOME"), '.yagtd++'])
    if not os.path.isdir(self.user_data_dir):
      try:
        os.mkdir(self.user_data_dir)
      except:
        raise Exception('OSError')
        
    self.credentials_file = os.sep.join([self.user_data_dir, 'credentials.dat'])
    
    self.client_secrets_files = ''
    for csf in ('/usr/share/yagtd++/client_secrets.json', 'client_secrets.json'):
        if os.path.isfile(csf):
            self.client_secrets_files = csf
            break
    if self.client_secrets_files == '':
        raise Exception('client_secrets.json not exits')
            
    self.storage = Storage(self.credentials_file)
    self.credentials = self.storage.get()
    
    #~ httplib2.debuglevel = 4
    if use_goagent:
        self.http = httplib2.Http( proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP, 'localhost', 8087), disable_ssl_certificate_validation = True )
    else:
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
    self.num_retries=5
    self.tasks = []
    
  def list(self):
    try:
        result = self.gtask.list(tasklist='@default').execute(num_retries=self.num_retries)
    except:
        raise Exception('network error')
    tasks = result.get('items', [])
    return tasks

  def rsync(self):
    pass
    
  def get(self, task_id):
    task = self.gtask.get(tasklist='@default', task=task_id).execute(num_retries=self.num_retries)
    return task

  def update(self, task_id, task):
    self.gtask.update(tasklist='@default', task=task_id, body=task).execute(num_retries=self.num_retries)

  def delete(self, task_id):
    self.gtask.delete(tasklist='@default', task=task_id).execute(num_retries=self.num_retries)
    
  def insert(self, task):
    self.gtask.insert(tasklist='@default', body=task).execute(num_retries=self.num_retries)
    
    
def main():
  gt = GoogleGtasks(True)
  # for test
  print gt.list()
  
if __name__ == "__main__":
  main()
 