%global build_branch master
%global pkg_name lldb

%global build_repo https://github.com/llvm/llvm-project

%global maj_ver 14
%global min_ver 0
%global patch_ver 0

%define commit d5166f86a33d718437a1f1d75a9d0efbe5f36e1f
%global commit_date 20210907
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%global gitrel .%{commit_date}.git%{shortcommit}


Name:		%{pkg_name}
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	0.1%{?gitrel}%{?dist}
Summary:	Next generation high-performance debugger

License:	NCSA
URL:      https://llvm.org
Source0:  %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  llvm-devel = %{version}
BuildRequires:  llvm-test = %{version}
BuildRequires:  clang-devel = %{version}
BuildRequires:  ncurses-devel
BuildRequires:  swig
BuildRequires:  llvm-static = %{version}
BuildRequires:  libffi-devel
BuildRequires:  zlib-devel
BuildRequires:  libxml2-devel
BuildRequires:  libedit-devel
BuildRequires:  python3-lit
BuildRequires:  multilib-rpm-config

Requires:	python2-lldb

%description
LLDB is a next generation, high-performance debugger. It is built as a set
of reusable components which highly leverage existing libraries in the
larger LLVM Project, such as the Clang expression parser and LLVM
disassembler.

%package devel
Summary:	Development header files for LLDB
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description devel
The package contains header files for the LLDB debugger.

%package -n python2-lldb
%{?python_provide:%python_provide python2-lldb}
Summary:	Python module for LLDB
BuildRequires:	python2-devel
Requires:	python2-six

%description -n python2-lldb
The package contains the LLDB Python module.

%prep
#force downloading the project, seems that copr dist-cache is poisoned with bogus archive
curl -Lo %{_sourcedir}/llvm-project-%{commit}.tar.gz %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz

%setup -q -n llvm-project-%{commit}/%{name}


# HACK so that lldb can find its custom readline.so, because we move it
# after install.
sed -i -e "s~import sys~import sys\nsys.path.insert\(1, '%{python2_sitearch}/lldb'\)~g" source/Interpreter/embedded_interpreter.py

%build

mkdir -p _build
cd _build

# Python version detection is broken

LDFLAGS="%{__global_ldflags} -lpthread -ldl"

CFLAGS="%{optflags} -Wno-error=format-security"
CXXFLAGS="%{optflags} -Wno-error=format-security"

%cmake  -B "%{_vpath_builddir}" \
  -GNinja \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_CONFIG:FILEPATH=/usr/bin/llvm-config-%{__isa_bits} \
	\
	-DLLDB_DISABLE_CURSES:BOOL=OFF \
	-DLLDB_DISABLE_LIBEDIT:BOOL=OFF \
	-DLLDB_DISABLE_PYTHON:BOOL=OFF \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64 \
%else
	-DLLVM_LIBDIR_SUFFIX= \
%endif
	\
	-DPYTHON_EXECUTABLE:STRING=%{__python2} \
	-DPYTHON_VERSION_MAJOR:STRING=$(%{__python2} -c "import sys; print(sys.version_info.major)") \
	-DPYTHON_VERSION_MINOR:STRING=$(%{__python2} -c "import sys; print(sys.version_info.minor)") \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_LIT_ARGS="-sv \
	--path %{_libdir}/llvm" \

%ninja_build -C "%{_vpath_builddir}"

%install
%ninja_install -C "%{_vpath_builddir}"

%multilib_fix_c_header --file %{_includedir}/lldb/Host/Config.h

# remove static libraries
rm -fv %{buildroot}%{_libdir}/*.a

# python: fix binary libraries location
liblldb=$(basename $(readlink -e %{buildroot}%{_libdir}/liblldb.so))
ln -vsf "../../../${liblldb}" %{buildroot}%{python2_sitearch}/lldb/_lldb.so
#mv -v %{buildroot}%{python2_sitearch}/readline.so %{buildroot}%{python2_sitearch}/lldb/readline.so
%py_byte_compile %{__python2} %{buildroot}%{python2_sitearch}/lldb

# remove bundled six.py
rm -f %{buildroot}%{python2_sitearch}/six.*

%ldconfig_scriptlets

%files
%{_bindir}/lldb*
%{_libdir}/liblldb.so.*
%{_libdir}/liblldbIntelFeatures.so.*

%files devel
%{_includedir}/lldb
%{_libdir}/*.so

%files -n python2-lldb
%{python2_sitearch}/lldb

%changelog
* Wed Nov 06 2019 Mihai Vultur <xanto@egaming.ro>
- Force downloading of archive source due to bad copr cache.

* Sat Nov 02 2019 Mihai Vultur <xanto@egaming.ro>
- Now that they have migrated to github, change to official source url.

* Sun Oct 06 2019 Mihai Vultur <xanto@egaming.ro>
- Architecture specific builds might run asynchronous.
- This might cause that same package build for x86_64 will be different when
-  built for i686. This is problematic when we want to install multilib packages. 
- Convert the specfile to template and use it to generate the actual script.
- This will prevent the random failues and mismatch between arch versions.

* Sun Jul 14 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.
- Based on spec files from 'GloriousEggroll' and 'che' coprs.
