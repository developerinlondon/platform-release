#!/usr/bin/env python2
import yaml
import argparse
import commands
import os
import versioning_library
from xml.etree.ElementTree import ElementTree
import re
import sys
parser = argparse.ArgumentParser(description='Options')
# ths script expects cp_manifest folder to have the manifest configs
parser.add_argument('--type', dest='type', default='minor', action='store', help="Release Type. major/minor/hotfix")
parser.add_argument('--skip-release-note', default=False, dest='skip_release_note', action='store_true', help="Skip Publishing a release_note.txt file")
parser.add_argument('--skip-push', default=False, dest='skip_push', action='store_true', help="skip_Push Mode. Does everything but does not push to remote if --skip_push is passed.")
parser.add_argument('--release-note-file', default='manifest_release_note.txt', dest='release_note_file', action='store', help="name of the release_note file")
parser.add_argument('--verbose', default=False, dest='verbose', action='store_true', help="verbose Mode. Spits out more info if in verbose mode")
parser.add_argument('--release-type', default='minor', dest='release_type', action='store', help="Type of release - major/minor/hotfix")
# parser.add_argument('--manifest_tags', default='openshift-cluster', dest='manifest_tags', action='store', help="Name of the Manifest Group to release.")
# parser.add_argument('--manifest_file', default='default.xml', dest='manifest_file', action='store', help="Name of the Manifest File to use.")
# parser.add_argument('--manifest_branch', default='master', dest='manifest_branch', action='store', help="Name of the Manifest Branch to make the release off of.")
args = parser.parse_args()


#TODO: need to add some validation code that ensures correct possible values for parameters are passed.

# last_release = versioning_library.get_last_release('cp_manifest')
# new_release  = versioning_library.get_new_version(last_release,args.type)
# print "last release "+last_release+" new release"+new_release
# # work out list of repos from cp_manifest
# tree = ElementTree()
# tree.parse('cp_manifest/default.xml')
# current_version = tree.getroot().find("project[@name='"+repo+"']").get('revision')

# run repo on cp_manifest to get the manifest file for the specified group


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
# move old  

filename = 'default.xml'
outputfile = 'output.xml'
release_note_file = 'release.txt'

f = open(outputfile,'w')
r = open(release_note_file,'w')
for line in open(filename,'r'):
  output_line = line
  m = re.search('<project name="(.*?)".*?revision="(.*?)"',line)
  if hasattr(m,'group'):
    project_name = m.group(1)
    manifest_version = m.group(2)
    # last_version = versioning_library.get_last_tag(project_name) # this is the version thats on the repo currently
    # new_version  = versioning_library.get_new_version(last_version,args.release_type)


    #### tag repo
    os.system(
      'cd /tmp; mkdir -p manifest-workspace; cd manifest-workspace; rm -fr '+project_name+';'
      +'git clone git@bitbucket.org:motabilityoperations/'+project_name+'.git; cd '+project_name+';'
      +'git checkout master'
      )
    cwd = os.getcwd()

    os.chdir('/tmp/manifest-workspace/'+project_name)

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
      if args.skip_push:
        print "==> Skipped Pushing as '--skip-push' passed!"
      else:
        os.system('git push --tags')
        print "==> Pushed new tag "+new_version

      r.write(versioning_library.generate_release_note(project_name, last_version, new_version, args.skip_release_note))

    #### End tag_repo

    # now update manifest
    if manifest_version == 'refs/tags/'+new_version:
      print project_name+": "+"skipping - "+manifest_version+ " to "+new_version
    else:
      print project_name+": "+"updating - "+manifest_version+ " to "+new_version
      output_line = re.sub(r"revision=\".*?\"","revision=\"refs/tags/"+new_version+"\"",line)
      #manifest_version = re.sub(r'refs/tags/','',manifest_version)
      #os.system("./tag-repo.py --repo "+project_name+('',' --skip-release-note')[args.skip_release_note]+('',' --skip-push')[args.skip_push]+('',' --verbose')[args.verbose]+" --release-note-file "+args.release_note_file)
      #versioning_library.generate_release_note(project_name, manifest_version, new_version, 'release_note.txt', 0)
  f.write(output_line)
f.close()
r.close()

# for repo in repos:
#   print "\n==> Processing Repo: "+repo+"\n"
#   os.system("./tag-repo.py --repo "+repo+('',' --skip-release-note')[args.skip_release_note]+('',' --skip-push')[args.skip_push]+('',' --verbose')[args.verbose]+" --release-note-file "+args.release_note_file)
#   #TODO: we need to ideally capture the new version from tag-repo and pass it to update-osmo-version so we dont have to check out the repo twice!
#   os.system("./update-manifest.py --repo "+repo)

# os.chdir('../cp_manifest')
# # print "==> Creating Release Branch: release/"+new_release+"\n"
# # os.system('git checkout -b release/'+new_release)
# # update release note for osmo
# versioning_library.generate_release_note('cp_manifest', last_release, new_release, args.release_note_file, args.skip_release_note)

# os.system('git add -A')
# os.system('git commit -m"release '+new_release+' created"')
# os.system('git tag '+new_release)
# if args.skip_push:
#   print '==> Skipping Pushing!'
# else:
#   print '==> Pushing Tags and Releases!'
#   os.system('git push --tags')
#   os.system('git push origin release/'+new_release)
