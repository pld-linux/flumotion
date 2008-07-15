Summary:	The Fluendo Streaming Server
Summary(pl.UTF-8):	Serwer strumieni Fluendo
Name:		flumotion
Version:	0.5.1
Release:	0.4
License:	GPL
Group:		Daemons
Source0:	http://www.flumotion.net/src/flumotion/%{name}-%{version}.tar.bz2
# Source0-md5:	70256d8d80a0d5cda61e468116ff8be2
Source1:	%{name}.init
Patch0:		%{name}-pdksh.patch
URL:		http://www.flumotion.net/
BuildRequires:	automake
BuildRequires:	gstreamer-devel >= 0.10.10
BuildRequires:	python-pygtk-devel >= 2.8.0
BuildRequires:	python-gstreamer >= 0.10.4
BuildRequires:	python-TwistedCore >= 2.0.1
BuildRequires:	python-TwistedNames
BuildRequires:	python-TwistedWeb
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(post):	openssl-tools
Requires:	gstreamer-audio-effects-good
Requires:	gstreamer-libpng
Requires:	gstreamer-plugins-base >= 0.10.10
Requires:	python-PIL
Requires:	python-TwistedCore-ssl
Provides:	user(flumotion)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Flumotion is a GPL streaming media server written in Python. It is
distributed and component-based: every step in the streaming process
(production, conversion, consumption) can be run inside a separate
process on separate machines.

Flumotion uses a central manager process to control the complete
network; one or more worker processes distributed over machines to run
actual streaming components; and one or more admin clients connecting
to the manager to control it.

%description -l pl.UTF-8
Flumotion to serwer strumieni multimedialnych napisany w Pythonie i
udostępniany na licencji GPL. Jest to system rozproszony i modularny:
każdy etap przetwarzania strumienia (produkcja, konwersja, konsumpcja)
może być przeprowadzany w osobnym procesie i na osobnej maszynie.

Flumotion używa centralnego procesu zarządcy, który kontroluje cały
system; jednego lub więcej procesu robotnika czuwającego nad
komponentami; jednego lub więcej klienta administracji, pozwalającego
na sprawowanie kontroli przez użytkownika.

%prep
%setup -q
%patch0 -p1

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/flumotion

# install service files
install -d $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}

# create log and run and cache directory
install -d $RPM_BUILD_ROOT%{_localstatedir}/log/flumotion
install -d $RPM_BUILD_ROOT%{_localstatedir}/run/flumotion
install -d $RPM_BUILD_ROOT%{_localstatedir}/cache/flumotion

# Install the logrotate entry
install -m 0644 -D doc/redhat/flumotion.logrotate \
	$RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/flumotion

%find_lang flumotion

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 229 flumotion
%useradd -u 229 -d %{_localstatedir}/cache/flumotion -s /bin/false -g flumotion -c "Flumotion server" flumotion

%post
/sbin/chkconfig --add flumotion
# generate a default .pem certificate ?
PEM_FILE="%{_sysconfdir}/flumotion/default.pem"
if ! test -e ${PEM_FILE}
then
	sh %{_datadir}/flumotion/make-dummy-cert ${PEM_FILE}
	chown :flumotion ${PEM_FILE}
	chmod 640 ${PEM_FILE}
fi

# create a default planet config if no manager configs present
# the default login will be user/test
if ! test -e %{_sysconfdir}/flumotion/managers
then
	mkdir -p %{_sysconfdir}/flumotion/managers/default/flows
	cat > %{_sysconfdir}/flumotion/managers/default/planet.xml <<EOF
<planet>
 
	<manager>
		<!-- <debug>3</debug> -->
		<host>localhost</host>
<!--
		<port>7531</port>
		<transport>ssl</transport>
-->
		<!-- certificate path can be relative to $sysconfdir/flumotion,
				 or absolute -->
<!--
		<certificate>default.pem</certificate>
-->
		<component name="manager-bouncer" type="htpasswdcrypt-bouncer">
			<property name="data"><![CDATA[
user:PSfNpHTkpTx1M
]]></property>
		</component>
	</manager>
 
</planet>
EOF
fi

# create a default worker config if no worker configs present
# the default login will be user/test
if ! test -e %{_sysconfdir}/flumotion/workers
then
	mkdir -p %{_sysconfdir}/flumotion/workers
	cat > %{_sysconfdir}/flumotion/workers/default.xml <<EOF
<worker>
 
	<!-- <debug>3</debug> -->

	<manager>
<!--
		<host>localhost</host>
		<port>7531</port>
-->
	</manager>

	<authentication type="plaintext">
		<username>user</username>
		<password>test</password>
	</authentication>
 
	<!-- <feederports>8600-8639</feederports> -->

</worker>
EOF

fi

%preun
# if removal and not upgrade, stop the processes, clean up locks
if [ $1 -eq 0 ]
then
	/sbin/service flumotion stop > /dev/null

	rm -rf %{_localstatedir}/lock/flumotion*
	rm -rf %{_localstatedir}/run/flumotion*

	# clean out the cache/home dir too, without deleting it or the user
	rm -rf %{_localstatedir}/cache/flumotion/*
	rm -rf %{_localstatedir}/cache/flumotion/.[^.]*

	/sbin/chkconfig --del flumotion
fi


%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/%{name}
%attr(755,root,root) %{_bindir}/*
%attr(750,root,flumotion) %{_sysconfdir}/flumotion
%attr(540,root,flumotion) %{_sysconfdir}/logrotate.d/flumotion
%attr(770,root,flumotion) %{_localstatedir}/run/flumotion
%attr(770,root,flumotion) %{_localstatedir}/log/flumotion
%attr(770,flumotion,flumotion) %{_localstatedir}/cache/%{name}
%attr(754,root,flumotion) %{_sysconfdir}/rc.d/init.d/%{name}
%{_libdir}/%{name}
%{_datadir}/%{name}
%{_desktopdir}/%{name}-admin.desktop
%{_pkgconfigdir}/%{name}.pc
%{_pixmapsdir}/*
%{_mandir}/man1/*
%doc ChangeLog COPYING README AUTHORS %{name}.doap
%doc conf
