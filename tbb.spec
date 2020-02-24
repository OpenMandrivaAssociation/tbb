%define major 2

%define libtbb %mklibname tbb %{major}
%define libtbbmalloc %mklibname tbbmalloc %{major}
%define libtbbmalloc_proxy %mklibname tbbmalloc_proxy %{major}
%define libirml %mklibname irml 1
%define devname %mklibname -d tbb

Summary:	Thread Building Blocks
Name:		tbb
Version:	2020.1
Release:	2
Url:		http://threadbuildingblocks.org/
Source0:	https://github.com/intel/tbb/archive/v%{version}/%{name}-%{version}.tar.gz
License:	Apache 2.0
Group:		System/Libraries
BuildRequires:	make
BuildRequires:	doxygen graphviz
BuildRequires:	pkgconfig(python3)
BuildRequires:	swig
# Only for the dependency generator
BuildRequires:	cmake
# Don't snip -Wall from C++ flags.  Add -fno-strict-aliasing, as that
# uncovers some static-aliasing warnings.
# Related: https://bugzilla.redhat.com/show_bug.cgi?id=1037347
Patch0:		https://src.fedoraproject.org/rpms/tbb/raw/master/f/tbb-2019-dont-snip-Wall.patch
# Make attributes of aliases match those on the aliased function.
Patch1:		https://src.fedoraproject.org/rpms/tbb/raw/master/f/tbb-2019-attributes.patch
# Fix test-thread-monitor, which had multiple bugs that could (and did, on
# ppc64le) result in a hang.
Patch2:		https://src.fedoraproject.org/rpms/tbb/raw/master/f/tbb-2019-test-thread-monitor.patch
# Fix a test that builds a 4-thread barrier, but cannot guarantee that more
# than 2 threads will be available to use it.
Patch3:		https://src.fedoraproject.org/rpms/tbb/raw/master/f/tbb-2019-test-task-scheduler-init.patch
# Fix compilation on aarch64 and s390x.  See
# https://github.com/intel/tbb/issues/186
Patch4:		https://src.fedoraproject.org/rpms/tbb/raw/master/f/tbb-2019-fetchadd4.patch

%description
Thread Building Blocks

%package -n %{libtbb}
Summary:	Thread Building Blocks library
Group:		System/Libraries

%description -n %{libtbb}
Thread Building Blocks library

%files -n %{libtbb}
%{_libdir}/libtbb.so.%{major}

%package -n %{libtbbmalloc}
Summary:	Thread Building Blocks library
Group:		System/Libraries

%description -n %{libtbbmalloc}
Thread Building Blocks library

%files -n %{libtbbmalloc}
%{_libdir}/libtbbmalloc.so.%{major}

%package -n %{libtbbmalloc_proxy}
Summary:	Thread Building Blocks library
Group:		System/Libraries

%description -n %{libtbbmalloc_proxy}
Thread Building Blocks library

%files -n %{libtbbmalloc_proxy}
%{_libdir}/libtbbmalloc_proxy.so.%{major}

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
%doc html
%{_includedir}/tbb
%{_includedir}/rml
%{_includedir}/serial
%{_libdir}/*.so
%{_libdir}/cmake/tbb
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
%autosetup -p1

%build
if echo %{__cc} | grep -q gcc; then
	COMPILER=gcc
else
	# Workaround for clang bug
	COMPILER=gcc #clang
fi
%make_build all compiler=$COMPILER stdver=c++2a \
	CXXFLAGS="%{optflags} -DDO_ITT_NOTIFY -DUSE_PTHREAD" \
	LDFLAGS="%{ldflags} -pthread"

. build/*_release/tbbvars.sh
cd python
%make_build -C rml stdver=c++2a \
	CPLUS_FLAGS="%{optflags} -DDO_ITT_NOTIFY -DUSE_PTHREAD" \
	LDFLAGS="%{ldflags} -pthread"
cp -a rml/libirml.so* .
%py3_build
cd -

%make_build doxygen


%install
mkdir -p %{buildroot}%{_libdir}/cmake %{buildroot}%{_libdir}/pkgconfig
install -p -D -m 755 build/*_release/*.so.%{major} %{buildroot}%{_libdir}/

cd %{buildroot}%{_libdir}
for i in *.so.*; do
	ln -s $i $(echo $i |sed -e 's,\.so\..*,.so,')
done
cd -

cp -a include %{buildroot}%{_includedir}
cp -a src/rml/include %{buildroot}%{_includedir}/rml

find %{buildroot}%{_includedir} -name "*.html" |xargs rm -f

. build/*_release/tbbvars.sh
cd python
%py3_install
find %{buildroot} -name "*.py" |xargs chmod +x
cp -a libirml.so.1 %{buildroot}%{_libdir}/
ln -s libirml.so.1 %{buildroot}%{_libdir}/libirml.so
cd -

rm cmake/README.rst
cp -a cmake %{buildroot}%{_libdir}/cmake/%{name}

for i in tbb tbbmalloc tbbmalloc_proxy irml; do
	cat >%{buildroot}%{_libdir}/pkgconfig/$i.pc <<EOF
Name: Thread Building Blocks - $i
Description: %{summary}
URL: http://threadbuildingblocks.org/
Version: %{version}
Libs: -l$i
EOF
done
