"""
Usage: python get_gist.py <username>
Description: This script will clone all gists for a user and rename the directory to the description of the gist(if present).
"""
import os, sys
import requests
from subprocess import call

user = sys.argv[1]

response = requests.get('https://api.github.com/users/{0}/gists'.format(user), headers={"Authorization": "Bearer super-secret-token-here"})

for i in response.json():
      call(['git', 'clone', i['git_pull_url']])
      new_description = i['description'].lower().replace(' ', '_')
      # renames dir to files description
      # Works only if a description is present
      os.rename(i['id'], new_description)

      # un-comment this block to have a description file in the directory
      # description_file = './{0}/description.txt'.format(i['id'])
      # with open(description_file, 'w') as f:
      #       f.write('{0}\n'.format(i['description']))
