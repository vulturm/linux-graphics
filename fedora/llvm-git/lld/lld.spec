%global build_branch master
%global pkg_name lld

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
Summary:	The LLVM Linker

License:	NCSA
URL:      https://llvm.org
Source0:  %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz

Patch0:		0001-CMake-Check-for-gtest-headers-even-if-lit.py-is-not-.patch
#Patch1:		0001-lld-Prefer-using-the-newest-installed-python-version.patch
#Patch2:		0001-Partial-support-of-SHT_GROUP-without-flag.patch

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  llvm-devel = %{version}
BuildRequires:  llvm-test = %{version}
BuildRequires:  ncurses-devel
BuildRequires:  zlib-devel

# For make check:
BuildRequires:  python3-rpm-macros
BuildRequires:  python3-lit
BuildRequires:  llvm-googletest = %{version}

Requires(post): %{_sbindir}/update-alternatives
Requires(preun): %{_sbindir}/update-alternatives

Requires: lld-libs = %{version}-%{release}

%description
The LLVM project linker.

%package devel
Summary:	Libraries and header files for LLD

%description devel
This package contains library and header files needed to develop new native
programs that use the LLD infrastructure.

%package libs
Summary:	LLD shared libraries

%description libs
Shared libraries for LLD.

%prep
%autosetup -n llvm-project-%{commit}/%{name}

%build

%cmake -GNinja \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_DYLIB_COMPONENTS="all" \
  -DCMAKE_SKIP_RPATH:BOOL=ON \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DLLVM_INCLUDE_TESTS=ON \
	-DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_LIT_ARGS="-sv \
	--path %{_libdir}/llvm" \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64
%else
	-DLLVM_LIBDIR_SUFFIX=
%endif

%cmake_build

%install
%cmake_install

%check
# armv7lhl tests disabled because of arm issue, see https://koji.fedoraproject.org/koji/taskinfo?taskID=33660162
#%ifnarch %{arm}
#make -C %{_target_platform} %{?_smp_mflags} check-lld
#%endif

%ldconfig_scriptlets libs

%files
%{_bindir}/lld*
%{_bindir}/ld.lld
%{_bindir}/ld64.lld
%{_bindir}/wasm-ld

%files devel
%{_includedir}/lld
%{_libdir}/liblld*.so

%files libs
%{_libdir}/liblld*.so.*

%changelog
* Mon Jul 20 2020 sguelton@redhat.com
- Use generic cmake macros
- Use Ninja as build system
- Remove chrpath dependency

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
