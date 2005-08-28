#
Summary:	the Fluendo Streaming Server
Name:		flumotion
Version:	0.1.9
Release:	0.1
License:	GPL
Group:		Daemons
Source0:	http://www.flumotion.net/src/flumotion/%{name}-%{version}.tar.bz2
# Source0-md5:	7f2b4abbabd7756d1d689b38fd477d3e
URL:		http://www.flumotion.net/
BuildRequires:	automake
BuildRequires:	gstreamer-devel >= 0.8
BuildRequires:	python-pygtk-devel >= 2.4.0
BuildRequires:	python-gstreamer >= 0.8.2-1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Flumotion is a streaming media server created with the backing of
Fluendo. It features intuitive graphical administration tools, making
the task of setting up and manipulating audio and video streams easy
for even novice system administrators.

%prep
%setup -q

%build
install /usr/share/automake/config.* .
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv -f $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}/ffserver
install doc/*.conf $RPM_BUILD_ROOT%{_sysconfdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
