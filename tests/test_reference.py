import commands
import os
import sys,inspect
import re
import unittest

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import versioning_library

class ReferenceTestCase(unittest.TestCase):
  def setUp(self):
    self.cwd = os.getcwd()
    self.workspace = self.cwd+'/workspace'

    os.system( 'rm -fr '+self.workspace+'; mkdir -p '+self.workspace)
    os.chdir(self.workspace)

    os.system(
      "git clone git@github.com:developerinlondon/manifest-test.git;"
      +"git clone git@github.com:developerinlondon/release-test-reference-repo.git;"
    )

    os.chdir('release-test-reference-repo')

    self.release_test_reference_repo_tag="0.1.0"
    print "Applying Tag to release_test_reference_repo_tag "
    os.system('git tag '+self.release_test_reference_repo_tag+'; git add -A; git push origin master --tags;')
    ##################################
    os.chdir('../../..');
    os.system('./manifest_release.py --manifest-release-type hotfix --repo-release-type hotfix --build --manifest-repo manifest-test --manifest-version master;')
    os.system('./manifest_release.py --apply;')

  def testReference(self):
    self.manifest_workspace = self.cwd+'/../workspace'
    self.manifest_file = self.manifest_workspace+'/manifest-test/manifest.xml'
    for line in open(self.manifest_file,'r'):
      output_line = line
      m = re.search('<project name="release-test-reference-repo".*?revision="(.*?)".*?groups="reference"',line)
      if hasattr(m,'group'):
        revision = m.group(1)
        print revision
        self.assertEqual(revision, 'refs/tags/0.1.0')

  def tearDown(self):
    os.chdir(self.workspace+'/../../')
    os.system("./manifest_release.py --undo;")
    os.chdir('tests/workspace')
    os.chdir('release-test-reference-repo')
    os.system('git push origin --tags :0.1.0')


if __name__ == '__main__':
    unittest.main()
