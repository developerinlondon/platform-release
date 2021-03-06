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
parser.add_argument('--manifest-release-type', dest='manifest_release_type', default='minor', action='store', help="Manifest Release Type. major/minor/hotfix")
parser.add_argument('--repo-release-type', default='minor', dest='repo_release_type', action='store', help="Type of release for repos - major/minor/hotfix")
parser.add_argument('--skip-release-note', default=False, dest='skip_release_note', action='store_true', help="Skip Publishing a release_note.txt file")
parser.add_argument('--build', default=False, dest='build', action='store_true', help="Build Mode. Builds the releases locally.")
parser.add_argument('--apply', default=False, dest='apply', action='store_true', help="Apply Mode. Pushes the changes to remote.")
parser.add_argument('--undo', default=False, dest='undo', action='store_true', help="Undo Mode. Updates remote by changing the tags that were last pushed.")
parser.add_argument('--release-note-file', default='manifest_release_note.txt', dest='release_note_file', action='store', help="name of the release_note file")
parser.add_argument('--verbose', default=False, dest='verbose', action='store_true', help="verbose Mode. Spits out more info if in verbose mode")
parser.add_argument('--manifest-tags', default='build', dest='manifest_tags', action='store', help="Name of the Manifest Group to release.")
parser.add_argument('--manifest-file', default='manifest.xml', dest='manifest_file', action='store', help="Name of the Manifest File to use.")
parser.add_argument('--manifest-repo', default='cp_manifest', dest='manifest_repo', action='store', help="Name of the Manifest Repo to use.")
parser.add_argument('--manifest-version', default='master', dest='manifest_version', action='store', help="Name of the Manifest Branch or Tag to make the release off of.")
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
manifest_file = workspace+'/'+ args.manifest_repo +'/'+args.manifest_file
release_note_source_file = workspace + '/release.txt'
release_note_destination_file = workspace +'/'+ args.manifest_repo + '/release.txt'
outputfile = workspace + '/output.xml'

if args.build:
  os.system( 'rm -fr '+workspace+'; mkdir -p '+workspace)
  os.chdir(workspace)
  os.system('git clone https://github.com/developerinlondon/'+args.manifest_repo+'.git; cd '+args.manifest_repo+'; git checkout '+args.manifest_version+';')
  os.chdir(workspace+'/'+args.manifest_repo)

  manifest_file_handler = open(outputfile,'w')
  release_note_file_handler = open(release_note_source_file,'w')

  last_manifest_tag = versioning_library.get_last_tag(args.manifest_repo)
  new_manifest_tag = versioning_library.get_new_tag(last_manifest_tag,args.manifest_release_type)
  release_note_file_handler.write(versioning_library.generate_release_note(args.manifest_repo, last_manifest_tag, new_manifest_tag, args.skip_release_note))

  for line in open(manifest_file,'r'):
    output_line = line
    m = re.search('<project name="(.*?)".*?revision="(.*?)".*?groups="(.*?'+args.manifest_tags+'.*?)"',line)
    if hasattr(m,'group'):
      project_name = m.group(1)
      manifest_version = m.group(2)

      #### tag repo
      os.system(
        'cd '+workspace+'; rm -fr '+project_name+';'
        +'git clone https://github.com/developerinlondon/'+project_name+'.git; cd '+project_name+';'
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
        new_version  = versioning_library.get_new_tag(last_version,args.repo_release_type)

        if args.verbose:
          print 'new version:'
          print new_version

        os.system('git tag '+new_version)
        print "==> Tagged with "+new_version

        release_note_file_handler.write(versioning_library.generate_release_note(project_name, last_version, new_version, args.skip_release_note))

      #### End tag_repo

      # now update manifest
      if manifest_version == 'refs/tags/'+new_version:
        print project_name+": "+"skipping - "+manifest_version+ " to "+new_version
      else:
        print project_name+": "+"updating - "+manifest_version+ " to "+new_version
        output_line = re.sub(r"revision=\".*?\"","revision=\"refs/tags/"+new_version+"\"",line)

    # deal with reference entries by picking up their latest tag and putting it in
    m = re.search('<project name="(.*?)".*?revision="(.*?)".*?groups=".*reference.*"',line)
    if hasattr(m,'group'):

      project_name = m.group(1)
      manifest_version = m.group(2)

      os.system(
        'cd '+workspace+'; rm -fr '+project_name+';'
        +'git clone https://github.com/developerinlondon/'+project_name+'.git; cd '+project_name+';'
        +'git checkout master;'
        )
      last_version = versioning_library.get_last_tag(project_name)
      print project_name+": "+"updating - "+manifest_version+ " to "+last_version
      output_line = re.sub(r"revision=\".*?\"","revision=\"refs/tags/"+last_version+"\"",line)
      os.system('cd '+workspace+'; rm -fr '+project_name+';')

    manifest_file_handler.write(output_line)

  manifest_file_handler.close()
  release_note_file_handler.close()

  os.chdir(workspace+'/'+args.manifest_repo)

  os.system('mv '+release_note_source_file+' '+release_note_destination_file)
  os.system('mv '+outputfile+' '+manifest_file)
  os.system('git add -A')
  os.system('git commit -m"release '+new_manifest_tag+' created"')
  os.system('git tag '+new_manifest_tag)

if args.apply:
  folder = os.listdir(workspace)
  for project in folder:
    if os.path.isdir(workspace + '/' + project):
      print "==> Applying " + project
      os.chdir(workspace + '/' + project)
      os.system('git push --tags')

if args.undo:
  folder = os.listdir(workspace)
  for project in folder:
    if os.path.isdir(workspace + '/' + project):
      tag = versioning_library.get_last_tag(project)
      if tag != '0.0.0':
        os.chdir(workspace+'/'+project)
        print "==> Undoing " + project + " tag "+tag + "----> " + 'git push origin --tags :'+tag
        os.system('git push origin --tags :'+tag)
