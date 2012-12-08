Name:		ccache
Version:	3.1.7
Release:	1
Group:		Development/Other
Summary:	Compiler Cache
License:	GPLv3+
URL:		http://ccache.samba.org/
Source0:	http://samba.org/ftp/ccache/%{name}-%{version}.tar.xz

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
%__install -pm 755 ccache %{buildroot}%{_bindir}
%__install -pm 644 ccache.1 %{buildroot}%{_mandir}/man1
%__install -pm 755 %{name}.sh -D %{buildroot}%{_sysconfdir}/profile.d/30ccache.sh
%__install -pm 755 %{name}.csh -D %{buildroot}%{_sysconfdir}/profile.d/30ccache.csh

rm -f %{name}-%{version}.compilers
pref=`gcc -dumpmachine`

create_compiler() {
%__cat <<EOF > %{buildroot}%{_prefix}/%{_lib}/ccache/bin/$1
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

%files -f %{name}-%{version}.compilers
%dir %{_libdir}/ccache
%dir %{_libdir}/ccache/bin
%{_bindir}/ccache
%{_mandir}/man1/ccache.1*
%{_sysconfdir}/profile.d/*
%config(noreplace) %{_sysconfdir}/sysconfig/*





%changelog
* Mon Jan 09 2012 Alexander Khrukin <akhrukin@mandriva.org> 3.1.7-1
+ Revision: 759181
- version update 3.1.7

* Sat Dec 03 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.1.5-2
+ Revision: 737400
- fix so that ccache gets added to $PATH earlier, so that other wrappers can be
  added with higher priority to $PATH later (ie. work with colorgcc)

* Sun May 29 2011 Funda Wang <fwang@mandriva.org> 3.1.5-1
+ Revision: 681745
- update to new version 3.1.5

* Wed Sep 22 2010 Funda Wang <fwang@mandriva.org> 3.1-1mdv2011.0
+ Revision: 580563
- new version 3.1

* Mon Aug 23 2010 Funda Wang <fwang@mandriva.org> 3.0.1-1mdv2011.0
+ Revision: 572118
- new version 3.0.1

* Mon Jun 22 2009 Wanderlei Cavassin <cavassin@mandriva.com.br> 2.4-20mdv2011.0
+ Revision: 388082
+ rebuild (emptylog)

* Mon Jun 22 2009 Wanderlei Cavassin <cavassin@mandriva.com.br> 2.4-19mdv2010.0
+ Revision: 388073
- remove shell bang to avoid uneeded dependencies (fixes mdv #51777)

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 2.4-19mdv2009.0
+ Revision: 266473
- rebuild early 2009.0 package (before pixel changes)

* Wed Apr 23 2008 Helio Chissini de Castro <helio@mandriva.com> 2.4-18mdv2009.0
+ Revision: 196994
- Moving ccache binary to bin to allow make install as root works

* Sat Mar 15 2008 Anssi Hannula <anssi@mandriva.org> 2.4-17mdv2008.1
+ Revision: 188046
- add mandriva variants of manbo g++ and c++

* Sat Mar 15 2008 Anssi Hannula <anssi@mandriva.org> 2.4-16mdv2008.1
+ Revision: 188036
- update compiler scripts to match current manbo-adapted compilers
- check the compiler existence before continuing to avoid fork bombs

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Oct 22 2007 Marcelo Ricardo Leitner <mrl@mandriva.com> 2.4-15mdv2008.1
+ Revision: 101148
- Rebuild

