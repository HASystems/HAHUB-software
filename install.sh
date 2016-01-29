#!/bin/bash

USER=pi

DEVDIR=`eval echo ~$USER`/dev
BINDIR=/usr/local/bin/
HABINDIR=$BINDIR/hahub
ETCDIR=/etc/hahub
LIBDIR=/usr/local/lib/hahub
VARLOGDIR=/var/log/hahub

echo "Checking all required directory paths ..."
if [ ! -e $HABINDIR ]; then
	echo "Creating $HABINDIR ..."
	mkdir -p $HABINDIR
else
	if [ ! -d $HABINDIR ]; then
		echo "$HABINDIR exists and is not a directory. Aborting ..."
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
echo

echo "Removing old $HABINDIR files..."
rm -rf $HABINDIR/*
echo "Copying latest ${DEVDIR}/utils files to $HABINDIR ..."
cp -r $DEVDIR/utils/* $HABINDIR
echo "Copying latest ${DEVDIR}/cli files to $HABINDIR ..."
cp -r $DEVDIR/cli/* $HABINDIR
echo "Linking files in $HABINDIR to $BINDIR ..."
for f in $( ls $HABINDIR ); do
	rm $BINDIR/$f
	ln -s $HABINDIR/$f $BINDIR
done
echo "Removing any broken symbolic links left behind ..."
for f in $( ls $BINDIR ); do
	if [ -h $BINDIR/$f -a ! -e $BINDIR/$f ]; then
		echo "REMOVING $BINDIR/$f ..."
		rm $BINDIR/$f
	fi
done
echo

echo "Removing old $ETCDIR files..."
rm -rf $ETCDIR/*
echo "Copying files from ${DEVDIR}/etc/hahub to $ETCDIR ..."
cp -r $DEVDIR/etc/hahub/* $ETCDIR
echo

echo "Removing old $LIBDIR files..."
rm -rf $LIBDIR/*
echo "Copying files from ${DEVDIR}/halib to $LIBDIR ..."
cp -r $DEVDIR/halib/* $LIBDIR
echo

echo "Uninstalling hahub-svcs..."
insserv --remove hahub-svcs
echo "Copying current habub-svcs script to /etc/init.d ..."
cp $DEVDIR/init.d/hahub-svcs /etc/init.d/hahub-svcs
echo "Installing current hahub-svcs in runlevels ..."
insserv hahub-svcs
echo

echo "Done"
