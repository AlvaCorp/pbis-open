# ex: set softtabstop=4 tabstop=8 expandtab shiftwidth=4:

%define _sysconfdir	/etc

%{!?Compat32: %define Compat32 0}

Summary:	Likewise IO Services
Version: 	%{RpmVersion}
Release: 	%{RpmRelease}
License: 	Likewise Proprietary
Group: 		Development/Libraries
URL: 		http://www.likewise.com/
BuildRoot: 	%{buildRootDir}/%{name}-%{version}

Requires: likewise-base likewise-krb5 likewise-netlogon likewise-sqlite

Name: 		%{RpmName}

AutoReq: no

%define INIT_DIR /etc/init.d

%if %{Compat32}
%define _lib lib
%endif

%description
Likewise IO Services

%package devel
Summary: Likewise IO Services Software Development Kit
Group: Development/Libraries
Requires: likewise-lwio

%description devel
The likewise-lwio-devel package includes the development libraries and header files that supply the application programming interface for the Likewise IO Services.

%prep

%build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
rsync -a %{PopulateRoot}/ ${RPM_BUILD_ROOT}/


%clean 
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{INIT_DIR}/*
%config(noreplace) /etc/likewise/lwiod.reg
%{PrefixDir}/sbin/*
%{PrefixDir}/bin/*

%{PrefixDir}/%{_lib}/*

%files devel
%defattr(0644,root,root,0755)

%attr(0644,root,root) %{PrefixDir}/%{_lib}/*.a
%attr(0644,root,root) %{PrefixDir}/%{_lib}/*.la
%if ! %{Compat32}
%attr(0644,root,root) %{PrefixDir}/include/*
#%attr(0644,root,root) %{PrefixDir}/share/man/*
#%attr(0644,root,root) %{PrefixDir}/share/doc/*
%endif


%define initScriptPathList %{INIT_DIR}/lwiod
%post
## chkconfig behaves differently on various updates of RHEL and SUSE
## So, we massage the init script according to the release, for now.
for daemon in %{initScriptPathList}; do
    if [ -x $daemon ]; then
        if grep "LWI_STARTUP_TYPE_" $daemon >/dev/null 2>&1; then
            daemon_new=${daemon}.new

            if [ -f /etc/redhat-release ]; then
                base_pri=19
                if [ -f /etc/rc2.d/S*NetworkManager ]; then
                    base_pri=$(( `basename /etc/rc2.d/S*NetworkManager | sed 's/S\([0-9]\+\).*/\1/' ` + 1 ))
                fi
                start_pri=`/bin/sed -n -e 's/.* chkconfig: [^ ]\+ \([0-9]\+\) [0-9]\+.*$/\1/p' $daemon`
                /bin/sed \
                    -e 's/^#LWI_STARTUP_TYPE_REDHAT\(.*\)$/\1/' \
                    -e '/^#LWI_STARTUP_TYPE_SUSE.*$/ d' \
                    -e 's/\(.* chkconfig: [^ ]\+ \)\([0-9]\+\)\( [0-9]\+.*\)$/\1'$(( $start_pri - 19 + $base_pri ))'\3/' \
                    $daemon > $daemon_new
            else
                /bin/sed \
                    -e 's/^#LWI_STARTUP_TYPE_SUSE\(.*\)$/\1/' \
                    -e '/^#LWI_STARTUP_TYPE_REDHAT.*$/ d' \
                    $daemon > $daemon_new
            fi
            mv $daemon_new $daemon
            chmod 0755 $daemon
        fi
    fi
done


%changelog
