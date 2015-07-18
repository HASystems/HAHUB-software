#!/bin/bash

if [ $# -lt 1 ]
then
	echo "$0 <channel number>"
	exit 1
fi

irsend SEND_ONCE RX-V675 KEY_TV
for i in 0 1 2 3
do
	irsend SEND_ONCE U-verse KEY_${1:$i:1}
	sleep 1
done

irsend SEND_ONCE U-Verse KEY_OK

exit 0
