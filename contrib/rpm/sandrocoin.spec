%define bdbv 4.8.30
%global selinux_variants mls strict targeted

%if 0%{?_no_gui:1}
%define _buildqt 0
%define buildargs --with-gui=no
%else
%define _buildqt 1
%if 0%{?_use_qt4}
%define buildargs --with-qrencode --with-gui=qt4
%else
%define buildargs --with-qrencode --with-gui=qt5
%endif
%endif

Name:		sandrocoin
Version:	0.12.0
Release:	2%{?dist}
Summary:	Peer to Peer Cryptographic Currency

Group:		Applications/System
License:	MIT
URL:		https://sandrocoin.org/
Source0:	https://sandrocoin.org/bin/sandrocoin-core-%{version}/sandrocoin-%{version}.tar.gz
Source1:	http://download.oracle.com/berkeley-db/db-%{bdbv}.NC.tar.gz

Source10:	https://raw.githubusercontent.com/sandrocoin/sandrocoin/v%{version}/contrib/debian/examples/sandrocoin.conf

#man pages
Source20:	https://raw.githubusercontent.com/sandrocoin/sandrocoin/v%{version}/doc/man/sandrocoind.1
Source21:	https://raw.githubusercontent.com/sandrocoin/sandrocoin/v%{version}/doc/man/sandrocoin-cli.1
Source22:	https://raw.githubusercontent.com/sandrocoin/sandrocoin/v%{version}/doc/man/sandrocoin-qt.1

#selinux
Source30:	https://raw.githubusercontent.com/sandrocoin/sandrocoin/v%{version}/contrib/rpm/sandrocoin.te
# Source31 - what about sandrocoin-tx and bench_sandrocoin ???
Source31:	https://raw.githubusercontent.com/sandrocoin/sandrocoin/v%{version}/contrib/rpm/sandrocoin.fc
Source32:	https://raw.githubusercontent.com/sandrocoin/sandrocoin/v%{version}/contrib/rpm/sandrocoin.if

Source100:	https://upload.wikimedia.org/wikipedia/commons/4/46/Sandrocoin.svg

%if 0%{?_use_libressl:1}
BuildRequires:	libressl-devel
%else
BuildRequires:	openssl-devel
%endif
BuildRequires:	boost-devel
BuildRequires:	miniupnpc-devel
BuildRequires:	autoconf automake libtool
BuildRequires:	libevent-devel


Patch0:		sandrocoin-0.12.0-libressl.patch


%description
Sandrocoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of sandrocoins is carried out collectively by the network.

%if %{_buildqt}
%package core
Summary:	Peer to Peer Cryptographic Currency
Group:		Applications/System
Obsoletes:	%{name} < %{version}-%{release}
Provides:	%{name} = %{version}-%{release}
%if 0%{?_use_qt4}
BuildRequires:	qt-devel
%else
BuildRequires:	qt5-qtbase-devel
# for /usr/bin/lrelease-qt5
BuildRequires:	qt5-linguist
%endif
BuildRequires:	protobuf-devel
BuildRequires:	qrencode-devel
BuildRequires:	%{_bindir}/desktop-file-validate
# for icon generation from SVG
BuildRequires:	%{_bindir}/inkscape
BuildRequires:	%{_bindir}/convert

%description core
Sandrocoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of sandrocoins is carried out collectively by the network.

This package contains the Qt based graphical client and node. If you are looking
to run a Sandrocoin wallet, this is probably the package you want.
%endif


%package libs
Summary:	Sandrocoin shared libraries
Group:		System Environment/Libraries

%description libs
This package provides the sandrocoinconsensus shared libraries. These libraries
may be used by third party software to provide consensus verification
functionality.

Unless you know need this package, you probably do not.

%package devel
Summary:	Development files for sandrocoin
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This package contains the header files and static library for the
sandrocoinconsensus shared library. If you are developing or compiling software
that wants to link against that library, then you need this package installed.

Most people do not need this package installed.

%package server
Summary:	The sandrocoin daemon
Group:		System Environment/Daemons
Requires:	sandrocoin-utils = %{version}-%{release}
Requires:	selinux-policy policycoreutils-python
Requires(pre):	shadow-utils
Requires(post):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
Requires(postun):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
BuildRequires:	systemd
BuildRequires:	checkpolicy
BuildRequires:	%{_datadir}/selinux/devel/Makefile

%description server
This package provides a stand-alone sandrocoin-core daemon. For most users, this
package is only needed if they need a full-node without the graphical client.

Some third party wallet software will want this package to provide the actual
sandrocoin-core node they use to connect to the network.

If you use the graphical sandrocoin-core client then you almost certainly do not
need this package.

%package utils
Summary:	Sandrocoin utilities
Group:		Applications/System

%description utils
This package provides several command line utilities for interacting with a
sandrocoin-core daemon.

The sandrocoin-cli utility allows you to communicate and control a sandrocoin daemon
over RPC, the sandrocoin-tx utility allows you to create a custom transaction, and
the bench_sandrocoin utility can be used to perform some benchmarks.

This package contains utilities needed by the sandrocoin-server package.


%prep
%setup -q
%patch0 -p1 -b .libressl
cp -p %{SOURCE10} ./sandrocoin.conf.example
tar -zxf %{SOURCE1}
cp -p db-%{bdbv}.NC/LICENSE ./db-%{bdbv}.NC-LICENSE
mkdir db4 SELinux
cp -p %{SOURCE30} %{SOURCE31} %{SOURCE32} SELinux/


%build
CWD=`pwd`
cd db-%{bdbv}.NC/build_unix/
../dist/configure --enable-cxx --disable-shared --with-pic --prefix=${CWD}/db4
make install
cd ../..

./autogen.sh
%configure LDFLAGS="-L${CWD}/db4/lib/" CPPFLAGS="-I${CWD}/db4/include/" --with-miniupnpc --enable-glibc-back-compat %{buildargs}
make %{?_smp_mflags}

pushd SELinux
for selinuxvariant in %{selinux_variants}; do
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile
	mv sandrocoin.pp sandrocoin.pp.${selinuxvariant}
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile clean
done
popd


%install
make install DESTDIR=%{buildroot}

mkdir -p -m755 %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/sandrocoind %{buildroot}%{_sbindir}/sandrocoind

# systemd stuff
mkdir -p %{buildroot}%{_tmpfilesdir}
cat <<EOF > %{buildroot}%{_tmpfilesdir}/sandrocoin.conf
d /run/sandrocoind 0750 sandrocoin sandrocoin -
EOF
touch -a -m -t 201504280000 %{buildroot}%{_tmpfilesdir}/sandrocoin.conf

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cat <<EOF > %{buildroot}%{_sysconfdir}/sysconfig/sandrocoin
# Provide options to the sandrocoin daemon here, for example
# OPTIONS="-testnet -disable-wallet"

OPTIONS=""

# System service defaults.
# Don't change these unless you know what you're doing.
CONFIG_FILE="%{_sysconfdir}/sandrocoin/sandrocoin.conf"
DATA_DIR="%{_localstatedir}/lib/sandrocoin"
PID_FILE="/run/sandrocoind/sandrocoind.pid"
EOF
touch -a -m -t 201504280000 %{buildroot}%{_sysconfdir}/sysconfig/sandrocoin

mkdir -p %{buildroot}%{_unitdir}
cat <<EOF > %{buildroot}%{_unitdir}/sandrocoin.service
[Unit]
Description=Sandrocoin daemon
After=syslog.target network.target

[Service]
Type=forking
ExecStart=%{_sbindir}/sandrocoind -daemon -conf=\${CONFIG_FILE} -datadir=\${DATA_DIR} -pid=\${PID_FILE} \$OPTIONS
EnvironmentFile=%{_sysconfdir}/sysconfig/sandrocoin
User=sandrocoin
Group=sandrocoin

Restart=on-failure
PrivateTmp=true
TimeoutStopSec=120
TimeoutStartSec=60
StartLimitInterval=240
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF
touch -a -m -t 201504280000 %{buildroot}%{_unitdir}/sandrocoin.service
#end systemd stuff

mkdir %{buildroot}%{_sysconfdir}/sandrocoin
mkdir -p %{buildroot}%{_localstatedir}/lib/sandrocoin

#SELinux
for selinuxvariant in %{selinux_variants}; do
	install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
	install -p -m 644 SELinux/sandrocoin.pp.${selinuxvariant} %{buildroot}%{_datadir}/selinux/${selinuxvariant}/sandrocoin.pp
done

%if %{_buildqt}
# qt icons
install -D -p share/pixmaps/sandrocoin.ico %{buildroot}%{_datadir}/pixmaps/sandrocoin.ico
install -p share/pixmaps/nsis-header.bmp %{buildroot}%{_datadir}/pixmaps/
install -p share/pixmaps/nsis-wizard.bmp %{buildroot}%{_datadir}/pixmaps/
install -p %{SOURCE100} %{buildroot}%{_datadir}/pixmaps/sandrocoin.svg
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/sandrocoin16.png -w16 -h16
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/sandrocoin32.png -w32 -h32
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/sandrocoin64.png -w64 -h64
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/sandrocoin128.png -w128 -h128
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/sandrocoin256.png -w256 -h256
%{_bindir}/convert -resize 16x16 %{buildroot}%{_datadir}/pixmaps/sandrocoin256.png %{buildroot}%{_datadir}/pixmaps/sandrocoin16.xpm
%{_bindir}/convert -resize 32x32 %{buildroot}%{_datadir}/pixmaps/sandrocoin256.png %{buildroot}%{_datadir}/pixmaps/sandrocoin32.xpm
%{_bindir}/convert -resize 64x64 %{buildroot}%{_datadir}/pixmaps/sandrocoin256.png %{buildroot}%{_datadir}/pixmaps/sandrocoin64.xpm
%{_bindir}/convert -resize 128x128 %{buildroot}%{_datadir}/pixmaps/sandrocoin256.png %{buildroot}%{_datadir}/pixmaps/sandrocoin128.xpm
%{_bindir}/convert %{buildroot}%{_datadir}/pixmaps/sandrocoin256.png %{buildroot}%{_datadir}/pixmaps/sandrocoin256.xpm
touch %{buildroot}%{_datadir}/pixmaps/*.png -r %{SOURCE100}
touch %{buildroot}%{_datadir}/pixmaps/*.xpm -r %{SOURCE100}

# Desktop File - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/applications
cat <<EOF > %{buildroot}%{_datadir}/applications/sandrocoin-core.desktop
[Desktop Entry]
Encoding=UTF-8
Name=Sandrocoin
Comment=Sandrocoin P2P Cryptocurrency
Comment[fr]=Sandrocoin, monnaie virtuelle cryptographique pair à pair
Comment[tr]=Sandrocoin, eşten eşe kriptografik sanal para birimi
Exec=sandrocoin-qt %u
Terminal=false
Type=Application
Icon=sandrocoin128
MimeType=x-scheme-handler/sandrocoin;
Categories=Office;Finance;
EOF
# change touch date when modifying desktop
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/applications/sandrocoin-core.desktop
%{_bindir}/desktop-file-validate %{buildroot}%{_datadir}/applications/sandrocoin-core.desktop

# KDE protocol - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/kde4/services
cat <<EOF > %{buildroot}%{_datadir}/kde4/services/sandrocoin-core.protocol
[Protocol]
exec=sandrocoin-qt '%u'
protocol=sandrocoin
input=none
output=none
helper=true
listing=
reading=false
writing=false
makedir=false
deleting=false
EOF
# change touch date when modifying protocol
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/kde4/services/sandrocoin-core.protocol
%endif

# man pages
install -D -p %{SOURCE20} %{buildroot}%{_mandir}/man1/sandrocoind.1
install -p %{SOURCE21} %{buildroot}%{_mandir}/man1/sandrocoin-cli.1
%if %{_buildqt}
install -p %{SOURCE22} %{buildroot}%{_mandir}/man1/sandrocoin-qt.1
%endif

# nuke these, we do extensive testing of binaries in %%check before packaging
rm -f %{buildroot}%{_bindir}/test_*

%check
make check
pushd src
srcdir=. test/sandrocoin-util-test.py
popd
qa/pull-tester/rpc-tests.py -extended

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%pre server
getent group sandrocoin >/dev/null || groupadd -r sandrocoin
getent passwd sandrocoin >/dev/null ||
	useradd -r -g sandrocoin -d /var/lib/sandrocoin -s /sbin/nologin \
	-c "Sandrocoin wallet server" sandrocoin
exit 0

%post server
%systemd_post sandrocoin.service
# SELinux
if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
for selinuxvariant in %{selinux_variants}; do
	%{_sbindir}/semodule -s ${selinuxvariant} -i %{_datadir}/selinux/${selinuxvariant}/sandrocoin.pp &> /dev/null || :
done
%{_sbindir}/semanage port -a -t sandrocoin_port_t -p tcp 9332
%{_sbindir}/semanage port -a -t sandrocoin_port_t -p tcp 9333
%{_sbindir}/semanage port -a -t sandrocoin_port_t -p tcp 19332
%{_sbindir}/semanage port -a -t sandrocoin_port_t -p tcp 19333
%{_sbindir}/fixfiles -R sandrocoin-server restore &> /dev/null || :
%{_sbindir}/restorecon -R %{_localstatedir}/lib/sandrocoin || :
fi

%posttrans server
%{_bindir}/systemd-tmpfiles --create

%preun server
%systemd_preun sandrocoin.service

%postun server
%systemd_postun sandrocoin.service
# SELinux
if [ $1 -eq 0 ]; then
	if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
	%{_sbindir}/semanage port -d -p tcp 9332
	%{_sbindir}/semanage port -d -p tcp 9333
	%{_sbindir}/semanage port -d -p tcp 19332
	%{_sbindir}/semanage port -d -p tcp 19333
	for selinuxvariant in %{selinux_variants}; do
		%{_sbindir}/semodule -s ${selinuxvariant} -r sandrocoin &> /dev/null || :
	done
	%{_sbindir}/fixfiles -R sandrocoin-server restore &> /dev/null || :
	[ -d %{_localstatedir}/lib/sandrocoin ] && \
		%{_sbindir}/restorecon -R %{_localstatedir}/lib/sandrocoin &> /dev/null || :
	fi
fi

%clean
rm -rf %{buildroot}

%if %{_buildqt}
%files core
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING sandrocoin.conf.example doc/README.md doc/bips.md doc/files.md doc/multiwallet-qt.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_bindir}/sandrocoin-qt
%attr(0644,root,root) %{_datadir}/applications/sandrocoin-core.desktop
%attr(0644,root,root) %{_datadir}/kde4/services/sandrocoin-core.protocol
%attr(0644,root,root) %{_datadir}/pixmaps/*.ico
%attr(0644,root,root) %{_datadir}/pixmaps/*.bmp
%attr(0644,root,root) %{_datadir}/pixmaps/*.svg
%attr(0644,root,root) %{_datadir}/pixmaps/*.png
%attr(0644,root,root) %{_datadir}/pixmaps/*.xpm
%attr(0644,root,root) %{_mandir}/man1/sandrocoin-qt.1*
%endif

%files libs
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/shared-libraries.md
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/developer-notes.md doc/shared-libraries.md
%attr(0644,root,root) %{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files server
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING sandrocoin.conf.example doc/README.md doc/REST-interface.md doc/bips.md doc/dnsseed-policy.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_sbindir}/sandrocoind
%attr(0644,root,root) %{_tmpfilesdir}/sandrocoin.conf
%attr(0644,root,root) %{_unitdir}/sandrocoin.service
%dir %attr(0750,sandrocoin,sandrocoin) %{_sysconfdir}/sandrocoin
%dir %attr(0750,sandrocoin,sandrocoin) %{_localstatedir}/lib/sandrocoin
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/sysconfig/sandrocoin
%attr(0644,root,root) %{_datadir}/selinux/*/*.pp
%attr(0644,root,root) %{_mandir}/man1/sandrocoind.1*

%files utils
%defattr(-,root,root,-)
%license COPYING
%doc COPYING sandrocoin.conf.example doc/README.md
%attr(0755,root,root) %{_bindir}/sandrocoin-cli
%attr(0755,root,root) %{_bindir}/sandrocoin-tx
%attr(0755,root,root) %{_bindir}/bench_sandrocoin
%attr(0644,root,root) %{_mandir}/man1/sandrocoin-cli.1*



%changelog
* Fri Feb 26 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-2
- Rename Qt package from sandrocoin to sandrocoin-core
- Make building of the Qt package optional
- When building the Qt package, default to Qt5 but allow building
-  against Qt4
- Only run SELinux stuff in post scripts if it is not set to disabled

* Wed Feb 24 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-1
- Initial spec file for 0.12.0 release

# This spec file is written from scratch but a lot of the packaging decisions are directly
# based upon the 0.11.2 package spec file from https://www.ringingliberty.com/sandrocoin/
