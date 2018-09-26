#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# this script updates the requirements.yml with the latest tag from the passed repo. Alternatively it can update wit with a specified tag.
#
# Usage:
#   Make a osmo-release for ansible-openshift-preparation to latest tage.g.
#   ./scripts/osmo-release.py --repo ansible-openshift-preparation --requirements requirements.yml 

import yaml
import argparse
import commands
import versioning_library

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('--repo', dest='repo', action='store', required='true', help="Repo to update")
parser.add_argument('--requirements', default='requirements.yml', dest='requirements', action='store', help="Location of release config file")
parser.add_argument('--new-version', default='', dest='new_version', action='store', help="new version to update with. by default it will look up the version from repo")
args = parser.parse_args()

with open(args.requirements, 'r') as f:
  requirements_yaml = yaml.safe_load(f)
f = None

if args.new_version == '':
  new_version = versioning_library.get_last_tag(args.repo)
else:
  new_version = args.new_version

for a_repo in requirements_yaml:
  if args.repo in a_repo['src']:
    if a_repo['version'] == new_version:
      print "==> " + args.repo+": "+new_version+" already set. Skipping!"
    else:
      print "==> Updating "+args.repo+": "+a_repo['version'] +" to "+new_version
      a_repo['version'] = new_version

with open(args.requirements, 'w') as f:
  yaml.dump(requirements_yaml, f, default_flow_style=False, default_style='', explicit_start=True)
f = None

# update terraform version
for a_repo in [ 'osmo-terraform' ]:
  repo_version_file = a_repo+'-version'
  current_version = open(repo_version_file, 'r').read()
  if args.repo in a_repo:
    if current_version == new_version:
      print "==> " + args.repo + ": " + new_version + " already set. Skipping!"
    else:
      update_version_file = open(repo_version_file,'w')
      update_version_file.write(new_version)
      update_version_file.close()
      print "==> Updating " + a_repo + ": " + current_version + " to " + new_version
