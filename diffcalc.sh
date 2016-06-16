#!/bin/sh
if [[ $# -eq 0 ]] ; then
    echo "You must supply a module name"
    exit 1
fi

diffcalc_dir=$(dirname "${BASH_SOURCE}")

# Add .py suffix to file name if necessary
file_name=$1
if [[ $file_name != *".py" ]]; then
	file_name="$file_name.py"
fi

# Assume file is in examples and check it exists
module_file="$diffcalc_dir/example/$file_name"
if [ ! -f "$module_file" ]; then
    echo "$file_name not found"
    exit 1
fi

command="ipython -i $module_file"
echo "Starting diffcalc with command $command"
$command
