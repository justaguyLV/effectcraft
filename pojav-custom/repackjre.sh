#!/bin/bash
# Vendored from PojavLauncherTeam/android-openjdk-build-multiarch (branch buildjre17-21); see that repository for its license.
# Modified: tolerate files that some builds lack (lib/jexec, lib/jvm.cfg, release) instead of aborting.
set -e

## Usage:
## ./repackjre.sh [path_to_normal_jre_tarballs] [output_path]

# set args
export in="$1"
export out="$2"

# set working dirs
work="$in/work"
work1="$in/work1"

# make sure paths exist
mkdir -p $work
mkdir -p $work1
mkdir -p "$out"

copyjvmlib() {
  if [[ -d lib/$1 ]]; then
    echo "Moving $1 VM for $2"
    mv lib/$1 "$work1"/lib/;
  fi
}

# here comes a not-so-complicated functions to easily make desired arch
## Usage: makearch [jre_libs_dir_name] [name_in_tarball]
makearch () {
  echo "Making $2...";
  cd "$work";
  tar xf $(find "$in" -name jre${TARGET_VERSION}-$2-*release.tar.xz) > /dev/null 2>&1;
  mv bin "$work1"/;
  mkdir -p "$work1"/lib;
  
  #mv lib/$1 "$work1"/lib/;
  [ -e lib/jexec ] && mv lib/jexec "$work1"/lib/ || true
  [ -e lib/jvm.cfg ] && mv lib/jvm.cfg "$work1"/lib/ || true
  
  # server contains the libjvm.so
  copyjvmlib server $2
  copyjvmlib client $2
  
  
  # All the other .so files are at the root of the lib folder
  find ./ -name '*.so' -execdir mv {} "$work1"/lib/{} \;
  
  [ -e release ] && mv release "$work1"/release || true
  
  XZ_OPT="-6 --threads=0" tar cJf bin-$2.tar.xz -C "$work1" . > /dev/null;
  mv bin-$2.tar.xz "$out"/;
  rm -rf "$work"/*;
  rm -rf "$work1"/*;
 }

# this one's static
makeuni () {
  echo "Making universal...";
  cd "$work";
  tar xf $(find "$in" -name jre${TARGET_VERSION}-arm64-*release.tar.xz) > /dev/null 2>&1;
  
  rm -rf bin;
  rm -rf lib/server;
  rm -f lib/jexec;
  rm -f lib/jvm.cfg;
  find ./ -name '*.so' -execdir rm {} \; # Remove arch specific shared objects
  rm -f release
  
  XZ_OPT="-6 --threads=0" tar cJf universal.tar.xz * > /dev/null;
  mv universal.tar.xz "$out"/;
  rm -rf "$work"/*;
 }

# now time to use them!
makeuni
makearch aarch32 arm
makearch aarch64 arm64
makearch i386 x86
makearch amd64 x86_64

# if running under GitHub Actions, write commit sha, else formatted system date
if [[ -n "$GITHUB_SHA" ]]
then
echo $GITHUB_SHA>"$out"/version
else
date +%Y%m%d>"$out"/version
fi
