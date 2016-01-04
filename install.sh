#!/bin/bash


SDIR=$(dirname $0)
BINDIR=~pi/bin
ETCDIR=/etc/hahub
LIBDIR=/usr/local/lib/hahub
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

if [ ! -e $LIBDIR ]; then
	echo "Creating $LIBDIR ..."
	mkdir -p $LIBDIR
else
	if [ ! -d $LIBDIR ]; then
		echo "$LIBDIR exists and is not a directory. Aborting ..."
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
echo "Copying latest ${SDIR}/utils files to $BINDIR ..."
cp -r $SDIR/utils/* $BINDIR
echo "Copying latest ${SDIR}/cli files to $BINDIR ..."
cp -r $SDIR/cli/* $BINDIR

echo "Copying rc.local to /etc/rc.local..."
cp -r $SDIR/etc/rc.local /etc/rc.local

echo "Removing old $ETCDIR files..."
rm -rf $ETCDIR/*
echo "Copying files from ${SDIR}/etc/hahub to $ETCDIR ..."
cp -r $SDIR/etc/hahub/* $ETCDIR

echo "Removing old $LIBDIR files..."
rm -rf $LIBDIR/*
echo "Copying files from ${SDIR}/halib to $LIBDIR ..."
cp -r $SDIR/halib/* $LIBDIR

echo "Copying $SDIR/dev/etc/rc.local to /etc/rc.local"
cp $SDIR/dev/etc/rc.local /etc/rc.local

echo "Done"
