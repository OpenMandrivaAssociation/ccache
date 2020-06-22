Summary:	Compiler Cache
Name:		ccache
Version:	3.7.10
Release:	1
Group:		Development/Other
License:	GPLv3+
Url:		http://ccache.samba.org/
Source0:	https://github.com/ccache/ccache/releases/download/v%{version}/%{name}-%{version}.tar.xz

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
%autosetup -p1

%build
%configure
%make_build

cat <<EOF > %{name}.sh

if [ -f /etc/sysconfig/ccache ]; then
    . /etc/sysconfig/ccache
fi
if [ "\$USE_CCACHE_DEFAULT" = "yes" ]; then
    if [ -z \`echo "\$PATH" | grep "%_libdir/ccache/bin"\` ]; then
        export PATH="%_libdir/ccache/bin:\$PATH"
    fi
fi
EOF

cat << EOF > %{name}.csh

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
install -dm 755 %{buildroot}{%{_bindir},%{_libdir}/ccache/bin,%{_mandir}/man1}
install -pm 755 ccache %{buildroot}%{_bindir}
install -pm 644 doc/ccache.1 %{buildroot}%{_mandir}/man1
install -pm 755 %{name}.sh -D %{buildroot}%{_sysconfdir}/profile.d/30ccache.sh
install -pm 755 %{name}.csh -D %{buildroot}%{_sysconfdir}/profile.d/30ccache.csh

rm -f %{name}-%{version}.compilers
pref=`gcc -dumpmachine`

create_compiler() {
cat <<EOF > %{buildroot}%{_prefix}/%{_lib}/ccache/bin/$1
#!/bin/sh
if [ ! -x %_bindir/$1 ]; then
	echo Error: compiler $1 does not exist. >&2
	exit 127
fi
PATH=%_bindir:\$PATH
if [ -f /etc/sysconfig/ccache ]; then
	. /etc/sysconfig/ccache
	if [ "\$USE_CCACHE_WITH_ICECREAM" = "yes" ]; then
	PATH=%{_libdir}/icecc/bin:\$PATH
	fi
fi

ccache ${1} "\$@"
EOF
echo "%attr(0755,root,root) %{_libdir}/ccache/bin/$1" >> %{name}-%{version}.compilers
}

for name in gcc g++ c++; do
 for comp in $name $pref-$name ${pref/manbo/mandriva}-$name; do
  # check for backports that have no manbo:
  [ -e "%{buildroot}%{_libdir}/ccache/bin/$comp" ] || create_compiler $comp
 done
done
create_compiler cc

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig/
cat <<EOF > %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
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

%check
%make_build check

%files -f %{name}-%{version}.compilers
%dir %{_libdir}/ccache
%dir %{_libdir}/ccache/bin
%{_bindir}/ccache
%{_mandir}/man1/ccache.1*
%{_sysconfdir}/profile.d/*
%config(noreplace) %{_sysconfdir}/sysconfig/*

