#!/usr/bin/env python2
import commands
import os
import sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import versioning_library
import unittest
import re

class ReferenceTestCase(unittest.TestCase):
  def setUp(self):
    self.expected_tag = "refs/tags/0.1.1"

    self.cwd = os.getcwd()
    self.workspace = self.cwd+'/workspace'
    os.system( 'rm -fr '+self.workspace+'; mkdir -p '+self.workspace)
    os.chdir(self.workspace)

    os.system(
      "git config -l; "+
      "git clone git@github.com:developerinlondon/manifest-test.git;"
      +"git clone git@github.com:developerinlondon/release-test-repo.git;"
    )

    os.chdir('release-test-repo')
    self.last_tag_released=commands.getstatusoutput("git tag | tail -n 1")
    os.system('echo "testing new hotfix release '+self.expected_tag+'" >> readme.txt;')
    os.system('git add -A && git commit -m "testing new release version '+self.expected_tag+' && git push origin master;')

    os.chdir('../../..');
    os.system('./manifest_release.py --manifest-release-type hotfix --repo-release-type hotfix --build --verbose --manifest-repo manifest-test --manifest-version master;')
    os.system('./manifest_release.py --apply;')

  def testReleaseTag(self):
    self.manifest_workspace = self.cwd+'/../workspace'
    self.manifest_file = self.manifest_workspace+'/manifest-test/manifest.xml'
    for line in open(self.manifest_file,'r'):
      output_line = line
      m = re.search('<project name="release-test-repo".*?revision="(.*?)".*?',line)
      if hasattr(m,'group'):
        self.revision = m.group(1)
        print self.revision
        self.assertEqual(self.revision , self.expected_tag)

  def tearDown(self):
    os.system("./manifest_release.py --undo;")
    os.chdir("tests/workspace/release-test-repo")
    os.system(
      "git config -l; "+
      " git reset --hard HEAD~1;"
      +" git push origin master -f"
    )


if __name__ == '__main__':
    unittest.main()
