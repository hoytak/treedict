#!/bin/bash

conditionals="<dict?>
<set?>
<TreeDict?>
<_PTNodeTree?>
<str?>
<list?>
<tuple?>"

if [ "$1" == "debug" ] ; then
    for c in $conditionals; do
	echo "replacing ${c/\?/} with ${c}."
	sed -i "s/${c/\?/}/${c}/g" treedict.pyx
    done
elif [ "$1" == "release" ] ; then
    for c in $conditionals; do
	echo "replacing ${c} with ${c/\?/}."
	sed -i "s/${c}/${c/\?/}/g" treedict.pyx
    done
else 
    echo "Must supply argument 'debug' or 'release'."
fi
