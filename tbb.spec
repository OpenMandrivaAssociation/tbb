%define tbbmajor 12
%define major 2
#define beta rc2

%define libtbb %mklibname tbb
%define libtbbbind %mklibname tbbind
%define libtbbmalloc %mklibname tbbmalloc
%define libtbbmalloc_proxy %mklibname tbbmalloc_proxy
%define libirml %mklibname irml
%define devname %mklibname -d tbb
%define oldlibirml %mklibname irml 1
%define oldlibtbb %mklibname tbb 12
%define oldlibtbbmalloc %mklibname tbbmalloc 2
%define oldlibtbbmalloc_proxy %mklibname tbbmalloc_proxy 2


Summary:	Thread Building Blocks
Name:		tbb
Version:	2021.13.0
Release:	1
#Release:	%{?beta:0.%{beta}.}1
Url:		https://oneapi-src.github.io/oneTBB/
Source0:	https://github.com/oneapi-src/oneTBB/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
#Source0:	https://github.com/intel/tbb/archive/v%{version}/%{name}-%{version}%{?beta:-%{beta}}.tar.gz
Patch0:		tbb-21.5-no-Werror.patch
License:	Apache 2.0
Group:		System/Libraries
BuildRequires:	ninja
BuildRequires:	doxygen
BuildRequires:	graphviz
BuildRequires:	pkgconfig(hwloc)
BuildRequires:	pkgconfig(python3)
BuildRequires:	swig
BuildRequires:	cmake

%description
Thread Building Blocks

#-----------------------------------------------------------------------

%package -n %{libtbb}
Summary:	Thread Building Blocks library
Group:		System/Libraries
Obsoletes:	%{oldlibtbb} < %{EVRD}

%description -n %{libtbb}
Thread Building Blocks library

%files -n %{libtbb}
%{_libdir}/libtbb.so.%{tbbmajor}*

#-----------------------------------------------------------------------

%package -n %{libtbbmalloc}
Summary:	Thread Building Blocks library
Group:		System/Libraries
Obsoletes:	%{oldlibtbbmalloc} < %{EVRD}

%description -n %{libtbbmalloc}
Thread Building Blocks library

%files -n %{libtbbmalloc}
%{_libdir}/libtbbmalloc.so.%{major}*

#-----------------------------------------------------------------------

%package -n %{libtbbbind}
Summary:	Thread Building Blocks library
Group:		System/Libraries


%description -n %{libtbbbind}
Thread Building Blocks library

%files -n %{libtbbbind}
%{_libdir}/libtbbbind_2_5.so.3*

#-----------------------------------------------------------------------

%package -n %{libtbbmalloc_proxy}
Summary:	Thread Building Blocks library
Group:		System/Libraries
Obsoletes:	%{oldlibtbbmalloc_proxy} < %{EVRD}

%description -n %{libtbbmalloc_proxy}
Thread Building Blocks library

%files -n %{libtbbmalloc_proxy}
%{_libdir}/libtbbmalloc_proxy.so.%{major}*

#-----------------------------------------------------------------------

%package -n %{libirml}
Summary:	Thread Building Blocks library
Group:		System/Libraries
Obsoletes:	%{oldlibirml} < %{EVRD}

%description -n %{libirml}
Thread Building Blocks library

%files -n %{libirml}
%{_libdir}/libirml.so.1

#-----------------------------------------------------------------------

%package -n %{devname}
Summary:	Development files for the Thread Building Blocks library
Group:		Development/C++ and C
Requires:	%{libtbb} = %{EVRD}
Requires:	%{libtbbmalloc} = %{EVRD}
Requires:	%{libtbbmalloc_proxy} = %{EVRD}
Requires:	%{libirml} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
Development files for the Thread Building Blocks library

%files -n %{devname}
%doc %{_docdir}/TBB/README.md
%{_includedir}/oneapi
%{_includedir}/tbb
%{_libdir}/*.so
%{_libdir}/cmake/TBB
%{_libdir}/pkgconfig/*.pc

#-----------------------------------------------------------------------

%package -n python-%{name}
Summary:	Python bindings for Thread Building Blocks
Group:		System/Libraries

%description -n python-%{name}
Python bindings for Thread Building Blocks

%files -n python-%{name}
%{python3_sitearch}/TBB*

#-----------------------------------------------------------------------

%prep
%autosetup -p1 -n oneTBB-%{version}%{?beta:-%{beta}}

%if "%{_lib}" != "lib"
sed -i -e 's,/build/lib,/build/%{_lib},g' python/CMakeLists.txt
%endif

export LDFLAGS="$LDFLAGS -Wl,--undefined-version"

%cmake \
	-DTBB_STRICT:BOOL=ON \
	-DTBB4PY_BUILD:BOOL=ON \
	-G Ninja

%build
%ninja_build -C build
%ninja_build -C build python_build

%install
%ninja_install -C build

#rm cmake/README.md
#cp -a cmake %{buildroot}%{_libdir}/cmake/%{name}

mkdir -p %{buildroot}%{_libdir}/pkgconfig
for i in tbb tbbmalloc tbbmalloc_proxy irml; do
	cat >%{buildroot}%{_libdir}/pkgconfig/$i.pc <<EOF
Name: Thread Building Blocks - $i
Description: %{summary}
URL: https://threadbuildingblocks.org/
Version: %{version}
Libs: -l$i
EOF
done
