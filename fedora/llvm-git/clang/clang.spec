%global compat_build 0

%global build_repo https://github.com/llvm/llvm-project

%global maj_ver 14
%global min_ver 0
%global patch_ver 0

%define commit d5166f86a33d718437a1f1d75a9d0efbe5f36e1f

%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20210907

%global gitrel .%{commit_date}.git%{shortcommit}
%global _default_patch_fuzz 2


%global clang_tools_binaries \
	%{_bindir}/clangd \
	%{_bindir}/clang-* \
	%{_bindir}/diagtool \
	%{_bindir}/hmaptool \
	%{_bindir}/pp-trace


%global clang_binaries \
	%{_bindir}/clang \
	%{_bindir}/clang+* \
	%{_bindir}/clang-*


%if 0%{?compat_build}
%global pkg_name clang%{maj_ver}.%{min_ver}
# Install clang to same prefix as llvm, so that apps that use llvm-config
# will also be able to find clang libs.
%global install_prefix %{_libdir}/llvm%{maj_ver}.%{min_ver}
%global install_bindir %{install_prefix}/bin
%global install_includedir %{install_prefix}/include
%global install_libdir %{install_prefix}/lib

%global pkg_bindir %{install_bindir}
%global pkg_includedir %{_includedir}/llvm%{maj_ver}.%{min_ver}
%global pkg_libdir %{install_libdir}
%else
%global pkg_name clang
%global install_prefix /usr
%endif

%if 0%{?fedora} || 0%{?rhel} > 7
%bcond_without python3
%else
%bcond_with python3
%endif

%global build_install_prefix %{buildroot}%{install_prefix}

%ifarch ppc64le
# Too many threads on ppc64 systems causes OOM errors.
%global _smp_mflags -j8
%endif

%global clang_srcdir llvm-project-%{commit}/clang
%global clang_tools_srcdir llvm-project-%{commit}/clang-tools-extra

Name:		%pkg_name
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	0.1%{?gitrel}%{?dist}
Summary:	A C language family front-end for LLVM

License:	NCSA
URL:      https://llvm.org
Source0:  %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz


# Patches for clang
Patch0:     0001-PATCH-clang-Reorganize-gtest-integration.patch
Patch1:     0002-PATCH-clang-Make-funwind-tables-the-default-on-all-a.patch
Patch2:     0003-PATCH-clang-Don-t-install-static-libraries.patch
Patch3:     0004-PATCH-clang-Prefer-gcc-toolchains-with-libgcc_s.so-w.patch


BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	ninja-build
%if 0%{?compat_build}
BuildRequires:	llvm%{maj_ver}.%{min_ver}-devel = %{version}
BuildRequires:	llvm%{maj_ver}.%{min_ver}-static = %{version}
%else
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-test = %{version}
# llvm-static is required, because clang-tablegen needs libLLVMTableGen, which
# is not included in libLLVM.so.
BuildRequires:	llvm-static = %{version}
BuildRequires:	llvm-googletest = %{version}
%endif

BuildRequires:	libxml2-devel
BuildRequires:	perl-generators
BuildRequires:	ncurses-devel
# According to https://fedoraproject.org/wiki/Packaging:Emacs a package
# should BuildRequires: emacs if it packages emacs integration files.
BuildRequires:	emacs

# These build dependencies are required for the test suite.
%if %with python3
# The testsuite uses /usr/bin/lit which is part of the python3-lit package.
BuildRequires:	python3-lit
%endif

BuildRequires:	python3-sphinx
BuildRequires:	libatomic

# We need python3-devel for pathfix.py.
BuildRequires:	python3-devel

# Needed for %%multilib_fix_c_header
BuildRequires:	multilib-rpm-config

# scan-build uses these perl modules so they need to be installed in order
# to run the tests.
BuildRequires: perl(Digest::MD5)
BuildRequires: perl(File::Copy)
BuildRequires: perl(File::Find)
BuildRequires: perl(File::Path)
BuildRequires: perl(File::Temp)
BuildRequires: perl(FindBin)
BuildRequires: perl(Hash::Util)
BuildRequires: perl(lib)
BuildRequires: perl(Term::ANSIColor)
BuildRequires: perl(Text::ParseWords)
BuildRequires: perl(Sys::Hostname)

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

# clang requires gcc, clang++ requires libstdc++-devel
# - https://bugzilla.redhat.com/show_bug.cgi?id=1021645
# - https://bugzilla.redhat.com/show_bug.cgi?id=1158594
Requires:	libstdc++-devel
Requires:	gcc-c++

Provides:	clang(major) = %{maj_ver}

Conflicts:  compiler-rt < %{version}
Conflicts:  compiler-rt > %{version}

%description
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

%package libs
Summary: Runtime library for clang
Recommends: compiler-rt%{?_isa} = %{version}
# libomp-devel is required, so clang can find the omp.h header when compiling
# with -fopenmp.
Recommends: libomp-devel%{_isa} = %{version}
Recommends: libomp%{_isa} = %{version}

%description libs
Runtime library for clang.

%package devel
Summary: Development header files for clang
%if !0%{?compat_build}
Requires: %{name}%{?_isa} = %{version}-%{release}
# The clang CMake files reference tools from clang-tools-extra.
Requires: %{name}-tools-extra%{?_isa} = %{version}-%{release}
Requires: %{name}-libs = %{version}-%{release}
%endif

%description devel
Development header files for clang.

%if !0%{?compat_build}
%package analyzer
Summary:	A source code analysis framework
License:	NCSA and MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}

%description analyzer
The Clang Static Analyzer consists of both a source code analysis
framework and a standalone tool that finds bugs in C and Objective-C
programs. The standalone tool is invoked from the command-line, and is
intended to run in tandem with a build of a project or code base.

%package tools-extra
Summary:	Extra tools for clang
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Requires:	emacs-filesystem

%description tools-extra
A set of extra tools built using Clang's tooling API.

# Put git-clang-format in its own package, because it Requires git
# and we don't want to force users to install all those dependenices if they
# just want clang.
%package -n git-clang-format
Summary:	Integration of clang-format for git
Requires: %{name}-tools-extra = %{version}-%{release}
Requires:	git
Requires:	python3

%description -n git-clang-format
clang-format integration for git.

 
%package -n python3-clang
Summary:       Python3 bindings for clang
Requires:      %{name}-libs%{?_isa} = %{version}-%{release}
Requires:      python3
%description -n python3-clang
%{summary}.


%endif


%prep
%if 0%{?compat_build}

%autosetup -D -n %{clang_srcdir} -p1
%else

%setup -D -q -n %{clang_tools_srcdir}

pathfix.py -i %{__python3} -pn \
  clang-tidy/tool/*.py \
  clang-include-fixer/find-all-symbols/tool/run-find-all-symbols.py

%setup -D -T -q -n %{clang_srcdir}
%autopatch -m200 -p2

#%patch4 -p1 -b .gtest
#%patch10 -p1 -b .bitfields
#%patch11 -p1 -b .libcxx-fix
#%patch15 -p2 -b .no-install-static

mv ../clang-tools-extra tools/extra

# %patch20 -p0

pathfix.py -i %{__python3} -pn \
  tools/clang-format/*.py \
  tools/clang-format/git-clang-format \
  utils/hmaptool/hmaptool \
  tools/scan-build-py/libexec/intercept-cc \
  tools/scan-build-py/libexec/intercept-c++ \
  tools/scan-build-py/libexec/analyze-cc \
  tools/scan-build-py/libexec/analyze-c++ \
  tools/scan-view/bin/scan-view \
  tools/scan-build-py/bin/*
%endif

%build

# We run the builders out of memory on armv7 and i686 when LTO is enabled
%ifarch %{arm} i686
%define _lto_cflags %{nil}
%endif

%if 0%{?__isa_bits} == 64
sed -i 's/\@FEDORA_LLVM_LIB_SUFFIX\@/64/g' test/lit.cfg.py
%else
sed -i 's/\@FEDORA_LLVM_LIB_SUFFIX\@//g' test/lit.cfg.py
%endif

%ifarch s390 s390x %{arm} %ix86 ppc64le
# Decrease debuginfo verbosity to reduce memory consumption during final library linking
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

LDFLAGS="%{__global_ldflags} -ldl"
# -DCMAKE_INSTALL_RPATH=";" is a workaround for llvm manually setting the
# rpath of libraries and binaries.  llvm will skip the manual setting
# if CAMKE_INSTALL_RPATH is set to a value, but cmake interprets this value
# as nothing, so it sets the rpath to "" when installing.
%cmake -B "%{_vpath_builddir}" \
  -G Ninja \
  -DLLVM_PARALLEL_LINK_JOBS=1 \
  -DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
  -DCMAKE_BUILD_TYPE=Release \
  -DPYTHON_EXECUTABLE=%{__python3} \
  -DCMAKE_INSTALL_RPATH:BOOL=";" \
%ifarch s390 s390x %{arm} %ix86 ppc64le
  -DCMAKE_C_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
  -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
%endif
%if 0%{?compat_build}
  -DLLVM_CONFIG:FILEPATH=%{_bindir}/llvm-config-%{maj_ver}.%{min_ver}-%{__isa_bits} \
  -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
  -DCLANG_INCLUDE_TESTS:BOOL=OFF \
%else
  -DCLANG_INCLUDE_TESTS:BOOL=OFF \
  -DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
  -DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src \
%if 0%{?__isa_bits} == 64
  -DLLVM_LIBDIR_SUFFIX=64 \
%else
  -DLLVM_LIBDIR_SUFFIX= \
%endif
%endif
  \
%if !0%{compat_build}
  -DLLVM_TABLEGEN_EXE:FILEPATH=%{_bindir}/llvm-tblgen \
%else
  -DLLVM_TABLEGEN_EXE:FILEPATH=%{_bindir}/llvm-tblgen-%{maj_ver}.%{min_ver} \
%endif
  -DCLANG_ENABLE_ARCMT:BOOL=ON \
  -DCLANG_ENABLE_STATIC_ANALYZER:BOOL=ON \
  -DCLANG_INCLUDE_DOCS:BOOL=ON \
  -DCLANG_PLUGIN_SUPPORT:BOOL=ON \
  -DENABLE_LINKER_BUILD_ID:BOOL=ON \
  -DLLVM_ENABLE_EH=ON \
  -DLLVM_ENABLE_RTTI=ON \
  -DLLVM_BUILD_DOCS=ON \
  -DLLVM_ENABLE_SPHINX=ON \
  -DCLANG_LINK_CLANG_DYLIB=ON \
  -DSPHINX_WARNINGS_AS_ERRORS=OFF \
  \
  -DCLANG_BUILD_EXAMPLES:BOOL=OFF \
  -DBUILD_SHARED_LIBS=OFF \
  -DCLANG_REPOSITORY_STRING="%{?fedora:Fedora}%{?rhel:Red Hat} %{version}-%{release}"

%ninja_build -C "%{_vpath_builddir}"

%install
%ninja_install -C "%{_vpath_builddir}"

%if 0%{?compat_build}

# Remove binaries/other files
rm -Rf %{buildroot}%{install_bindir}
rm -Rf %{buildroot}%{install_prefix}/share
rm -Rf %{buildroot}%{install_prefix}/libexec

# Move include files
mkdir -p %{buildroot}%{pkg_includedir}
mv  %{buildroot}/%{install_includedir}/clang %{buildroot}/%{pkg_includedir}/
mv  %{buildroot}/%{install_includedir}/clang-c %{buildroot}/%{pkg_includedir}/

%else

# install clang python bindings
mkdir -p %{buildroot}%{python3_sitelib}/clang/
install -p -m644 bindings/python/clang/* %{buildroot}%{python3_sitelib}/clang/
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}/clang

# multilib fix
%multilib_fix_c_header --file %{_includedir}/clang/Config/config.h

# Move emacs integration files to the correct directory
mkdir -p %{buildroot}%{_emacs_sitestartdir}
for f in clang-format.el clang-rename.el clang-include-fixer.el; do
mv %{buildroot}{%{_datadir}/clang,%{_emacs_sitestartdir}}/$f
done

# remove editor integrations (bbedit, sublime, emacs, vim)
rm -vf %{buildroot}%{_datadir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{_datadir}/clang/clang-format-sublime.py*

# TODO: Package html docs
rm -Rvf %{buildroot}%{_pkgdocdir}
rm -Rvf %{buildroot}%{_docdir}/clang/html
rm -Rvf %{buildroot}%{_datadir}/clang/clang-doc-default-stylesheet.css
rm -Rvf %{buildroot}%{_datadir}/clang/index.js

# TODO: What are the Fedora guidelines for packaging bash autocomplete files?
rm -vf %{buildroot}%{_datadir}/clang/bash-autocomplete.sh

# Create Manpage symlinks
ln -s clang.1.gz %{buildroot}%{_mandir}/man1/clang++.1.gz
ln -s clang.1.gz %{buildroot}%{_mandir}/man1/clang-%{maj_ver}.1.gz
ln -s clang.1.gz %{buildroot}%{_mandir}/man1/clang++-%{maj_ver}.1.gz

# Add clang++-{version} sylink
ln -s clang++ %{buildroot}%{_bindir}/clang++-%{maj_ver}


# Fix permission
chmod u-x %{buildroot}%{_mandir}/man1/scan-build.1*

# create a link to clang's resource directory that is "constant" across minor
# version bumps
# this is required for packages like ccls that hardcode the link to clang's
# resource directory to not require rebuilds on minor version bumps
# Fix for bugs like rhbz#1807574
pushd %{buildroot}%{_libdir}/clang/
ln -s %{version} %{maj_ver}
popd

%endif

# Remove clang-tidy headers.  We don't ship the libraries for these.
rm -Rvf %{buildroot}%{_includedir}/clang-tidy/

%check
#%if !0%{?compat_build}
# requires lit.py from LLVM utilities
# FIXME: Fix failing ARM tests
#LD_LIBRARY_PATH=%{buildroot}/%{_libdir} cmake_build --target check-all || \
#%ifarch %{arm}
#:
#%else
#false
#%endif
#
#%endif


%if !0%{?compat_build}
%files
%license LICENSE.TXT
%{clang_binaries}
%{_mandir}/man1/clang.1.gz
%{_mandir}/man1/clang++.1.gz
%{_mandir}/man1/clang-%{maj_ver}.1.gz
%{_mandir}/man1/clang++-%{maj_ver}.1.gz
%endif

%files libs
%if !0%{?compat_build}
%{_libdir}/clang/
%{_libdir}/*.so.*
%else
%{pkg_libdir}/*.so.*
%{pkg_libdir}/clang/%{version}
%endif

%files devel
%if !0%{?compat_build}
%{_libdir}/*.so
%{_includedir}/clang/
%{_includedir}/clang-c/
%{_libdir}/cmake/*
%dir %{_datadir}/clang/
%else
%{pkg_libdir}/*.so
%{pkg_includedir}/clang/
%{pkg_includedir}/clang-c/
%{pkg_libdir}/cmake/
%endif

%if !0%{?compat_build}
%files analyzer
%{_bindir}/scan-view
%{_bindir}/scan-build
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_datadir}/scan-view/
%{_datadir}/scan-build/
%{_mandir}/man1/scan-build.1.*

%files tools-extra
%{clang_tools_binaries}
%{_bindir}/c-index-test
%{_bindir}/find-all-symbols
%{_bindir}/modularize
%{_mandir}/man1/diagtool.1.gz
%{_emacs_sitestartdir}/clang-format.el
%{_emacs_sitestartdir}/clang-rename.el
%{_emacs_sitestartdir}/clang-include-fixer.el
%{_datadir}/clang/clang-format.py*
%{_datadir}/clang/clang-format-diff.py*
%{_datadir}/clang/clang-include-fixer.py*
%{_datadir}/clang/clang-tidy-diff.py*
%{_datadir}/clang/run-clang-tidy.py*
%{_datadir}/clang/run-find-all-symbols.py*
%{_datadir}/clang/clang-rename.py*

%files -n git-clang-format
%{_bindir}/git-clang-format

%files -n python3-clang
%{python3_sitelib}/clang/


%endif
%changelog
* Tue Jul 20 2021 Mihai Vultur <xanto@egaming.ro>
- Update patches from upstream.

* Mon Jul 20 2020 sguelton@redhat.com
- Update cmake macro usage

* Sat Nov 02 2019 Mihai Vultur <xanto@egaming.ro>
- Now that they have migrated to github, change to official source url.

* Sun Oct 06 2019 Mihai Vultur <xanto@egaming.ro>
- Architecture specific builds might run asynchronous.
- This might cause that same package build for x86_64 will be different when     
-  built for i686. This is problematic when we want to install multilib packages.
- Convert the specfile to template and use it to generate the actual script.
- This will prevent the random failues and mismatch between arch versions.

* Wed Jul 10 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.
- Based on spec files from 'GloriousEggroll' and 'che' coprs.
