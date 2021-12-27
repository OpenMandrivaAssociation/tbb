%define tbbmajor 12
%define major 2
#define beta rc2

%define libtbb %mklibname tbb %{tbbmajor}
%define libtbbmalloc %mklibname tbbmalloc %{major}
%define libtbbmalloc_proxy %mklibname tbbmalloc_proxy %{major}
%define libirml %mklibname irml 1
%define devname %mklibname -d tbb

Summary:	Thread Building Blocks
Name:		tbb
Version:	2021.5.0
Release:	%{?beta:0.%{beta}.}1
Url:		http://threadbuildingblocks.org/
Source0:	https://github.com/oneapi-src/oneTBB/archive/refs/tags/v%{version}%{?beta:-%{beta}}.tar.gz
#Source0:	https://github.com/intel/tbb/archive/v%{version}/%{name}-%{version}%{?beta:-%{beta}}.tar.gz
Patch0:		tbb-21.5-no-Werror.patch
License:	Apache 2.0
Group:		System/Libraries
BuildRequires:	ninja
BuildRequires:	doxygen graphviz
BuildRequires:	pkgconfig(python3)
BuildRequires:	swig
BuildRequires:	cmake
#Patch0:		tbb-2021.1.1-compile.patch
#Patch1:		tbb-2021.3.0-compile.patch
# Fix compilation on aarch64 and s390x.  See
# https://github.com/intel/tbb/issues/186
Patch4:		https://src.fedoraproject.org/rpms/tbb/raw/rawhide/f/tbb-2019-fetchadd4.patch

%description
Thread Building Blocks

%package -n %{libtbb}
Summary:	Thread Building Blocks library
Group:		System/Libraries

%description -n %{libtbb}
Thread Building Blocks library

%files -n %{libtbb}
%{_libdir}/libtbb.so.%{tbbmajor}*

%package -n %{libtbbmalloc}
Summary:	Thread Building Blocks library
Group:		System/Libraries

%description -n %{libtbbmalloc}
Thread Building Blocks library

%files -n %{libtbbmalloc}
%{_libdir}/libtbbmalloc.so.%{major}*

%package -n %{libtbbmalloc_proxy}
Summary:	Thread Building Blocks library
Group:		System/Libraries

%description -n %{libtbbmalloc_proxy}
Thread Building Blocks library

%files -n %{libtbbmalloc_proxy}
%{_libdir}/libtbbmalloc_proxy.so.%{major}*

%package -n %{libirml}
Summary:	Thread Building Blocks library
Group:		System/Libraries

%description -n %{libirml}
Thread Building Blocks library

%files -n %{libirml}
%{_libdir}/libirml.so.1

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

%package -n python-%{name}
Summary:	Python bindings for Thread Building Blocks
Group:		System/Libraries

%description -n python-%{name}
Python bindings for Thread Building Blocks

%files -n python-%{name}
%{python3_sitearch}/TBB*
%{python3_sitearch}/tbb
%{python3_sitearch}/__pycache__/TBB*

%prep
%autosetup -p1 -n oneTBB-%{version}%{?beta:-%{beta}}

%if "%{_lib}" != "lib"
sed -i -e 's,/build/lib,/build/%{_lib},g' python/CMakeLists.txt
%endif

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
URL: http://threadbuildingblocks.org/
Version: %{version}
Libs: -l$i
EOF
done
