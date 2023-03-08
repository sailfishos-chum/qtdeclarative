%define _prefix /opt/qt5/
%define qmake5 %{_prefix}/lib64/qt5/bin/qmake

Name:       qt5-lgpl-qtdeclarative
Summary:    Qt Declarative library
Version:    5.15.8
Release:    1%{?dist}
License:    (LGPLv2 or LGPLv3) with exception or GPLv3 or Qt Commercial
URL:        https://www.qt.io/
Source0:    %{name}-%{version}.tar.bz2
BuildRequires:  qt5-lgpl-qtcore-devel >= 5.15.8
BuildRequires:  qt5-lgpl-qtgui-devel >= 5.15.8
BuildRequires:  qt5-lgpl-qtnetwork-devel
BuildRequires:  qt5-lgpl-qtsql-devel
BuildRequires:  qt5-lgpl-qttest-devel
BuildRequires:  qt5-lgpl-qtxmlpatterns-devel
BuildRequires:  qt5-lgpl-qmake
BuildRequires:  fdupes
BuildRequires:  python3-base
BuildRequires:  gdb
BuildRequires:  qml-rpm-macros

%description
Qt is a cross-platform application and UI framework. Using Qt, you can
write web-enabled applications once and deploy them across desktop,
mobile and embedded systems without rewriting the source code.
.
This package contains the Declarative library

%package devel
Summary:        Qt Development Kit
Group:          Development/Libraries/X11
Requires:       %{name} = %{version}
Requires:       %{name}-tools = %{version}
Provides:       libQt5Quick-devel = %{version}
Obsoletes:      libQt5Quick-devel < %{version}

%description devel
You need this package, if you want to compile programs with qtdeclarative.

%package tools
Summary:        Qt 5 Declarative Tools
Group:          Development/Tools/Debuggers
License:        GPL-3.0-only

%description tools
Qt is a set of libraries for developing applications.

This package contains aditional tools for inspecting, testing, viewing, etc, QML imports and files.

%description private-headers-devel
This package provides private headers of libqt5-qtdeclarative that are normally
not used by application development and that do not have any ABI or
API guarantees. The packages that build against these have to require
the exact Qt version.

%prep
%autosetup -n %{name}-%{version}/upstream

%build
export QTDIR=%{_prefix}
touch .git

%ifarch %arm
# to enable JIT, we need to enable thumb, as it is the only supported
# configuration for JIT on ARM. unfortunately, we are not currently in the right
# frame of mind to be able to deal with a full thumb transition, so we need to
# hack it in.
#
# OBS forces -mno-thumb, so first step, we need to remove that, and then add our
# own thumb argument. we can't do this in the .pro, as it won't propegate. we
# can't do it in .qmake.conf, because that's loaded too early. -after is *just*
# the right place: it's after everything has happened except for
# default_post.prf, which sets up the real QMAKE_C{XX}FLAGS, so brutally abuse
# it to acomplish our evil goals.
%qmake5 \
    QT.widgets.name= DEFINES+=QT_NO_WIDGETS \
    -after \
    QMAKE_CFLAGS_RELEASE-=-mno-thumb     QMAKE_CFLAGS_DEBUG-=-mno-thumb \
    QMAKE_CXXFLAGS_RELEASE-=-mno-thumb   QMAKE_CXXFLAGS_DEBUG-=-mno-thumb \
    QMAKE_CFLAGS_RELEASE+=-mthumb        QMAKE_CFLAGS_DEBUG+=-mthumb \
    QMAKE_CXXFLAGS_RELEASE+=-mthumb      QMAKE_CXXFLAGS_DEBUG+=-mthumb
%else
%qmake5
%endif

make %{?_smp_mflags}

%install
%qmake5_install
# Fix wrong path in pkgconfig files
find %{buildroot}%{_libdir}/pkgconfig -type f -name '*.pc' \
-exec perl -pi -e "s, -L%{_builddir}/?\S+,,g" {} \;
# Fix wrong path in prl files
find %{buildroot}%{_libdir} -type f -name '*.prl' \
-exec sed -i -e "/^QMAKE_PRL_BUILD_DIR/d;s/\(QMAKE_PRL_LIBS =\).*/\1/" {} \;
# Remove unneeded .la files
rm -f %{buildroot}/%{_libdir}/*.la

# We don't need qt5/Qt/
rm -rf %{buildroot}/%{_includedir}/qt5/Qt

# Manually copy qmldevtools static library
cp lib/libQt5QmlDevTools.a %{buildroot}/%{_libdir}
%fdupes %{buildroot}/%{_libdir}
%fdupes %{buildroot}/%{_includedir}


# Copy docs
mkdir -p %{buildroot}/%{_docdir}/qt5/qtqml
mkdir -p %{buildroot}/%{_docdir}/qt5/qtquick


#### Pre/Post section

%post
/sbin/ldconfig
%postun
/sbin/ldconfig

#### File section


%files
%license LICENSE.*
%{_libdir}/libQt5Q*.so.*
%dir %{_libdir}/qt5/qml
%dir %{_libdir}/qt5/qml/Qt
%{_libdir}/qt5/qml/QtQuick
%{_libdir}/qt5/qml/QtQuick.2
%{_libdir}/qt5/qml/QtQml
%{_libdir}/qt5/qml/builtins.qmltypes
%dir %{_libdir}/qt5/qml/Qt/labs
%{_libdir}/qt5/qml/Qt/labs/animation/
%{_libdir}/qt5/qml/Qt/labs/folderlistmodel/
%{_libdir}/qt5/qml/Qt/labs/settings/
%{_libdir}/qt5/qml/Qt/labs/sharedimage/
%{_libdir}/qt5/qml/Qt/labs/qmlmodels/
%{_libdir}/qt5/qml/Qt/labs/wavefrontmesh/
%dir %{_libdir}/qt5/qml/Qt/test
%{_libdir}/qt5/qml/Qt/test/qtestroot/
%{_libdir}/qt5/plugins/qmltooling

%files tools
%license LICENSE.*
%{_libdir}/qt5/bin/qmltyperegistrar

%files devel
%license LICENSE.*
%{_includedir}/qt5/Qt*
%{_libdir}/cmake/Qt5*
%{_libdir}/libQt5*.prl
%{_libdir}/libQt5Q*.so
%{_libdir}/libQt5*.a
%{_libdir}/pkgconfig/Qt5Q*.pc
%{_libdir}/metatypes/qt5quick*_metatypes.json
%{_libdir}/metatypes/qt5qml*_metatypes.json
%{_datadir}/qt5/mkspecs/modules/*.pri
%{_datadir}/qt5/mkspecs/features/qmltypes.prf
%{_libdir}/qt5/qml/QtTest
