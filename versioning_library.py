import commands
import os
import re
import string
import sys

def get_last_tag(repo_name):
  version = commands.getstatusoutput("git ls-remote --tags git@bitbucket.org:motabilityoperations/"+repo_name+" 2>/dev/null | awk -F/ -f "+os.path.dirname(os.path.realpath(__file__))+"/latest_tag.awk")
  if version[1] == '':
    return '0.0.0'
  else:
    return version[1]

# get all the branches starting with the word 'release' to find out what the last release branch was then create a new release branch
def get_last_release(repo_name):
    version = commands.getstatusoutput('git ls-remote --heads git@bitbucket.org:motabilityoperations/'+repo_name+' 2>/dev/null  | cut -f3,4 -d"/" | grep release | tail -1 | cut -f2 -d"/"')
    if version[1] == '':
      return '0.0.0'
    else:
      return version[1]

def insert_to_file(originalfile,string):
    print "==> updating release note on "+originalfile
    os.system('touch '+originalfile)
    with open(originalfile,'r') as f:
        with open('newfile.txt','w+') as f2: 
            f2.write(string+"\n\n")
            initial_content = f.read()
            f2.write(initial_content)
    os.rename('newfile.txt',originalfile)

def get_new_version(last_version,release_type='minor'):
    version_bits=last_version.split('.')
    # bump version
    if release_type == 'major':
      version_bits[0] = str(int(version_bits[0])+1)
      version_bits[1] = '0'
    elif release_type == 'minor':
      version_bits[1] = str(int(version_bits[1])+1)
    elif release_type == 'hotfix':
      print "\nCRITICAL ERROR: 'hotfix' releases are not currently supported. Please pass 'release-type' of 'major' or 'minor'.\n"
      exit()  
    version_bits[2] = '0'   # hotfix version is always zero, release type 'hotfix' is not currently supported.

    new_version = '.'.join(version_bits)
    print "new version is: "+new_version
    return new_version

def generate_release_note(repo_name, last_version, new_version, empty_release_note):
  print 'last:'+last_version
  print 'new:'+new_version
  if empty_release_note:
    print "==> Skipping Creating Release Note"
  else:
    if last_version == '0.0.0':
      log_filter = ''
    else:
      pattern = re.compile("^(\d+\.\d+)\.\d+$")
      match = pattern.match(last_version)
      if hasattr(match,'group'):
        log_filter = match.group(1)+'.0..HEAD '
      else:
        log_filter = ''
    
    release_note = repo_name+" "+new_version+"\n"+"-"*len(repo_name+" "+new_version)+"\n"
    release_note = release_note+commands.getstatusoutput("git log "+log_filter+' --pretty=format:%s')[1] + "\n\n"
    
    return release_note
    # insert_to_file(release_note_file,release_note)
    # print "==> Release Note added to "+release_note_file

def update_tag(filename, repo, new_tag, outputfile):
  f = open(outputfile,'w')
  for line in open(filename,'r'):
    output_line = line
    if re.match(r'.*?project name="'+repo+'".*?', output_line):
      output_line=commands.getstatusoutput('echo \''+output_line+'\' | sed  \'s/revision=\\"[^"]*\\"/revision=\\"'+new_tag+'\\"/\'')[1]
    f.write(output_line)
    sys.stdout.write(output_line)
  f.close()
