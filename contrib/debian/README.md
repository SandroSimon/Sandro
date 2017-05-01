
Debian
====================
This directory contains files used to package sandrocoind/sandrocoin-qt
for Debian-based Linux systems. If you compile sandrocoind/sandrocoin-qt yourself, there are some useful files here.

## sandrocoin: URI support ##


sandrocoin-qt.desktop  (Gnome / Open Desktop)
To install:

	sudo desktop-file-install sandrocoin-qt.desktop
	sudo update-desktop-database

If you build yourself, you will either need to modify the paths in
the .desktop file or copy or symlink your sandrocoin-qt binary to `/usr/bin`
and the `../../share/pixmaps/sandrocoin128.png` to `/usr/share/pixmaps`

sandrocoin-qt.protocol (KDE)

