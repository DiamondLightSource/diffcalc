#!/bin/sh
if [[ $# -eq 0 ]] ; then
    echo "You must supply a module name"
    exit 1
fi

diffcalc_dir=$(dirname "${BASH_SOURCE}")
working_dir=$PWD

# Add .py suffix to file name if necessary
file_name=$1
if [[ $file_name != *".py" ]]; then
	file_name="$file_name.py"
fi

# Assume file is in examples and check it exists
module_file="example/$file_name"
if [ ! -f "$diffcalc_dir/$module_file" ]; then
    echo "$file_name not found"
    exit 1
fi

echo "Changing current directory to $diffcalc_dir"
cd $diffcalc_dir

command="ipython -i $module_file"
echo "Starting diffcalc with command $command"
$command

echo "Restoring working directory $working_dir"
cd $working_dir
