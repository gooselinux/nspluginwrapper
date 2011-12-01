# Compile as a debug package
%define make_debug_package 	0

# What gecko we use
%define gecko_flavour		"mozilla"

%define plugin_config_version 1.9
%define plugin_config_name plugin-config-%{plugin_config_version}
%define plugin_config_binary plugin-config

# Excluded plugins (separated by ':')
%define exclude_list 	"libtotem*:libjavaplugin*:gecko-mediaplayer*:mplayerplug-in*:librhythmbox*:packagekit*:libnsISpicec*"

# Target defines
%if "%{_target_cpu}" == "i386"
%define target_bits	32
%endif

%if "%{_target_cpu}" == "i586"
%define target_bits	32
%endif

%if "%{_target_cpu}" == "i686"
%define target_bits	32
%endif

%if "%{_target_cpu}" == "ppc"
%define target_bits	32
%endif

%if "%{_target_cpu}" == "x86_64"
%define target_bits	64
%endif

%if "%{_target_cpu}" == "ppc64"
%define target_bits	64
%endif

# Define libraries for 32/64 arches
%define lib32			lib
%define lib64			lib64
%define libdir32		/usr/lib
%define libdir64		/usr/lib64

# define nspluginswrapper libdir (invariant, including libdir)
%define pkgdir32		%{libdir32}/%{name}
%define pkgdir64		%{libdir64}/%{name}

# define mozilla plugin dir and back up dir for 32-bit browsers
%define pluginsourcedir32	%{libdir32}/mozilla/plugins
%define plugindir32 		%{libdir32}/mozilla/plugins-wrapped

# define mozilla plugin dir and back up dir for 64-bit browsers
%define pluginsourcedir64	%{libdir64}/mozilla/plugins
%define plugindir64 		%{libdir64}/mozilla/plugins-wrapped

%define build_dir 		objs-%{target_bits}

%if "%{target_bits}" == "32"
%define lib		%{lib32}
%define libdir  	%{libdir32}
%define pkgdir  	%{pkgdir32}
%define plugindir	%{plugindir32}
%define pluginsourcedir	%{pluginsourcedir32}
%else
%define lib	  	%{lib64}
%define libdir  	%{libdir64}
%define pkgdir  	%{pkgdir64}
%define plugindir	%{plugindir64}
%define pluginsourcedir	%{pluginsourcedir64}
%endif

Summary:	A compatibility layer for Netscape 4 plugins
Name:		nspluginwrapper
Version:	1.3.0
Release:	14%{?dist}
Source0:	http://gwenole.beauchesne.info/projects/nspluginwrapper/files/%{name}-%{version}%{?svndate:-%{svndate}}.tar.bz2
Source1:	%{plugin_config_name}.tar.gz
Source2:	plugin-config.sh.in
Source3:	%{name}.sh.in
Patch1:		nspluginwrapper-1.3.0-make.patch
Patch2:		nspluginwrapper-1.3.0-configure.patch
Patch3:		nspluginwrapper-1.3.0-directory.patch
Patch4:		nspluginwrapper-20090625-fix-npident-array-sending.patch
Patch5:		nspluginwrapper-1.3.0-inst.patch
Patch6:		nspluginwrapper-1.3.0-compiz.patch
Patch100:	plugin-config-setuid.patch
Patch101:	plugin-config-umask.patch
Patch102:	plugin-config-print.patch
Patch103:	plugin-config-native.patch
Patch104:	plugin-config-time-check.patch
License:	GPLv2+
Group:		Applications/Internet
Url:		http://gwenole.beauchesne.info/projects/nspluginwrapper/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Provides:	%{name} = %{version}-%{release}
Requires:	mozilla-filesystem
BuildRequires:	pkgconfig gtk2-devel glib2-devel nspr-devel
BuildRequires:	libX11-devel libXt-devel cairo-devel pango-devel libcurl-devel
BuildRequires:	gecko-devel
ExclusiveArch:	%{ix86} x86_64 ppc

%description
nspluginwrapper makes it possible to use Netscape 4 compatible plugins
compiled for %{_arch} into Mozilla for another architecture, e.g. x86_64.

This package consists in:
  * npviewer: the plugin viewer
  * npwrapper.so: the browser-side plugin
  * nspluginplayer: stand-alone NPAPI plugin player
  * mozilla-plugin-config: a tool to manage plugins installation and update

%prep
%setup  -q -a 1

# Installation & build patches
%patch1 -p1 -b .make
%patch2 -p1 -b .conf
%patch3 -p1 -b .dir
%patch4 -p0 -b .array
%patch5 -p1 -b .inst
%patch6 -p1 -b .compiz

# Plugin-config patches
pushd %plugin_config_name
%patch100 -p2
%patch101 -p2 -b .umask
%patch102 -p2 -b .print
%patch103 -p2 -b .native
%patch104 -p2 -b .time-check
popd

%build
# Build wrapper

# set the propper built options
%if %{make_debug_package}
    %if "%{target_bits}" == "64"
	export CFLAGS="-g -m64 -DDEBUG"
    %else
	export CFLAGS="-g -m32 -DDEBUG"
    %endif
%else
    export CFLAGS="$RPM_OPT_FLAGS"
%endif

# set the propper built options
%if "%{target_bits}" == "64"
    export LDFLAGS="-m64 -L%{libdir64}"
%else
    export LDFLAGS="-m32 -L%{libdir32}"
%endif

mkdir %{build_dir}
pushd %{build_dir}
../configure 					\
	    --prefix=%{_prefix} 		\
	    --target-cpu=%{_target_cpu}		\
	    --pkgdir=%{name}			\
	    --pkglibdir=%{pkgdir}	        \
	    --with-lib32=%{lib32}		\
	    --with-lib64=%{lib64}		\
	    --with-base-lib=%{lib}		\
	    --with-base-libdir=%{libdir}	\
	    --viewer-paths=%{pkgdir}		\
	    --with-x11-prefix=/usr		\
	    --with-gecko=%{gecko_flavour}	\
	    --enable-viewer			\
	    --viewer-paths="%{pkgdir32}:%{pkgdir64}"\
	    --disable-biarch
	
make
popd

#Build plugin configuration utility
pushd %{plugin_config_name}
./configure --prefix=%{_prefix} --libdir=%{_libdir} CFLAGS="$RPM_OPT_FLAGS"
make
popd

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{plugindir}
mkdir -p $RPM_BUILD_ROOT%{pluginsourcedir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig

make -C %{build_dir} install DESTDIR=$RPM_BUILD_ROOT

ln -s %{pkgdir}/npwrapper.so $RPM_BUILD_ROOT/%{plugindir}/npwrapper.so

# Install plugin-config utility
pushd %{plugin_config_name}
DESTDIR=$RPM_BUILD_ROOT make install
popd

cd $RPM_BUILD_ROOT/usr/bin
mv %{plugin_config_binary} $RPM_BUILD_ROOT/%{pkgdir}
cd -

rm -rf $RPM_BUILD_ROOT/usr/doc/plugin-config

cat %{SOURCE2} > $RPM_BUILD_ROOT%{_bindir}/mozilla-plugin-config
chmod 755 $RPM_BUILD_ROOT%{_bindir}/mozilla-plugin-config

cat %{SOURCE3} | %{__sed} -e "s|EXCLUDE_LIST|%{exclude_list}|g" \
    > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
chmod 644 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

# set up nsplugin player starting script
%{__cat} > $RPM_BUILD_ROOT%{pkgdir}/nspluginplayer << EOF
export MOZ_PLUGIN_PATH=%{pluginsourcedir}
%{pkgdir}/npplayer "$@"
EOF
chmod 755 $RPM_BUILD_ROOT%{pkgdir}/nspluginplayer

# Remove conflicting files
rm -rf $RPM_BUILD_ROOT%{_bindir}/nspluginplayer
rm -rf $RPM_BUILD_ROOT%{_bindir}/nspluginwrapper

%clean
rm -rf $RPM_BUILD_ROOT

%post
/usr/bin/mozilla-plugin-config -i -f > /dev/null 2>&1 || :

%preun
if [ "$1" == "0" ]; then
    /usr/bin/mozilla-plugin-config -r > /dev/null 2>&1 || :
fi;

%files
%defattr(-,root,root)
%doc README COPYING NEWS
%dir %{pkgdir}
%dir %{plugindir}

%{pkgdir}/%{plugin_config_binary}
%{pkgdir}/npconfig
%{pkgdir}/npwrapper.so
%{pkgdir}/npviewer.bin
%{pkgdir}/npviewer.sh
%{pkgdir}/npviewer
%{pkgdir}/npplayer
%{pkgdir}/libxpcom.so
%{pkgdir}/libnoxshm.so
%{pkgdir}/nspluginplayer
%{plugindir}/npwrapper.so
%{_bindir}/mozilla-plugin-config
%config %{_sysconfdir}/sysconfig/%{name}


%changelog
* Wed Jun 30 2010 Martin Stransky <stransky@redhat.com> 1.3.0-14
- Fixed patch for rhbz#603564

* Tue Jun 29 2010 Martin Stransky <stransky@redhat.com> 1.3.0-13
- Fixed rhbz#603564  - wrapped plugins not getting updated

* Mon Mar 15 2010 Martin Stransky <stransky@redhat.com> 1.3.0-12
- Removed spice-xpi from wrapped plugins

* Wed Jan 6 2010 Martin Stransky <stransky@redhat.com> 1.3.0-11
- Fixed rpmlint complains

* Fri Dec 4 2009 Martin Stransky <stransky@redhat.com> 1.3.0-10
- added Compiz workaround (#542424)

* Tue Nov 10 2009 Martin Stransky <stransky@redhat.com> 1.3.0-9
- added NULL check (#531669)

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 15 2009 Martin Stransky <stransky@redhat.com> 1.3.0-7
- NPIdentifiers fix by Tristan Schmelcher (Google)

* Wed Jul 15 2009 Martin Stransky <stransky@redhat.com> 1.3.0-6
- Package kit plugin is ignored now (#511385)

* Tue Mar 03 2009 Warren Togami <wtogami@redhat.com> - 1.3.0-5
- Really Fix x86 32bit build (#488308)

* Sun Mar 01 2009 Warren Togami <wtogami@redhat.com> - 1.3.0-4
- Fix x86 32bit build

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 9 2009 Martin Stransky <stransky@redhat.com> 1.3.0-2
- Fixed multilib conflicts

* Thu Jan 8 2009 Martin Stransky <stransky@redhat.com> 1.3.0-1
- Updated to 1.3.0 and removed some fedora build patches

* Tue Dec 02 2008 Warren Togami <wtogami@redhat.com> 1.1.8-2
- fix-invalid-RPC-after-NPP_Destroy fixes a crasher

* Mon Dec 1 2008 Martin Stransky <stransky@redhat.com> 1.1.8-1
- Updated to 1.1.8
- Removed already upstreamed patches

* Wed Nov 12 2008 Martin Stransky <stransky@redhat.com> 1.1.4-1
- Updated to 1.1.4
- Consolidated build patches

* Wed Oct 22 2008 Martin Stransky <stransky@redhat.com> 1.1.2-4
- Fixed #449338 - mozilla-plugin-config segfaults with -v argument

* Tue Oct 21 2008 Martin Stransky <stransky@redhat.com> 1.1.2-3
- Removed event patch, it blocks X events and breaks Adobe pdf plugin
- Removed event limit in xt_event_polling_timer_callback 

* Fri Oct 17 2008 Martin Stransky <stransky@redhat.com> 1.1.2-2
- added umask to plugin config (#463736)

* Thu Oct 16 2008 Martin Stransky <stransky@redhat.com> 1.1.2-1
- updated to 1.1.12
- added librhythmbox* to ignored plugins (#467187)
- removed debug prints (#467090)

* Mon Oct 06 2008 Warren Togami <wtogami@redhat.com> 1.1.0-11
- Unrevert patch from -7 because Warren was wrong
- Concurrent rpc_method_invoke() patch

* Fri Oct 03 2008 Warren Togami <wtogami@redhat.com> 1.1.0-10
- Revert libcurl requires because it was done in an incorrect way
- Revert patch from -7 because it made things worse

* Tue Sep 30 2008 Martin Stransky <stransky@redhat.com> 1.1.0-7
- Updated fix for #456432 -(Windowless Crash) Flash 10 w/ Firefox 3

* Wed Sep 17 2008 Martin Stransky <stransky@redhat.com> 1.1.0-6
- Added libcurl to requires (#460988)

* Mon Aug 04 2008 Martin Stransky <stransky@redhat.com> 1.1.0-5
- Added fix for #456432 -(Windowless Crash) Flash 10 w/ Firefox 3

* Mon Jul 21 2008 Martin Stransky <stransky@redhat.com> 1.1.0-4
- Removed gecko-libs from requieres (it's not needed now)

* Tue Jul 18 2008 Martin Stransky <stransky@redhat.com> 1.1.0-3
- Enabled experimental stand-alone plugin player

* Tue Jul 15 2008 Martin Stransky <stransky@redhat.com> 1.1.0-2
- Fixed build warnings in our patches

* Tue Jul 8 2008 Martin Stransky <stransky@redhat.com> 1.1.0-1
- update to latest upstream version (1.1.0)

* Mon May 5 2008 Martin Stransky <stransky@redhat.com> 0.9.91.5-28
- link pluginwrapper with stdc++ lib

* Wed Apr 30 2008 Christopher Aillon <caillon@redhat.com> 0.9.91.5-27
- mozilla-filesystem now owns the plugin source dir

* Tue Mar 11 2008 Martin Stransky <stransky@redhat.com> 0.9.91.5-26
- /etc/sysconfig/nspluginwrapper marked as config file
- exclude some player plugins

* Mon Mar 10 2008 Martin Stransky <stransky@redhat.com> 0.9.91.5-25
- updated the sleep patch

* Thu Mar 06 2008 Martin Stransky <stransky@redhat.com> 0.9.91.5-24
- added experimental patch for #426968 - nspluginwrapper wakes up too much

* Tue Feb 26 2008 Martin Stransky <stransky@redhat.com> 0.9.91.5-23
- merged exclude patch with main tarball
- fixed #431095 - Typo in mozilla-plugin-config verbose output

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.9.91.5-22
- Autorebuild for GCC 4.3

* Mon Jan 21 2008 Martin Stransky <stransky@redhat.com> 0.9.91.5-21
- fixed #426618 - gcjwebplugin error: Failed to run
  (added to ignored plugins)

* Mon Jan 14 2008 Martin Stransky <stransky@redhat.com> 0.9.91.5-20
- fixed #426176 - Orphaned npviewer.bin processes

* Thu Jan 10 2008 Martin Stransky <stransky@redhat.com> 0.9.91.5-19
- xulrunner rebuild
- fixed build script, added gthread-2.0

* Mon Dec 24 2007 Warren Togami <wtogami@redhat.com> 0.9.91.5-18
- Make nsviewer.bin initialized for multithreading, fixes #360891

* Tue Dec 20 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-17
- disabled xpcom support - it causes more troubles than advantages

* Tue Dec 13 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-16
- spec fixes
- fixed xulrunner support

* Mon Dec 10 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-15
- updated configure script - gecko selection

* Thu Dec 06 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-14
- enabled xpcom support
- added fix for #393541 - scripts will never fail

* Fri Nov 23 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-13
- rebuilt against xulrunner

* Tue Nov 6 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-12
- more fixes from review by security standards team

* Wed Oct 31 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-11
- added fixes from review by security standards team

* Fri Oct 26 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-10
- mozilla-plugin-config can be run by normal user now

* Wed Oct 24 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-9
- Updated config utility - removes dangling symlinks and
  wrapped plugins
  
* Tue Oct 23 2007 Jeremy Katz <katzj@redhat.com> 0.9.91.5-8
- Rebuild against new firefox

* Mon Oct 15 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-7
- added a fix for #281061 - gnash fails when wrapped, works when native

* Wed Oct 10 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-6
- removed possibble deadlock during plugin restart

* Tue Oct 9 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-5
- fixed browser crashes (#290901)

* Mon Oct 1 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-4
- quit the plugin when browser crashes (#290901)

* Fri Sep 21 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-3
- added original plugin dir to the package

* Mon Sep 10 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-2
- added upstream patches - RPC error handling and plugin restart

* Mon Aug 27 2007 Martin Stransky <stransky@redhat.com> 0.9.91.5-1
- update to the latest upstream

* Mon Aug 27 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-19
- converted rpc error handling code to a thread-safe variant
- added a time limit to plugin restart

* Tue Aug 14 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-18
- implemented plugin restart (#251530)

* Tue Aug 14 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-17
- fixed an installation script (#251698)

* Mon Aug 13 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-16
- fixed plugins check
- minor spec fixes

* Fri Aug 10 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-15
- removed mozembeded dependency
- excluded totem plugins from wrapping
- xpcom support is optional now

* Thu Aug 9 2007 Christopher Aillon <caillon@redhat.com> 0.9.91.4-14
- Rebuild against newer gecko

* Wed Aug 8 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-13
- removed unsafe plugins probe
- added agruments to mozilla-plugin-config

* Tue Aug 7 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-12
- removed fake libxpcom

* Mon Aug 6 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-11
- added gecko dependency
- added plugin configuration utility

* Fri Aug 3 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-10
- fixed totem-complex plugin wrapping

* Mon Jul 30 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-9
- added plugin dirs

* Fri Jul 27 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-8
- added switch for creating debug packages

* Thu Jul 19 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-7
- integrated with firefox / seamonkey

* Tue Jul 11 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-6
- added new options to the configuration utility
- modified along new plug-ins concept

* Thu Jun 19 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-5
- updated nspluginsetup script
- added support for x86_64 plug-ins

* Thu Jun 14 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-4
- added ppc arch
- silenced installation scripts
- moved configuration to /etc/sysconfig

* Thu Jun 12 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-3
- updated nspluginsetup script and package install/uninstall scripts
- added cross-compilation support
- removed binaries stripping

* Fri Jun 8 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-2
- added BuildRequires - pkgconfig, gtk2-devel, glib, libXt-devel

* Fri Jun 8 2007 Martin Stransky <stransky@redhat.com> 0.9.91.4-1
- initial build
