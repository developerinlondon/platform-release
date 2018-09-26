#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# this script updates the requirements.yml with the latest tag from the passed repo. Alternatively it can update wit with a specified tag.
#
# Usage:
#   Tags a repo that is passed tage.g.
#   ./scripts/tag-repo.py --repo <repo_name> [--skip_push] [--release_note true/false] [--release_note_file <publish release note to the specified file> ]

import yaml
import argparse
import commands
import os
import versioning_library

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('--repo', dest='repo', action='store', required='true', help="Repo to update")
parser.add_argument('--skip-push', default=False, dest='skip_push', action='store_true', help="skip_push Mode. Defaults to false. Will skip pushing the new branch and tags to remote if --skip_push is passed")
parser.add_argument('--verbose', default=False, dest='verbose', action='store_true', help="verbose Mode. Spits out more info if in verbose mode")
parser.add_argument('--branch', default='master', dest='branch', action='store', help="Branch to build (defaults to master)")
parser.add_argument('--release-type', default='minor', dest='release_type', action='store', help="Type of release - major/minor/hotfix")
parser.add_argument('--skip-release-note', default=False, dest='skip_release_note', action='store_true', help="Skips Publishing a release_note.txt file")
parser.add_argument('--release-note-file', default='release_note.txt', dest='release_note_file', action='store', help="name of the release_note file")
args = parser.parse_args()

os.system(
  'cd /tmp; mkdir -p osmo-workspace; cd osmo-workspace; rm -fr '+args.repo+';'
  +'git clone git@bitbucket.org:motabilityoperations/'+args.repo+'.git; cd '+args.repo+';'
  +'git checkout '+args.branch
  )
cwd = os.getcwd()

os.chdir('/tmp/osmo-workspace/'+args.repo)
head_tag=commands.getstatusoutput("git describe --contains `git rev-parse HEAD`")
if args.verbose:
  print 'head_tag:'
  print head_tag
if head_tag[0] == 0:
  print "==> The latest commit on "+args.branch+" already tagged to "+head_tag[1]+". Skipping!"
  exit()

last_version=versioning_library.get_last_tag(args.repo)
new_version = versioning_library.get_new_version(last_version,args.release_type)

if args.verbose:
  print 'new version:'
  print new_version

versioning_library.generate_release_note(args.repo, last_version, new_version, cwd+"/"+args.release_note_file, args.skip_release_note)

os.system('git tag '+new_version)
print "==> Tagged with "+new_version
if args.skip_push:
  print "==> Skipped Pushing as '--skip-push' passed!"
else:
  os.system('git push --tags')
  print "==> Pushed new tag "+new_version
