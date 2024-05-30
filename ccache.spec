Summary:	Compiler Cache
Name:		ccache
Version:	4.10
Release:	1
Group:		Development/Other
License:	GPLv3+
Url:		https://ccache.samba.org/
Source0:	https://github.com/ccache/ccache/releases/download/v%{version}/%{name}-%{version}.tar.xz

BuildRequires: asciidoc
BuildRequires: a2x
BuildRequires: cmake
BuildRequires: ninja
BuildRequires: pkgconfig(hiredis)
BuildRequires: pkgconfig(libzstd)
BuildRequires: %{_lib}zstd-static-devel

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
%cmake \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DENABLE_TESTING=$TEST \
        -DZSTD_LIBRARY=/usr/%{_lib}/libzstd.a
%ninja_build

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
%ninja_install -C build

%files
%{_bindir}/ccache

