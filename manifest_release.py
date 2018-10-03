#!/usr/bin/env python2
import yaml
import argparse
import commands
import os
import versioning_library

import re
import sys

parser = argparse.ArgumentParser(description='Options')
# ths script expects cp_manifest folder to have the manifest configs
parser.add_argument('--type', dest='type', default='minor', action='store', help="Release Type. major/minor/hotfix")
parser.add_argument('--skip-release-note', default=False, dest='skip_release_note', action='store_true', help="Skip Publishing a release_note.txt file")
parser.add_argument('--apply', default=False, dest='apply', action='store_true', help="Apply Mode. Pushes the changes to remote.")
parser.add_argument('--release-note-file', default='manifest_release_note.txt', dest='release_note_file', action='store', help="name of the release_note file")
parser.add_argument('--verbose', default=False, dest='verbose', action='store_true', help="verbose Mode. Spits out more info if in verbose mode")
parser.add_argument('--release-type', default='minor', dest='release_type', action='store', help="Type of release - major/minor/hotfix")
parser.add_argument('--manifest_tags', default='openshift-cluster', dest='manifest_tags', action='store', help="Name of the Manifest Group to release.")
parser.add_argument('--manifest_file', default='default.xml', dest='manifest_file', action='store', help="Name of the Manifest File to use.")
parser.add_argument('--manifest_branch', default='master', dest='manifest_branch', action='store', help="Name of the Manifest Branch to make the release off of.")
args = parser.parse_args()


##### LOGIC ######
# clone cp_manifest.xml repo master branch
# open the file called default.xml
# loop through each line
# if line starts with <project
#   read the name of the project
#   new_version = versioning_library.get_last_tag(project_name)
#   read the existing version on manifest
#   check the last version already on repo
#   if manifest version is different then last version on repo
#     write to new file the updated version
#   else
#     write to new file old version
#  end for loop
# close new file
# close old file

cwd = os.getcwd()
workspace = cwd+'/workspace'
manifest_file = workspace+'/cp_manifest/'+args.manifest_file
release_note_file = workspace+'/cp_manifest/release.txt'
outputfile = workspace + '/output.xml'


os.system( 'rm -fr '+workspace+'; mkdir -p '+workspace)
os.chdir(workspace)
os.system('git clone git@bitbucket.org:motabilityoperations/cp_manifest.git; cd cp_manifest; git checkout master;')

manifest_file_handler = open(outputfile,'w')
release_note_file_handler = open(release_note_file,'w')

last_release = versioning_library.get_last_release('cp_manifest')
new_release  = versioning_library.get_new_version(last_release,args.type)

last_version = versioning_library.get_last_tag('cp_manifest')
new_version = versioning_library.get_new_version(last_version,args.release_type)
release_note_file_handler.write(versioning_library.generate_release_note('cp_manifest', last_version, new_version, args.skip_release_note))

for line in open(manifest_file,'r'):
  output_line = line
  m = re.search('<project name="(.*?)".*?revision="(.*?)"',line)
  if hasattr(m,'group'):
    project_name = m.group(1)
    manifest_version = m.group(2)

    #### tag repo
    os.system(
      'cd '+workspace+'; rm -fr '+project_name+';'
      +'git clone git@bitbucket.org:motabilityoperations/'+project_name+'.git; cd '+project_name+';'
      +'git checkout master'
      )

    os.chdir(workspace+'/'+project_name)

    head_tag=commands.getstatusoutput("git describe --contains `git rev-parse HEAD`")
    last_version = versioning_library.get_last_tag(project_name)
    if args.verbose:
      print 'head_tag:'
      print head_tag
    if head_tag[0] == 0:
      print "==> The latest commit on master already tagged to "+head_tag[1]+". Skipping!"
      new_version = last_version
    else:
      new_version  = versioning_library.get_new_version(last_version,args.release_type)

      if args.verbose:
        print 'new version:'
        print new_version

      os.system('git tag '+new_version)
      print "==> Tagged with "+new_version
      if args.apply:
       # os.system('git push --tags')
        print "==> Pushed new tag "+new_version
      else:
        print "==> Skipped Pushing as '--apply' not passed!"

      release_note_file_handler.write(versioning_library.generate_release_note(project_name, last_version, new_version, args.skip_release_note))

    #### End tag_repo

    # now update manifest
    if manifest_version == 'refs/tags/'+new_version:
      print project_name+": "+"skipping - "+manifest_version+ " to "+new_version
    else:
      print project_name+": "+"updating - "+manifest_version+ " to "+new_version
      output_line = re.sub(r"revision=\".*?\"","revision=\"refs/tags/"+new_version+"\"",line)
  manifest_file_handler.write(output_line)

manifest_file_handler.close()
release_note_file_handler.close()

os.chdir(workspace+'/cp_manifest')
os.system('git checkout -b release/'+new_release)
os.system('cp '+outputfile+' '+manifest_file)
os.system('git add -A')
os.system('git commit -m"release '+new_release+' created"')
os.system('git tag '+new_release)
if args.apply:
  print '==> Pushing Tags and Releases '+new_release+'!'
  os.system('git push --tags')
  os.system('git push origin release/'+new_release)
else:
  print '==> Skipping Pushing as apply not passed!'

