#! /usr/bin/env python3
__doc__ = '''
Make a release of the visualization software. Typically, the
version numbers are advanced, updating a version file.  The git repo
is updated with the new version file and then tagged for that version.
'''

import sys, os, argparse, json, git, re, shutil
from export_common import *
from export_trinket import *
from export_macOS import *
from export_windows import *

version_labels = ['major', 'minor']
platforms = ['trinket', 'macOS', 'windows']
version_file_dirs = [os.path.dirname(sys.argv[0]), '.']
repository_directory = os.path.dirname(
   os.path.abspath(os.path.dirname(sys.argv[0])))
source_directory = os.path.join(repository_directory, 'PythonVisualizations')

def make_release(
      kind: 'Type of version update.  Should be one of version_labels or None',
      source_directory: 'Directory containing source and PNG files' = '.',
      force: 'Allow version update even if git working tree is dirty' =False,
      version_filename: 'Name of version file' ='version.json',
      targets: 'Platforms to be exported. Must be members of platforms' =platforms,
      prefix: 'Prefix of release subdirectory' ='release_',
      backup: 'Suffix for backup of any existing release directory' = '.bak',
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
      print('New version will be', newVersionString)
   else:
      newVersion = version
      newVersionString = '.'.join(str(v) for v in newVersion)

   releaseDirectory = prefix + newVersionString
   
   repo = git.Repo(repoDir)
   if repo.is_dirty() and not force:
      raise Exception('Git repository is modified.  Use --force to override.')
   elif verbose > 0:
      print('Ignoring unsaved changes to git working directory: {}'.format(
         repo.working_dir))

   if newVersion != version:
      tagName = releaseDirectory.strip().replace(' ', '_')
      matchingTags = [tag for tag in repo.tags if tag.name == tagName]
      if matchingTags:
         if force:
            if verbose > 1:
               print('Deleting {} existing tag{} named {!r}'.format(
                  len(matchingTags), '' if len(matchingTags) == 1 else 's',
                  tagName))
            repo.delete_tag(*matchingTags)
         else:
            raise Exception(
               'Tag {!r} already exists.  Use --force option to delete.'.format(
                  tagName))
         
      releaseString = 'Release {}'.format(newVersionString)
      with open(version_path, 'w') as vfile:
         vfile.write(json.dumps(newVersion))
      if verbose > 0:
         print('Wrote new version, {}, to {}'.format(
            newVersionString, version_path))
      repo.index.add([os.path.relpath(version_path, repo.working_dir)])
      commit = repo.index.commit(releaseString)
      newTag = repo.create_tag(tagName, message=releaseString, force=force)
      print('Commit of new {} file resulted in:'.format(version_path),
            commit, 'which is now tagged {!r}'.format(newTag.name))

   if os.path.exists(releaseDirectory):
      if not os.path.isdir(releaseDirectory):
         raise Exception(
            'Release directory is not a directory: {}'.format(
               releaseDirectory))
      if backup:
         backupFiles((releaseDirectory,), backup, verbose)
         os.mkdir(releaseDirectory)
      elif verbose > 0:
         print('Release directory, {}, already exists '
               'and no backup specified'.format(releaseDirectory))
   else:
      os.mkdir(releaseDirectory)

   border = '=' * 72
   targetAnnounce = '{}\n        Export target -> {{}}\n{}'.format(
      border, border)
   if 'trinket' in targets:
      if verbose > 0:
         print(targetAnnounce.format('trinket'))
      export_trinket(
         os.path.join(releaseDirectory, 'trinket'),
         source_directory=source_directory, verbose=verbose,
         force=force, exclude=[re.compile(exp) for exp in excludeDefaults],
         clean=[re.compile(exp) for exp in cleanDefaults])
   if 'macOS' in targets:
      if sys.platform.lower() in ('darwin'):
         if verbose > 0:
            print(targetAnnounce.format('macOS'))
         export_macOS(
            version_file=version_path, source_directory=source_directory, 
            disk_image=os.path.join(releaseDirectory, '{name}{version}.dmg'),
            work_dir=os.path.join(releaseDirectory, 'build'),
            distribution=os.path.join(releaseDirectory, 'dist'),
            verbose=verbose)
      elif verbose > 0:
         print('Skipping {} export since current platform is {}'.format(
            'macOS', sys.platform))
   if 'windows' in targets:
      if sys.platform.lower().startswith('win'):
         if verbose > 0:
            print(targetAnnounce.format('Windows'))
         # TBD export_windows()
      elif verbose > 0:
         print('Skipping {} export since current platform is {}'.format(
            'windows', sys.platform))
         
   print('Completed release in {}'.format(releaseDirectory))

if __name__ == '__main__':
   parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument(
      '-u', '--update', default=version_labels[-1],
      choices=version_labels + ['none'],
      help='Update the specified version component, which can be "none".')
   parser.add_argument(
      '-s', '--source', default=source_directory,
      help='Directory containing source Python and PNG files')
   parser.add_argument(
      '-f', '--force', default=False, action='store_true',
      help='Force git update even if working tree directory is "dirty".')
   parser.add_argument(
      '--version-file', default='version.json',
      help='Filename containing current version numbers')
   parser.add_argument(
      '-t', '--target', metavar='PLATFORM', choices=platforms + ['all'],
      nargs='*', default=['all'],
      help=('Export release to target platform. Possible platforms: {}. '
            'Some platforms can only be exported when run on that platform').format(
               ', '.join(platforms)))
   parser.add_argument(
      '-p', '--prefix', default='release_',
      help='Prefix for release subdirectory and git tag name')
   parser.add_argument(
      '--repository-directory', default=repository_directory,
      help='Repository directory of git working tree')
   parser.add_argument(
      '-b', '--backup', default='.bak',
      help='File extension for backup of last release')
   parser.add_argument(
      '-v', '--verbose', action='count', default=0,
      help='Add verbose comments')
   args = parser.parse_args()

   if 'all' in args.target:
      args.target = platforms

   make_release(
      args.update if args.update.lower() != "none" else None,
      source_directory=args.source, force=args.force,
      version_filename=args.version_file, prefix=args.prefix,
      targets=args.target, repoDir=args.repository_directory,
      backup=args.backup, verbose=args.verbose)
