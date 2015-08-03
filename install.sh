#!/bin/bash


SDIR=$(dirname $0)
BINDIR=~pi/bin
ETCDIR=/etc/hahub
VARLOGDIR=/var/log/hahub

if [ ! -e $BINDIR ]; then
	echo "Creating $BINDIR ..."
	mkdir -p $BINDIR
else
	if [ ! -d $BINDIR ]; then
		echo "$BINDIR exists and is not a directory. Aborting ..."
		exit 1
	fi
fi

if [ ! -e $ETCDIR ]; then
	echo "Creating $ETCDIR ..."
	mkdir -p $ETCDIR
else
	if [ ! -d $ETCDIR ]; then
		echo "$ETCDIR exists and is not a directory. Aborting ..."
		exit 1
	fi
fi

if [ ! -e $VARLOGDIR ]; then
	echo "Creating $VARLOGDIR ..."
	mkdir -p $VARLOGDIR
else
	if [ ! -d $VARLOGDIR ]; then
		echo "$VARLOGDIR exists and is not a directory. Aborting ..."
		exit 1
	fi
fi

echo "Removing old $BINDIR files..."
rm -rf $BINDIR/*
echo "Copying latest ~/bin files..."
cp $SDIR/bin/* $BINDIR
echo "Copying latest ~/client files..."
cp -r $SDIR/client/* $BINDIR

echo "Copying rc.local to /etc/rc.local..."
cp $SDIR/etc/rc.local /etc/rc.local

echo "Removing old $ETCDIR files..."
rm -rf $ETCDIR/*
echo "Copying files to $ETCDIR ..."
cp -r $SDIR/etc/hahub/* $ETCDIR

echo "Setting log level to Warn ..."
/etc/hahub/setlogwarn
echo "Done"
