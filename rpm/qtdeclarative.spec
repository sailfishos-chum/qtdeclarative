%define keepstatic 1

# Bug: https://bugzilla.redhat.com/show_bug.cgi?id=2061194
%define _lto_cflags %{nil}

%global qt_module qtdeclarative

# definition borrowed from qtbase
%global multilib_archs x86_64 %{ix86} %{?mips} ppc64 ppc s390x s390 sparc64 sparcv9

#global bootstrap 1

Summary: Qt5 - QtDeclarative component
Name: opt-qt5-%{qt_module}
Version: 5.15.8
Release: 1%{?dist}

# See LICENSE.GPL LICENSE.LGPL LGPL_EXCEPTION.txt, for details
License: LGPLv2 with exceptions or GPLv3 with exceptions
Url:     http://www.qt.io
Source0: %{name}-%{version}.tar.bz2

# header file to workaround multilib issue
# https://bugzilla.redhat.com/show_bug.cgi?id=1441343
Source5: qv4global_p-multilib.h

## upstream patches
## repo: https://invent.kde.org/qt/qt/qtdeclarative
## branch: kde/5.15
## git format-patch v5.15.8-lts-lgpl
Patch1:  0001-Document-that-StyledText-also-supports-nbsp-and-quot.patch
Patch2:  0002-Support-apos-in-styled-text.patch
Patch3:  0003-Remove-unused-QPointer-QQuickPointerMask.patch
Patch4:  0004-QQmlDelegateModel-Refresh-the-view-when-a-column-is-.patch
Patch5:  0005-Fix-sweep-step-for-tainted-QObject-JavaScript-wrappe.patch
Patch6:  0006-Fix-TapHandler-so-that-it-actually-registers-a-tap.patch
Patch7:  0007-Revert-Fix-TapHandler-so-that-it-actually-registers-.patch
Patch8:  0008-QQmlJs-FixedPoolArray-fix-UB-precondition-violation-.patch
Patch9:  0009-V4-Do-not-call-dtor-of-an-object-we-continue-to-use.patch
Patch10: 0010-Make-sure-QQuickWidget-and-its-offscreen-window-s-sc.patch
Patch11: 0011-QQuickItem-Guard-against-cycles-in-nextPrevItemInTab.patch
Patch12: 0012-QSGOpenGLDistanceFieldGlyphCache-fix-multiplication-.patch
Patch13: 0013-QSGOpenGLDistanceFieldGlyphCache-fix-UB-ordering-of-.patch
Patch14: 0014-Reset-currentChanges-if-currentChanges-is-active-whe.patch
Patch15: 0015-Don-t-convert-QByteArray-in-startDrag.patch
Patch16: 0016-Fix-build-after-95290f66b806a307b8da1f72f8fc2c698019.patch
Patch17: 0017-Implement-accessibility-for-QQuickWidget.patch
Patch18: 0018-Send-ObjectShow-event-for-visible-components-after-i.patch
Patch19: 0019-QQuickItem-avoid-emitting-signals-during-destruction.patch
Patch20: 0020-a11y-track-item-enabled-state.patch
Patch21: 0021-Make-QaccessibleQuickWidget-private-API.patch


## upstreamable patches
Patch100: qt5-qtdeclarative-gcc11.patch
# https://pagure.io/fedora-kde/SIG/issue/82
Patch101: qtdeclarative-5.15.0-FixMaxXMaxYExtent.patch

# filter qml provides
%global __provides_exclude_from ^%{_opt_qt5_archdatadir}/qml/.*\\.so$

Obsoletes: opt-qt5-qtjsbackend < 5.2.0
Obsoletes: opt-qt5-qtdeclarative-render2d < 5.7.1-10

BuildRequires: make
BuildRequires: gcc-c++
BuildRequires: opt-qt5-rpm-macros
BuildRequires: opt-qt5-qtbase-devel >= %{version}
BuildRequires: opt-qt5-qtbase-private-devel
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
BuildRequires: python3-base

%if 0%{?tests}
BuildRequires: dbus-x11
BuildRequires: mesa-dri-drivers
BuildRequires: time
BuildRequires: xorg-x11-server-Xvfb
%endif

%description
%{summary}.

%package devel
Summary: Development files for %{name}
Obsoletes: opt-qt5-qtjsbackend-devel < 5.2.0
Obsoletes: opt-qt5-qtdeclarative-render2d-devel < 5.7.1-10
Provides:  %{name}-private-devel = %{version}-%{release}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: opt-qt5-qtbase-devel%{?_isa}
%description devel
%{summary}.

%package static
Summary: Static library files for %{name}
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
%description static
%{summary}.

%prep
%setup -q -n %{name}-%{version}/upstream


%build

# HACK so calls to "python" get what we want
ln -s %{__python3} python
export PATH=`pwd`:$PATH

%opt_qmake_qt5

%make_build

# bug in sb2 leading to 000 permission in some generated plugins.qmltypes files
chmod -R ugo+r .

%install
%make_install INSTALL_ROOT=%{buildroot}

%ifarch %{multilib_archs}
# multilib: qv4global_p.h
  mv %{buildroot}%{_opt_qt5_headerdir}/QtQml/%{version}/QtQml/private/qv4global_p.h \
     %{buildroot}%{_opt_qt5_headerdir}/QtQml/%{version}/QtQml/private/qv4global_p-%{__isa_bits}.h
  install -p -m644 -D %{SOURCE5} %{buildroot}%{_opt_qt5_headerdir}/QtQml/%{version}/QtQml/private/qv4global_p.h
%endif

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_opt_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  rm -fv "$(basename ${prl_file} .prl).la"
  sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
done
popd


%check
%if 0%{?tests}
export CTEST_OUTPUT_ON_FAILURE=1
export PATH=%{buildroot}%{_opt_qt5_bindir}:$PATH
export LD_LIBRARY_PATH=%{buildroot}%{_opt_qt5_libdir}
make sub-tests-all %{?_smp_mflags}
xvfb-run -a \
dbus-launch --exit-with-session \
time \
make check -k -C tests ||:
%endif


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE.LGPL*
%{_opt_qt5_libdir}/libQt5Qml.so.5*
%{_opt_qt5_libdir}/libQt5QmlModels.so.5*
%{_opt_qt5_libdir}/libQt5QmlWorkerScript.so.5*
%{_opt_qt5_libdir}/libQt5Quick.so.5*
%{_opt_qt5_libdir}/libQt5QuickWidgets.so.5*
%{_opt_qt5_libdir}/libQt5QuickParticles.so.5*
%{_opt_qt5_libdir}/libQt5QuickShapes.so.5*
%{_opt_qt5_libdir}/libQt5QuickTest.so.5*
%{_opt_qt5_plugindir}/qmltooling/
%{_opt_qt5_archdatadir}/qml/

%files devel
%{_opt_qt5_bindir}/qml*
%{_opt_qt5_headerdir}/Qt*/
%{_opt_qt5_libdir}/libQt5Qml.so
%{_opt_qt5_libdir}/libQt5Qml.prl
%{_opt_qt5_libdir}/libQt5QmlModels.so
%{_opt_qt5_libdir}/libQt5QmlModels.prl
%{_opt_qt5_libdir}/libQt5QmlWorkerScript.so
%{_opt_qt5_libdir}/libQt5QmlWorkerScript.prl
%{_opt_qt5_libdir}/libQt5Quick*.so
%{_opt_qt5_libdir}/libQt5Quick*.prl
%dir %{_opt_qt5_libdir}/cmake/Qt5Quick*/
%{_opt_qt5_libdir}/cmake/Qt5*/Qt5*Config*.cmake
%{_opt_qt5_libdir}/metatypes/qt5*_metatypes.json
%{_opt_qt5_libdir}/pkgconfig/Qt5*.pc
%{_opt_qt5_archdatadir}/mkspecs/modules/*.pri
%{_opt_qt5_archdatadir}/mkspecs/features/*.prf
%dir %{_opt_qt5_libdir}/cmake/Qt5Qml/
%{_opt_qt5_libdir}/cmake/Qt5Qml/Qt5Qml_*Factory.cmake
%{_opt_qt5_libdir}/cmake/Qt5QmlImportScanner/

%files static
%{_opt_qt5_libdir}/libQt5QmlDevTools.a
%{_opt_qt5_libdir}/libQt5QmlDevTools.prl
%{_opt_qt5_libdir}/libQt5PacketProtocol.a
%{_opt_qt5_libdir}/libQt5PacketProtocol.prl
%{_opt_qt5_libdir}/libQt5QmlDebug.a
%{_opt_qt5_libdir}/libQt5QmlDebug.prl


%changelog
* Thu Jan 05 2023 Jan Grulich <jgrulich@redhat.com> - 5.15.8-1
- 5.15.8

* Mon Oct 31 2022 Jan Grulich <jgrulich@redhat.com> - 5.15.7-1
- 5.15.7

* Tue Sep 20 2022 Jan Grulich <jgrulich@redhat.com> - 5.15.6-1
- 5.15.6

* Sat Jul 23 2022 Fedora Release Engineering <releng@fedoraproject.org> - 5.15.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Wed Jul 13 2022 Jan Grulich <jgrulich@redhat.com> - 5.15.5-1
- 5.15.5

* Mon May 16 2022 Jan Grulich <jgrulich@redhat.com> - 5.15.4-1
- 5.15.4

* Mon Mar 07 2022 Jan Grulich <jgrulich@redhat.com> - 5.15.3-2
- Disable LTO

* Fri Mar 04 2022 Jan Grulich <jgrulich@redhat.com> - 5.15.3-1
- 5.15.3 + kde-5.15 fixes

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 5.15.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Wed Nov 17 2021 Rex Dieter <rdieter@fedoraproject.org> - 5.15.2-10
- sync kde/5.15 branch fixes

* Sat Oct 30 2021 Rex Dieter <rdieter@fedoraproject.org> - 5.15.2-9
- sync kde/5.15 branch fixes

* Mon Oct 18 2021 Adam Williamson <awilliam@redhat.com> - 5.15.2-8
- Backport Qt review #372646 to partially fix #2011774

* Fri Jul 30 2021 Rex Dieter <rdieter@fedoraproject.org> - 5.15.2-7
- sync kde/5.15 branch fixes
- pull in candidate fix QTBUG-83890

* Fri Jul 23 2021 Fedora Release Engineering <releng@fedoraproject.org> - 5.15.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Tue Jun 01 2021 Rex Dieter <rdieter@fedoraproject.org> - 5.15.2-5
- pull in kde/5.15 branch fixes

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 5.15.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Dec 10 12:36:25 CET 2020 Jan Grulich <jgrulich@redhat.com> - 5.15.2-3
- Bump for eln build

* Tue Nov 24 07:54:13 CET 2020 Jan Grulich <jgrulich@redhat.com> - 5.15.2-2
- Rebuild for qtbase with -no-reduce-relocations option

* Fri Nov 20 09:30:45 CET 2020 Jan Grulich <jgrulich@redhat.com> - 5.15.2-1
- 5.15.2

* Fri Oct 16 2020 Jeff Law <law@redhat.com> - 5.15.1-2
- Fix missing #includes for gcc-11

* Thu Sep 10 2020 Jan Grulich <jgrulich@redhat.com> - 5.15.1-1
- 5.15.1

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 5.14.2-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 5.14.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sat Apr 04 2020 Rex Dieter <rdieter@fedoraproject.org> - 5.14.2-1
- 5.14.2

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 5.13.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Dec 09 2019 Jan Grulich <jgrulich@redhat.com> - 5.13.2-1
- 5.13.2

* Wed Oct 16 2019 Jan Grulich <jgrulich@redhat.com> - 5.12.5-4
- Drop revert of upstream change

* Tue Oct 08 2019 Rex Dieter <rdieter@fedoraproject.org> - 5.12.5-3
- bisected different upstream commit as culprit for plasma notification crasher (#1758263)

* Mon Oct 07 2019 Rex Dieter <rdieter@fedoraproject.org> - 5.12.5-2
- revert upstream commit possibly related to plasma notification applet crashes (#1758263)

* Tue Sep 24 2019 Jan Grulich <jgrulich@redhat.com> - 5.12.5-1
- 5.12.5

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.12.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Jul 16 2019 Rex Dieter <rdieter@fedoraproject.org> - 5.12.4-2
- build with python3

* Fri Jun 14 2019 Jan Grulich <jgrulich@redhat.com> - 5.12.4-1
- 5.12.4

* Tue Jun 04 2019 Jan Grulich <jgrulich@redhat.com> - 5.12.3-1
- 5.12.3

* Fri Mar 15 2019 Rex Dieter <rdieter@fedoraproject.org> - 5.12.1-2
- de-bootstrap

* Mon Feb 04 2019 Rex Dieter <rdieter@fedoraproject.org> - 5.12.1-1
- 5.12.1
- drop remants of sse2 hack support
- add bootstrap support (examples)

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.11.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Dec 07 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.11.3-1
- 5.11.3

* Fri Sep 21 2018 Jan Grulich <jgrulich@redhat.com> - 5.11.2-1
- 5.11.2

* Sun Jul 15 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.11.1-3
- BR: /usr/bin/python

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 5.11.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.11.1-1
- 5.11.1

* Mon Jun 18 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.11.0-2
- %%ix86: nosse2_hack on < f29 only

* Wed May 23 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.11.0-1
- 5.11.0
- i686: use nosse2_hack again

* Tue Apr 03 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.10.1-5
- pull in candidate memleak fix (review#224684)

* Sun Mar 18 2018 Iryna Shcherbina <ishcherb@redhat.com> - 5.10.1-4
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Mar 08 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.10.1-3
- BR: qt5-rpm-macros

* Mon Mar 05 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.10.1-2
- BR: gcc-c++, use %%make_build %%make_install %%ldconfig_scriptlets

* Tue Feb 13 2018 Jan Grulich <jgrulich@redhat.com> - 5.10.1-1
- 5.10.1

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 5.10.0-2
- Escape macros in %%changelog

* Tue Dec 19 2017 Jan Grulich <jgrulich@redhat.com> - 5.10.0-1
- 5.10.0

* Thu Nov 23 2017 Jan Grulich <jgrulich@redhat.com> - 5.9.3-1
- 5.9.3

* Tue Oct 31 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.9.2-3
- Obsoletes: qt5-qtdeclarative-render2d

* Thu Oct 26 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.9.2-2
- revert commit causing regresions (QTBUG-64017)

* Mon Oct 09 2017 Jan Grulich <jgrulich@redhat.com> - 5.9.2-1
- 5.9.2

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.9.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 19 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.9.1-1
- 5.9.1

* Thu Jun 15 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.9.0-3
- drop shadow/out-of-tree builds (#1456211,QTBUG-37417)
- use debian's i686/sse2 support patch

* Fri Jun 02 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.9.0-2
- rebuild

* Wed May 31 2017 Helio Chissini de Castro <helio@kde.org> - 5.9.0-1
- Upstream official release

* Fri May 26 2017 Helio Chissini de Castro <helio@kde.org> - 5.9.0-0.1.rc
- Upstream Release Candidate retagged

* Wed May 24 2017 Helio Chissini de Castro <helio@kde.org> - 5.9.0-0.rc.1
- Upstream Release Candidate 1

* Sun May 14 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.9.0-0.5.beta3
- Conflict in qt5-qtdeclarative-devel (#1441343), fix Release: 1%%{?dist}

* Mon May 08 2017 Than Ngo <than@redhat.com> - 5.9.0-0.beta.4
- drop useless qtdeclarative-opensource-src-5.9.0-v4bootstrap.patch,
  apply correct qtdeclarative-opensource-src-5.9.0-no_sse2.patch to
  fix the build issue in JIT on ppc64/ppc64le/s390x

* Fri May 05 2017 Helio Chissini de Castro <helio@kde.org> - 5.9.0-0.beta.3
- New upstream beta3 release

* Sun Apr 16 2017 Helio Chissini de Castro <helio@kde.org> - 5.9.0-0.beta.1
- New upstream beta release

* Mon Apr 03 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.8.0-3
- build -doc on all archs

* Thu Mar 30 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.8.0-2
- de-bootstrap

* Fri Jan 27 2017 Helio Chissini de Castro <helio@kde.org> - 5.8.0-1
- New upstream version
- bootstrap

* Mon Jan 02 2017 Rex Dieter <rdieter@math.unl.edu> - 5.7.1-6
- filter qml provides

* Sat Dec 17 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.7.1-5
- restore bootstrap/doc macros, drop pkgconfig-style deps (for now)

* Sat Dec 10 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.7.1-4
- drop BR: cmake (handled by qt5-rpm-macros now)

* Fri Dec 09 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.7.1-3
- rebuild

* Fri Dec 09 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.7.1-2
- 5.7.1 dec5 snapshot

* Wed Nov 09 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.1-1
- New upstream version

* Mon Jul 04 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.0-2
- Compiled with gcc

* Tue Jun 14 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.0-1
- Qt 5.7.0 release

* Thu Jun 09 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.0-0.1
- Prepare for 5.7.0

* Thu Jun 09 2016 Jan Grulich <jgrulich@redhat.com> - 5.6.1-1
- Update to 5.6.1

* Thu Jun 02 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-12
- pull in upstream qml/jsruntime workaround (ie, apply compiler workarounds only for src/qml/)

* Tue May 31 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-11
- include crasher workaround (#1259472,kde#346118)

* Sat May 28 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-10
- macro'ize no_sse2 hack (to make it easier to enable/disable)
- re-introduce -fno-delete-null-pointer-checks here (following upstream)
- add -fno-lifetime-dse too, helps fix i686/qml crasher (#1331593)
- disable tests (for now, not useful yet)

* Fri May 20 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-9
- Use system double-conversion (#1078524)

* Thu May 19 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-8
- -devel: don't own libQt5QuickWidgets.so.5 (#1337621)

* Thu May 05 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-7
- BR: mesa-dri-drivers (tests)

* Thu May 05 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-6
- drop local -fno-delete-null-pointer-checks hack, used in all Qt5 builds now
- add %%check

* Sun Apr 17 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-5
- BR: qt5-qtbase-private-devel, -devel: Provides: -private-devel

* Fri Mar 25 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-4
- backport upstream fixes
- drop -fno-delete-null-pointer-checks hack (included in qt5-rpm-macros as needed now)

* Sat Mar 19 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-3
- BR: cmake (cmake autoprovides)

* Fri Mar 18 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-2
- rebuild

* Mon Mar 14 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-1
- 5.6.0 final release

* Tue Feb 23 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.11.rc
- Update to final RC

* Mon Feb 22 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.10
- Update RC tarball from git

* Mon Feb 15 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.9
- Update RC release

* Tue Feb 02 2016 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.8.beta3
- build with -fno-delete-null-pointer-checks to workaround gcc6-related runtime crashes (#1303643)

* Thu Jan 28 2016 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.7.beta3
- backport fix for older compilers (aka rhel6)

* Sun Jan 17 2016 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.6.beta3
- use %%license

* Mon Dec 21 2015 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.5.beta3
- fix Source URL, Release: 1%%{?dist}

* Mon Dec 21 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.4
- Update to final beta3 release

* Thu Dec 10 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.3
- Official beta3 release

* Sun Dec 06 2015 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.2
- de-bootstrap

* Tue Nov 03 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.1
- Start to implement 5.6.0 beta3, bootstrap

* Sat Oct 24 2015 Rex Dieter <rdieter@fedoraproject.org> 5.5.1-3
- workaround QQuickShaderEffectSource::updatePaintNode deadlock (#1237269, kde#348385)

* Thu Oct 15 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.1-2
- Update to final release 5.5.1

* Tue Sep 29 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.1-1
- Update to Qt 5.5.1 RC1

* Wed Jul 29 2015 Rex Dieter <rdieter@fedoraproject.org> 5.5.0-3
- -docs: BuildRequires: qt5-qhelpgenerator

* Thu Jul 16 2015 Rex Dieter <rdieter@fedoraproject.org> 5.5.0-2
- tighten qtbase dep (#1233829), .spec cosmetics

* Wed Jul 1 2015 Helio Chissini de Castro <helio@kde.org> 5.5.0-1
- New final upstream release Qt 5.5.0

* Mon Jun 29 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-0.4.rc
- Second round of builds now with bootstrap enabled due new qttools

* Sat Jun 27 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-0.3.rc
- Disable bootstrap

* Wed Jun 24 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-0.2.rc
- Update for official RC1 released packages

* Mon Jun 08 2015 Rex Dieter <rdieter@fedoraproject.org> 5.4.2-2
- restore fix for QTBUG-45753/kde-345544 lost in 5.4.2 rebase

* Wed Jun 03 2015 Jan Grulich <jgrulich@redhat.com> 5.4.2-1
- 5.4.2

* Sat May 02 2015 Rex Dieter <rdieter@fedoraproject.org> 5.4.1-4
- pull in some upstream fixes, for QTBUG-45753/kde-345544 in particular

* Wed Apr 22 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.4.1-3
- fix non-sse2 support (kde#346244) and optimize sse2 binaries

* Fri Feb 27 2015 Rex Dieter <rdieter@fedoraproject.org> - 5.4.1-2
- rebuild (gcc5)

* Tue Feb 24 2015 Jan Grulich <jgrulich@redhat.com> 5.4.1-1
- 5.4.1

* Mon Feb 16 2015 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-3
- rebuild (gcc)

* Sat Feb 14 2015 Ville Skyttä <ville.skytta@iki.fi> - 5.4.0-2
- Fix cmake dir ownerhips

* Wed Dec 10 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-1
- 5.4.0 (final)

* Fri Nov 28 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.3.rc
- 5.4.0-rc

* Mon Nov 03 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.2.beta3
- use new %%opt_qmake_qt5 macro

* Sat Oct 18 2014 Rex Dieter <rdieter@fedoraproject.org> - 5.4.0-0.1.beta3
- 5.4.0-beta3
- %%ix84: drop sse2-optimized bits, need to rethink if/how to support it now

* Tue Sep 16 2014 Rex Dieter <rdieter@fedoraproject.org> 5.3.2-1
- 5.3.2

* Tue Sep 16 2014 Rex Dieter <rdieter@fedoraproject.org> 5.3.1-3
- -qt5 wrappers for qml qmlbundle qmlmin qmlscene

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 17 2014 Jan Grulich <jgrulich@redhat.com> - 5.3.1-1
- 5.3.1

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 21 2014 Jan Grulich <jgrulich@redhat.com> 5.3.0-1
- 5.3.0

* Wed Feb 05 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.1-1
- 5.2.1

* Sun Feb 02 2014 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> 5.2.0-6
- Add AArch64 support (RHBUG: 1040452, QTBUG-35528)

* Mon Jan 27 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-5
- build -examples only if supported

* Sun Jan 26 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-4
- -examples subpkg

* Tue Jan 14 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-3
- epel7 bootstrapped

* Mon Jan 06 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-2
- BR: qt5-qtxmlpatterns-devel (#1048558)

* Thu Dec 12 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-1
- 5.2.0

* Tue Dec 10 2013 Rex Dieter <rdieter@fedoraproject.org> - 5.2.0-0.12.rc1
- support out-of-src-tree builds
- %%ix86: install sse2/jit version to %%_qt5_libdir/sse2/

* Thu Dec 05 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.11.rc1
- %%ix86: cannot assume sse2 (and related support) or the JIT that requires it...  disable.

* Mon Dec 02 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.10.rc1
- 5.2.0-rc1

* Mon Nov 25 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.5.beta31
- enable -doc only on primary archs (allow secondary bootstrap)

* Sat Nov 09 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.4.beta31
- rebuild (arm/qreal)

* Thu Oct 24 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.3.beta31
- 5.2.0-beta31

* Wed Oct 16 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.2.alpha
- bootstrap ppc

* Tue Oct 01 2013 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-0.1.alpha
- 5.2.0-alpha
- Obsoletes: qt5-qtjsbackend
- -doc subpkg

* Wed Aug 28 2013 Rex Dieter <rdieter@fedoraproject.org> 5.1.1-1
- 5.1.1

* Tue Aug 20 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-4
- qt5-qtjsbackend only supports ix86, x86_64 and arm

* Tue May 14 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-3
- fix qmlprofiler conflict with qt-creator

* Fri Apr 12 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-2
- fix qmlplugindump conflict with qt4-devel
- include license files, dist/changes*

* Thu Apr 11 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.2-1
- 5.0.2

* Sat Feb 23 2013 Rex Dieter <rdieter@fedoraproject.org> 5.0.1-1
- first try





