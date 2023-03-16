%define keepstatic 1

%global qt_version 5.15.8

Summary: Qt5 - QtDeclarative component
Name: opt-qt5-qtdeclarative
Version: 5.15.8
Release: 1%{?dist}

# See LICENSE.GPL LICENSE.LGPL LGPL_EXCEPTION.txt, for details
License: LGPLv2 with exceptions or GPLv3 with exceptions
Url:     http://www.qt.io
Source0: %{name}-%{version}.tar.bz2

# filter qml provides
%global __provides_exclude_from ^%{_opt_qt5_archdatadir}/qml/.*\\.so$

BuildRequires: make
BuildRequires: gcc-c++
BuildRequires: opt-qt5-rpm-macros
BuildRequires: opt-qt5-qtbase-devel >= %{qt_version}
BuildRequires: opt-qt5-qtbase-private-devel
%{?_qt5:Requires: %{_opt_qt5}%{?_isa} = %{_opt_qt5_version}}
Requires: opt-qt5-qtbase-gui
BuildRequires: python3-base

%description
%{summary}.

%package tools
Summary: Tools for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
%description tools
%{summary}.

%package devel
Summary: Development files for %{name}
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
%autosetup -n %{name}-%{version}/upstream

%build

export QTDIR=%{_opt_qt5_prefix}
touch .git

%opt_qmake_qt5

make %{?_smp_mflags}

# bug in sb2 leading to 000 permission in some generated plugins.qmltypes files
chmod -R ugo+r .

%install
%make_install INSTALL_ROOT=%{buildroot}

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_opt_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  rm -fv "$(basename ${prl_file} .prl).la"
  sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
done
popd


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

%files tools
%{_opt_qt5_bindir}/qml*

%files devel
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
