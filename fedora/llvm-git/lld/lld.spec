%global build_branch master

%global build_repo https://github.com/llvm-mirror/%{name}

%global maj_ver %(curl -s https://raw.githubusercontent.com/llvm/llvm-project/%{build_branch}/llvm/CMakeLists.txt | grep LLVM_VERSION_MAJOR | grep -oP '[0-9]+')
%global min_ver %(curl -s https://raw.githubusercontent.com/llvm/llvm-project/%{build_branch}/llvm/CMakeLists.txt | grep LLVM_VERSION_MINOR | grep -oP '[0-9]+')
%global patch_ver %(curl -s https://raw.githubusercontent.com/llvm/llvm-project/%{build_branch}/llvm/CMakeLists.txt | grep LLVM_VERSION_PATCH | grep -oP '[0-9]+')

%define commit %(git ls-remote %{build_repo} | grep -w "refs/heads/%{build_branch}" | awk '{print $1}')

%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date %(date +"%Y%m%d.%H")
%global gitrel .%{commit_date}.git%{shortcommit}

%global pkg_name lld

Name:		%{pkg_name}
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	0.1%{?gitrel}%{?dist}
Summary:	The LLVM Linker

License:	NCSA
URL:		https://github.com/llvm-mirror/
Source0:	%url/%{name}/archive/%{commit}.tar.gz#/%{name}-%{commit}.tar.gz

Patch0:		0001-CMake-Check-for-gtest-headers-even-if-lit.py-is-not-.patch
Patch1:		0001-lld-Prefer-using-the-newest-installed-python-version.patch
#Patch2:		0001-Partial-support-of-SHT_GROUP-without-flag.patch

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	llvm-devel = %{version}
BuildRequires:  llvm-static = %{version}
BuildRequires:  llvm-test = %{version}
BuildRequires:	ncurses-devel
BuildRequires:	zlib-devel
BuildRequires:	chrpath

# For make check:
BuildRequires:	python3-rpm-macros
BuildRequires:	python3-lit
BuildRequires:	llvm-googletest

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
%autosetup -n %{name}-%{commit}

%build

mkdir %{_target_platform}
cd %{_target_platform}

%cmake .. \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_DYLIB_COMPONENTS="all" \
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

%make_build

%install
cd %{_target_platform}
%make_install

# Remove rpath
chrpath --delete %{buildroot}%{_bindir}/*
chrpath --delete %{buildroot}%{_libdir}/*.so*

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
* Sun Jul 14 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.
