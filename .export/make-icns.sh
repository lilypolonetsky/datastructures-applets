#! /usr/bin/env bash

# Script to make a macOS icon set from a PNG image
prog=`basename $0`
usage="$prog PNG-file [ICNS-dir]"

if (( $# < 1 )) ; then
    echo $prog: too few arguments
    echo Usage: $usage
    exit -1
fi

in_filepath="$1"

stem="${2-$in_filepath}"
stem=${stem%.png}
stem=${stem%.PNG}
out_iconset_name="${stem}.iconset"

# echo in_filepath = $in_filepath
# echo out_iconset_name = $out_iconset_name
mkdir "$out_iconset_name"

sips -z 16 16     $in_filepath --out "${out_iconset_name}/icon_16x16.png"
sips -z 32 32     $in_filepath --out "${out_iconset_name}/icon_16x16@2x.png"
sips -z 32 32     $in_filepath --out "${out_iconset_name}/icon_32x32.png"
sips -z 64 64     $in_filepath --out "${out_iconset_name}/icon_32x32@2x.png"
sips -z 128 128   $in_filepath --out "${out_iconset_name}/icon_128x128.png"
sips -z 256 256   $in_filepath --out "${out_iconset_name}/icon_128x128@2x.png"
sips -z 256 256   $in_filepath --out "${out_iconset_name}/icon_256x256.png"
sips -z 512 512   $in_filepath --out "${out_iconset_name}/icon_256x256@2x.png"
sips -z 512 512   $in_filepath --out "${out_iconset_name}/icon_512x512.png"

iconutil -c icns $out_iconset_name && rm -R $out_iconset_name

