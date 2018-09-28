#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# this script updates the manifest.xml file with the latest tag from the passed repo
# Alternatively it can update wit with a specified tag.
#
# Usage:
#   Make a osmo-release for ansible-openshift-preparation to latest tage.g.
#   ./scripts/update-manifest.py --repo ansible-openshift-preparation --manifest default.xml 

import argparse
import commands
import versioning_library
from xml.etree.ElementTree import ElementTree

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('--repo', dest='repo', action='store', required='true', help="Repo to update")
parser.add_argument('--manifest', default='default.xml', dest='manifest', action='store', help="Location of the manifest file")
parser.add_argument('--new-version', default='', dest='new_version', action='store', help="new version to update with. by default it will look up the version from repo")
args = parser.parse_args()

tree = ElementTree()
tree.parse(args.manifest)
current_version = tree.getroot().find("project[@name='"+args.repo+"']").get('revision')

if args.new_version == '':
  new_version = versioning_library.get_last_tag(args.repo)
else:
  new_version = 'refs/tags/'+args.new_version

if current_version == new_version:
  print "==> " + args.repo+": "+new_version+" already set. Skipping!"
else:
  print "==> Updating "+args.repo+": "+current_version +" to "+new_version
  tree.getroot().find("project[@name='"+args.repo+"']").set('revision',new_version)
  tree.write(args.manifest)


# clone cp_manifest.xml repo master branch
# open the file called default.xml
# loop through each line
# if line starts with <project
#   read the name of the project
#   new_version = versioning_library.get_last_tag(project_name)
#   read the existing version
#   if version is different then new version
#     write to new file the updated version
#   else
#     write to new file old version
#  end for loop
# close new file
# close old file
# move old  
