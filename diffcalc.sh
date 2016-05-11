#!/bin/sh
if [[ $# -eq 0 ]] ; then
    echo "You must supply a module name"
    exit 1
fi

diffcalc_dir=`dirname "$BASH_SOURCE"`
working_dir=$PWD

module_file="$diffcalc_dir/example/$1.py"
if [ ! -f $module_file ]; then
    echo "$1 not found"
    exit 1
fi

echo "Changing current directory to $diffcalc_dir"
cd $diffcalc_dir

command="ipython -i example/$1.py"
echo "Starting diffcalc with command $command"
$command

echo "Restoring working directory $working_dir"
cd $working_dir
