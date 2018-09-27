#!/usr/bin/env python2
import yaml
import argparse
import commands
import os
import versioning_library
from xml.etree.ElementTree import ElementTree

parser = argparse.ArgumentParser(description='Options')
# ths script expects cp_manifest folder to have the manifest configs
parser.add_argument('--type', dest='type', default='minor', action='store', help="Release Type. major/minor/hotfix")
parser.add_argument('--skip-release-note', default=False, dest='skip_release_note', action='store_true', help="Skip Publishing a release_note.txt file")
parser.add_argument('--skip-push', default=False, dest='skip_push', action='store_true', help="skip_Push Mode. Does everything but does not push to remote if --skip_push is passed.")
parser.add_argument('--release-note-file', default='release_note.txt', dest='release_note_file', action='store', help="name of the release_note file")
parser.add_argument('--verbose', default=False, dest='verbose', action='store_true', help="verbose Mode. Spits out more info if in verbose mode")
parser.add_argument('--manifest_tags', default='openshift-cluster', dest='manifest_tags', action='store', help="Name of the Manifest Group to release.")
parser.add_argument('--manifest_file', default='default.xml', dest='manifest_file', action='store', help="Name of the Manifest File to use.")
parser.add_argument('--manifest_branch', default='master', dest='manifest_branch', action='store', help="Name of the Manifest Branch to make the release off of.")
args = parser.parse_args()

repos=[
  # "tf-module-vpc",
  # "tf-module-vpc-peering",
  # "tf-module-vpc-dns",
  # "tf-module-vpn-connection",
  # "tf-module-vpc-s3-endpoint",
  # "tf-module-vpn-gateway",
  # "tf-module-jenkins",
  # "tf-stack-vpc-peering",
  # "tf-module-osmo-openshift",
  # "tf-stack-clusters",
  # "ansible-role-openshift-inventory-gen",
  # "ansible-openshift-preparation",
  # "ansible-role-aws-monitor-scripts",
  # "ansible-role-openshift-postinstall",
  # "ansible-role-openshift-postinstall-secret-enc",
  # "ansible-openshift-users",
  # "ansible-role-openshift-testing",
  # "ansible-role-openshift-mark-provisioned",
  # "ansible-role-fluentd",
  # "ansible-role-openshift-checks",
  # "ansible-role-nix-users",
  # "ansible-role-chrony",
  # "ansible-role-openshift-delete-env-cleanup",
  # "ansible-role-osmo-test-framework",
  # "ansible-role-ossec-wazuh",
  # "ansible-role-pvc-backup",
  # "ansible-role-vault",
  # "ansible-role-transit-vpc",
  # "ansible-role-os-hardening-rhel7",
  # "ansible-role-build-tf-project",
  "osmo"
]

#TODO: need to add some validation code that ensures correct possible values for parameters are passed.

last_release = versioning_library.get_last_release('cp_manifest')
new_release  = versioning_library.get_new_version(last_release,args.type)

# # work out list of repos from cp_manifest
# tree = ElementTree()
# tree.parse('cp_manifest/default.xml')
# current_version = tree.getroot().find("project[@name='"+repo+"']").get('revision')

# run repo on cp_manifest to get the manifest file for the specified group
for repo in repos:
  print "\n==> Processing Repo: "+repo+"\n"
  os.system("./tag-repo.py --repo "+repo+('',' --skip-release-note')[args.skip_release_note]+('',' --skip-push')[args.skip_push]+('',' --verbose')[args.verbose]+" --release-note-file "+args.release_note_file)
  #TODO: we need to ideally capture the new version from tag-repo and pass it to update-osmo-version so we dont have to check out the repo twice!
  os.system("./update-manifest.py --repo "+repo)

os.chdir('../cp_manifest')
print "==> Creating Release Branch: release/"+new_release+"\n"
os.system('git checkout -b release/'+new_release)
# update release note for osmo
versioning_library.generate_release_note('cp_manifest', last_release, new_release, args.release_note_file, args.skip_release_note)

os.system('git add -A')
os.system('git commit -m"release '+new_release+' created"')
os.system('git tag '+new_release)
if args.skip_push:
  print '==> Skipping Pushing!'
else:
  print '==> Pushing Tags and Releases!'
  os.system('git push --tags')
  os.system('git push origin release/'+new_release)
