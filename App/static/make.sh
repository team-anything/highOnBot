#!/bin/bash
echo "$1 $2"
echo " Creating $1.cpp "
# touch $1.cpp no need
if [ ! -f $2.$1 ]
then
	cat template.$1 >> $2.$1
  	echo " Ready Set Go! "
  	vim $2.$1
else
 	echo " Sorry ! file already exists "
fi

# track my progress
