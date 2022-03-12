#! /usr/bin/env python3
__doc__ = '''
Make a release of the software. Typically, the version numbers are advanced,
updating a version file.  The git repo is updated with the new version file
and then tagged for that version.
'''

import sys, os, argparse, json, git, re
from make_trinket_export import *
from export_macOS import *

version_labels = ['major', 'minor']
version_file_dirs = [os.path.dirname(sys.argv[0]), '.']
repository_directory = os.path.dirname(os.path.dirname(sys.argv[0]))

def make_release(
      kind: 'Type of version update.  Should be one of version_labels or None',
      force: 'Allow version update even if git working tree is dirty' =False,
      version_filename: 'Name of version file' = 'version.json',
      prefix: 'Prefix of release subdirectory' ='release_',
      repoDir: 'Root directory of git repository' =repository_directory,
      verbose: 'Verbosity of status messages' =0):
   version_path = None
   for dir in version_file_dirs:
      if verbose > 1:
         print('Checking for {} in {}'.format(version_filename, dir))
      if os.path.exists(os.path.join(dir, version_filename)):
         version_path = os.path.join(dir, version_filename)
         if verbose > 1:
            print('Found', version_path)
         break
   if version_path is None:
      msg = 'Unable to find {} among these directories:\n{}'.format(
         version_filename, '\n '.join(dir for dir in version_file_dirs))
      raise Exception(msg)
   try:
      with open(version_path, 'r') as vfile:
         version = json.loads(vfile.read())
   except Exception as e:
      print('Exception raised when reading {} as JSON'.format(version_path), e)
      raise e
   if kind is not None and kind not in version_labels:
      raise ValueError('Kind of release, {}, is not in {}'.format(
         kind, version_labels))
   if kind:
      labelIndex = version_labels.index(kind)
      newVersion = [version[i] if i < labelIndex else
                    version[i] + 1 if i == labelIndex else 0
                    for i in range(len(version))]
      newVersionString = '.'.join(str(v) for v in newVersion)
      print('New version is', newVersionString)
   else:
      newVersion = version
      newVersionString = '.'.join(str(v) for v in newVersion)

   releaseDirectory = prefix + newVersionString
   
   repo = git.Repo(repoDir)
   if repo.is_dirty() and not force:
      raise Exception('Git repository is modified.  Use --force to override')
   elif verbose > 0:
      print('Ignoring unsaved changes to git working directory: {}'.format(
         repo.working_dir))

   if newVersion != version:
      releaseString = 'Release {}'.format(newVersionString)
      with open(version_path, 'w') as vfile:
         vfile.write(json.dumps(newVersion))
      if verbose > 0:
         print('Wrote new version to', version_path)
      repo.index.add([os.path.relpath(repo.working_dir, version_path)])
      result = repo.index.commit(releaseString)
      newTag = repo.create_tag(releaseDirectory.strip().replace(' ', '_'),
                               releaseString)
      if verbose > 1:
         print('Commit of new {} file resulted in:'.format(version_path),
               result, 'which is now tagged {!r}'.format(newTag.name))

   if os.path.exists(releaseDirectory):
      if os.path.isdir(releaseDirectory):
         if verbose > 0:
            print('Release directory already exists: {}'.format(
               releaseDirectory))
      else:
         raise Exception(
            'Release directory is not a directory: {}'.format(
               releaseDirectory))
   else:
      os.mkdir(releaseDirectory)
      
   make_trinket_export(
      os.path.join(releaseDirectory, 'trinket'), verbose=verbose, force=force,
      exclude=[re.compile(exp) for exp in excludeDefaults],
      clean=[re.compile(exp) for exp in cleanDefaults])
   if sys.platform.lower() in ('darwin'):
      if verbose > 0:
         print('Exporting macOS application and disk image...')
      export_macOS(
         version_file=version_path,
         disk_image=os.path.join(releaseDirectory, '{name}{version}.dmg'),
         work_dir=os.path.join(releaseDirectory, 'build'),
         distribution=os.path.join(releaseDirectory, 'dist'),
         verbose=verbose)

if __name__ == '__main__':
   parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument(
      '-u', '--update', default=version_labels[-1],
      choices=version_labels + ['none'],
      help='Update the specified version component, which can be "none".')
   parser.add_argument(
      '-f', '--force', default=False, action='store_true',
      help='Force git update even if working tree directory is "dirty".')
   parser.add_argument(
      '--version-file', default='version.json',
      help='Filename containing current version numbers')
   parser.add_argument(
      '-p', '--prefix', default='release_',
      help='Prefix for release subdirectory and git tag name')
   parser.add_argument(
      '--repository-directory', default=repository_directory,
      help='Repository directory of git working tree')
   parser.add_argument(
      '-v', '--verbose', action='count', default=0,
      help='Add verbose comments')
   args = parser.parse_args()

   make_release(args.update if args.update!= "none" else None,
                args.force, args.version_file, args.prefix,
                args.repository_directory, args.verbose)
