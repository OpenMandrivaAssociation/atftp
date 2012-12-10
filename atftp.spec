Summary:	Advanced Trivial File Transfer Protocol (TFTP) client
Name:		atftp
Version:	0.7
Release:	%mkrel 9
License:	GPL
Group:		System/Servers
URL:		http://ftp.de.debian.org/debian/pool/main/a/atftp/
Source0:	%{name}-%{version}.tar.gz
Source1:	atftpd.init.d
Source2:	atftpd.sysconfig
Source3:	atftpd.logrotate
Patch1:		atftp-0.7-inlines.patch
Patch2:		atftp-0.7.diff
Patch3:		atftp-CLK_TCK.diff
Patch4:		atftp-0.7_compiler_warnings.patch
Patch5:		atftp-0.7_thread_crash.patch
Patch6:		atftp-0.7_sol_ip.patch
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	libreadline-devel
BuildRequires:	termcap-devel
BuildRequires:	tcp_wrappers-devel
Requires(pre):	rpm-helper
Provides:	tftp

%description
atftp is an advanced client implementation of the TFTP protocol that implements
RFCs 1350, 2090, 2347, 2348, and 2349. The server is multi-threaded and the
client presents a friendly interface using libreadline. The current server
implementation lacks IPv6 support.

%package	server
Summary:	Advanced Trivial File Transfer Protocol (TFTP) server
Group:		System/Servers
Requires:	binutils
Requires:	gawk
Requires:	tcp_wrappers
Requires:	logrotate
Requires(pre): rpm-helper
Conflicts:	tftp-server

%description	server
atftpd is an advanced server implementation of the TFTP
protocol that implements RFCs 1350, 2090, 2347, 2348, and 2349.
The server is multi-threaded and the client presents a friendly
interface using libreadline. The current server implementation
lacks IPv6 support.

%prep

%setup -q
%patch1 -p1
%patch2
%patch3
%patch4
%patch5
%patch6

### FIXME: Change location of pcre.h to pcre/pcre.h (Please fix upstream)
if [ -r %{_includedir}/pcre/pcre.h ]; then
    %{__perl} -pi.orig -e 's|\bpcre.h\b|pcre/pcre.h|' configure tftpd_pcre.h
fi

%{__cat} <<EOF >tftp.xinetd
# default: off
# description: The tftp server serves files using the trivial file transfer protocol. The tftp protocol is often used to boot diskless workstations, download configuration files to network-aware printers, and to start the installation process for some operating systems.
service tftp
{
	disable	= yes
	socket_type		= dgram
	protocol		= udp
	wait			= yes
	user			= root
	server			= %{_sbindir}/in.tftpd
# multicast config
#	server_args		= --tftpd-timeout 300 --retry-timeout 5 --mcast-port 1758 --mcast-addr 239.239.239.0-255 --maxthread 1000 --verbose=5 %{_localstatedir}/lib/tftpboot
	server_args		= %{_localstatedir}/lib/tftpboot
	per_source		= 11
	cps			= 100 2
	flags			= IPv4
}
EOF

%build
autoreconf -fi

%configure \
    --disable-dependency-tracking \
    --enable-libreadline \
    --enable-libwrap \
    --enable-libpcre \
    --enable-mtftp
%serverbuild

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_logdir}/atftpd
install -d %{buildroot}%{_var}/run/atftpd

%makeinstall

%{__install} -Dp -m 0755 %{SOURCE1} %{buildroot}/%{_initrddir}/atftpd
%{__install} -Dp -m 0644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/atftpd
%{__install} -Dp -m 0644 %{SOURCE3} %{buildroot}/%{_sysconfdir}/logrotate.d/atftpd

%{__install} -d %{buildroot}/%{_localstatedir}/lib/tftpboot/
%{__install} -Dp -m0644 tftp.xinetd %{buildroot}%{_sysconfdir}/xinetd.d/tftp
touch %{buildroot}%{_logdir}/atftpd/atftpd.log

%post -n atftp-server
%_post_service atftpd

%preun -n atftp-server
%_preun_service atftpd

%files
%defattr(-, root, root, 0755)
%doc BUGS Changelog FAQ INSTALL LICENSE README* TODO
%doc %{_mandir}/man1/atftp.*
%{_bindir}/atftp

%files server
%defattr(-, root, root, 0755)
%doc docs/*
%attr(0755,root,root) %{_initrddir}/atftpd
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/xinetd.d/tftp
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/atftpd
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/atftpd
%dir %{_localstatedir}/lib/tftpboot
%dir %attr(0755,nobody,nogroup) %{_var}/run/atftpd
%dir %attr(0755,nobody,nogroup) %{_logdir}/atftpd
%{_sbindir}/atftpd
%{_sbindir}/in.tftpd
%attr(0644,nobody,nogroup) %{_logdir}/atftpd/atftpd.log
%{_mandir}/man8/atftpd.*
%{_mandir}/man8/in.tftpd.*
