Name:		ccache
Version:	2.4
Release:	%mkrel 15
Group:		Development/Other
Summary:	Compiler Cache
License:	GPL
URL:		http://ccache.samba.org/
Source0:	%{name}-%{version}.tar.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
ccache is a compiler cache. It acts as a caching pre-processor to 
C/C++ compilers, using the -E compiler switch and a hash to detect 
when a compilation can be satisfied from cache. This often results 
in a 5 to 10 times speedup in common compilations.

To enable ccache's default use, the system admin should modify 
%{_sysconfdir}/sysconfig/ccache to "yes". If its default use is not 
enabled and you wish to use it, simply add %{_prefix}/%{_lib}/ccache/bin/ to 
the start of your \$PATH

%prep
%setup -q

%build
%configure2_5x
%make

%__cat <<EOF > %{name}.sh
#!/bin/sh

if [ -f /etc/sysconfig/ccache ]; then
    . /etc/sysconfig/ccache
fi
if [ "\$USE_CCACHE_DEFAULT" = "yes" ]; then
    if [ -z \`echo "\$PATH" | grep "%_libdir/ccache/bin"\` ]; then
        export PATH="%_libdir/ccache/bin:\$PATH"
    fi
fi
EOF

%__cat << EOF > %{name}.csh
#!/bin/csh

if ( -f /etc/sysconfig/ccache ) then
    eval \`sed -n 's/^\([^#]*\)=\([^#]*\)/set \1=\2;/p' < /etc/sysconfig/ccache\`
endif
if ( "\$USE_CCACHE_DEFAULT" == "yes" ) then
    if ( "\$path" !~ *%_libdir/ccache/bin* ) then
        setenv path = ( %_libdir/ccache/bin \$path )
    endif
endif
EOF

%install
%__rm -rf %{buildroot}
%__install -dm 755 %{buildroot}{%{_bindir},%{_libdir}/ccache/bin,%{_mandir}/man1}
%__install -pm 755 ccache %{buildroot}%{_libdir}/ccache/bin
%__install -pm 644 ccache.1 %{buildroot}%{_mandir}/man1
%__install -dm 755 %{buildroot}%{_sysconfdir}/profile.d
%__install -pm 755 %{name}.sh %{name}.csh %{buildroot}%{_sysconfdir}/profile.d
rm -f %{name}-%{version}.compilers
pref=`gcc -dumpmachine`
for name in cc gcc g++ c++; do
for comp in $name $pref-$name; do
%__cat <<EOF > %{buildroot}%{_prefix}/%{_lib}/ccache/bin/$comp
#!/bin/sh
PATH=%_bindir:\$PATH
if [ -f /etc/sysconfig/ccache ]; then
	. /etc/sysconfig/ccache
	if [ "\$USE_CCACHE_WITH_ICECREAM" = "yes" ]; then
	PATH=%{_libdir}/icecc/bin:\$PATH
	fi
fi

ccache ${comp} "\$@"
EOF
echo "%attr(0755,root,root) %{_libdir}/ccache/bin/$comp" >> %{name}-%{version}.compilers
done
done

%__mkdir_p %{buildroot}%{_sysconfdir}/sysconfig/
%__cat <<EOF > %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
# Should we add the ccache compiler symlinks to PATH
# yes|no
# Please note that if added to \$PATH the user can still disable 
# it with CCACHE_DISABLE
# If not enabled by default, the user can add %{_libdir}/ccache/bin/
# to their \$PATH
USE_CCACHE_DEFAULT="no"

# Enable icecream integration
USE_CCACHE_WITH_ICECREAM="no"

EOF

%clean
rm -rf %{buildroot}

%files -f %{name}-%{version}.compilers
%defattr(-,root,root)
%doc README
%dir %{_libdir}/ccache
%dir %{_libdir}/ccache/bin
%{_libdir}/ccache/bin/ccache
%{_mandir}/man1/ccache.1*
%{_sysconfdir}/profile.d/*
%config(noreplace) %{_sysconfdir}/sysconfig/*



