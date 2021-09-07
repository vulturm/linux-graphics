%global build_repo https://github.com/llvm/llvm-project

%global maj_ver 14
%global min_ver 0
%global patch_ver 0

%define commit d5166f86a33d718437a1f1d75a9d0efbe5f36e1f
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20210907
%global gitrel .%{commit_date}.git%{shortcommit}
%global _default_patch_fuzz 2

# Components enabled if supported by target architecture:
%define gold_arches %{ix86} x86_64 %{arm} aarch64 %{power64} s390x
%ifarch %{gold_arches}
  %bcond_without gold
%else
  %bcond_with gold
%endif

%bcond_with compat_build

%global llvm_libdir %{_libdir}/%{name}
%global build_llvm_libdir %{buildroot}%{llvm_libdir}
%global llvm_srcdir llvm-project-%{commit}/llvm

%if %{with compat_build}
%global pkg_name llvm%{maj_ver}.%{min_ver}
%global exec_suffix -%{maj_ver}.%{min_ver}
%global install_prefix %{_libdir}/%{name}
%global install_bindir %{install_prefix}/bin
%global install_includedir %{install_prefix}/include
%global install_libdir %{install_prefix}/lib

%global pkg_bindir %{install_bindir}
%global pkg_includedir %{_includedir}/%{name}
%global pkg_libdir %{install_libdir}
%else
%global pkg_name llvm
%global install_prefix /usr
%global install_libdir %{_libdir}
%global pkg_libdir %{install_libdir}
%endif

%global build_install_prefix %{buildroot}%{install_prefix}

Name:     %{pkg_name}
Version:  %{maj_ver}.%{min_ver}.%{patch_ver}
Release:  0.1%{?gitrel}%{?dist}
Summary:  The Low Level Virtual Machine

License:  NCSA
URL:      https://llvm.org
Source0:  %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz
%if %{without compat_build}
Source3:  run-lit-tests
Source4:  lit.fedora.cfg.py
%endif

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  zlib-devel
BuildRequires:  libffi-devel
BuildRequires:  ncurses-devel
BuildRequires:  python3-sphinx
BuildRequires:  python3-recommonmark
BuildRequires:  multilib-rpm-config
%if %{with gold}
BuildRequires:  binutils-devel
%endif
%ifarch %{valgrind_arches}
# Enable extra functionality when run the LLVM JIT under valgrind.
BuildRequires:  valgrind-devel
%endif
# LLVM's LineEditor library will use libedit if it is available.
BuildRequires:  libedit-devel
# We need python3-devel for pathfix.py.
BuildRequires:  python3-devel

# For origin certification
BuildRequires:  gnupg2


Requires: %{name}-libs%{?_isa} = %{version}-%{release}

Provides: llvm(major) = %{maj_ver}

%description
LLVM is a compiler infrastructure designed for compile-time, link-time,
runtime, and idle-time optimization of programs from arbitrary programming
languages. The compiler infrastructure includes mirror sets of programming
tools as well as libraries with equivalent functionality.

%package devel
Summary:  Libraries and header files for LLVM
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
# The installed LLVM cmake files will add -ledit to the linker flags for any
# app that requires the libLLVMLineEditor, so we need to make sure
# libedit-devel is available.
Requires: libedit-devel
# The installed cmake files reference binaries from llvm-test and llvm-static.
# We tried in the past to split the cmake exports for these binaries out into
# separate files, so that llvm-devel would not need to Require these packages,
# but this caused bugs (rhbz#1773678) and forced us to carry two non-upstream
# patches.
Requires: llvm-static%{?_isa} = %{version}-%{release}
Requires: llvm-test%{?_isa} = %{version}-%{release}


Requires(post): %{_sbindir}/alternatives
Requires(postun): %{_sbindir}/alternatives

Provides: llvm-devel(major) = %{maj_ver}

%description devel
This package contains library and header files needed to develop new native
programs that use the LLVM infrastructure.

%package doc
Summary:  Documentation for LLVM
BuildArch:  noarch
Requires: %{name} = %{version}-%{release}

%description doc
Documentation for the LLVM compiler infrastructure.

%package libs
Summary:  LLVM shared libraries

%description libs
Shared libraries for the LLVM compiler infrastructure.

%package static
Summary:  LLVM static libraries
Conflicts:  %{name}-devel < 8

%description static
Static libraries for the LLVM compiler infrastructure.

%if %{without compat_build}

%package test
Summary:  LLVM regression tests
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: python3-lit
# The regression tests need gold.
Requires: binutils
# This is for llvm-config
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
# Bugpoint tests require gcc
Requires: gcc
Requires: findutils

Provides: llvm-test(major) = %{maj_ver}

%description test
LLVM regression tests.

%package googletest
Summary: LLVM's modified googletest sources

%description googletest
LLVM's modified googletest sources.

%endif

%prep
%autosetup -n %{llvm_srcdir} -p1

pathfix.py -i %{__python3} -pn \
  test/BugPoint/compile-custom.ll.py \
  tools/opt-viewer/*.py \
  utils/update_cc_test_checks.py

%build

# Disable LTO on s390x, this causes some test failures:
# LLVM-Unit :: Target/AArch64/./AArch64Tests/InstSizes.Authenticated
# LLVM-Unit :: Target/AArch64/./AArch64Tests/InstSizes.PATCHPOINT
# LLVM-Unit :: Target/AArch64/./AArch64Tests/InstSizes.STACKMAP
# LLVM-Unit :: Target/AArch64/./AArch64Tests/InstSizes.TLSDESC_CALLSEQ
# On X86_64, LTO builds of TableGen crash.  This can be reproduced by:
# %%cmake_build --target include/llvm/IR/IntrinsicsAArch64.h
# Because of these failures, lto is disabled for now.
%global _lto_cflags %{nil}

%ifarch s390 %{arm} %ix86
# Decrease debuginfo verbosity to reduce memory consumption during final library linking
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

# force off shared libs as cmake macros turns it on.
%cmake -B "%{_vpath_builddir}" \
  -G Ninja \
  -DBUILD_SHARED_LIBS:BOOL=OFF \
  -DLLVM_PARALLEL_LINK_JOBS=1 \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_SKIP_RPATH:BOOL=ON \
%ifarch s390 %{arm} %ix86
  -DCMAKE_C_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
  -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
%endif
%if %{without compat_build}
%if 0%{?__isa_bits} == 64
  -DLLVM_LIBDIR_SUFFIX=64 \
%else
  -DLLVM_LIBDIR_SUFFIX= \
%endif
%endif
  \
  -DLLVM_TARGETS_TO_BUILD=all \
  -DLLVM_ENABLE_LIBCXX:BOOL=OFF \
  -DLLVM_ENABLE_ZLIB:BOOL=ON \
  -DLLVM_ENABLE_FFI:BOOL=ON \
  -DLLVM_ENABLE_RTTI:BOOL=ON \
%if %{with gold}
  -DLLVM_BINUTILS_INCDIR=%{_includedir} \
%endif
  -DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD=AVR \
  \
  -DLLVM_BUILD_RUNTIME:BOOL=ON \
  \
  -DLLVM_INCLUDE_TOOLS:BOOL=ON \
  -DLLVM_BUILD_TOOLS:BOOL=ON \
  \
  -DLLVM_INCLUDE_TESTS:BOOL=ON \
  -DLLVM_BUILD_TESTS:BOOL=ON \
  \
  -DLLVM_INCLUDE_EXAMPLES:BOOL=ON \
  -DLLVM_BUILD_EXAMPLES:BOOL=OFF \
  \
  -DLLVM_INCLUDE_UTILS:BOOL=ON \
%if %{with compat_build}
  -DLLVM_INSTALL_UTILS:BOOL=OFF \
%else
  -DLLVM_INSTALL_UTILS:BOOL=ON \
  -DLLVM_UTILS_INSTALL_DIR:PATH=%{_bindir} \
  -DLLVM_TOOLS_INSTALL_DIR:PATH=bin \
%endif
  \
  -DLLVM_INCLUDE_DOCS:BOOL=ON \
  -DLLVM_BUILD_DOCS:BOOL=ON \
  -DLLVM_ENABLE_SPHINX:BOOL=ON \
  -DLLVM_ENABLE_DOXYGEN:BOOL=OFF \
  \
%if %{without compat_build}
  -DLLVM_VERSION_SUFFIX='' \
%endif
  -DLLVM_BUILD_LLVM_DYLIB:BOOL=ON \
  -DLLVM_DYLIB_EXPORT_ALL:BOOL=ON \
  -DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
  -DLLVM_BUILD_EXTERNAL_COMPILER_RT:BOOL=ON \
  -DLLVM_INSTALL_TOOLCHAIN_ONLY:BOOL=OFF \
  \
  -DSPHINX_WARNINGS_AS_ERRORS=OFF \
  -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
  -DLLVM_INSTALL_SPHINX_HTML_DIR=%{_pkgdocdir}/html \
  -DSPHINX_EXECUTABLE=%{_bindir}/sphinx-build-3

# Build libLLVM.so first.  This ensures that when libLLVM.so is linking, there
# are no other compile jobs running.  This will help reduce OOM errors on the
# builders without having to artificially limit the number of concurrent jobs.
%ninja_build -C "%{_vpath_builddir}" LLVM
%ninja_build -C "%{_vpath_builddir}"


%install
%ninja_install -C "%{_vpath_builddir}"

%if %{without compat_build}
mkdir -p %{buildroot}/%{_bindir}
mv %{buildroot}/%{_bindir}/llvm-config %{buildroot}/%{_bindir}/llvm-config-%{__isa_bits}

# ghost presence
touch %{buildroot}%{_bindir}/llvm-config

# Fix some man pages
ln -s llvm-config.1 %{buildroot}%{_mandir}/man1/llvm-config-%{__isa_bits}.1

# Install binaries needed for lit tests
%global test_binaries llvm-isel-fuzzer llvm-opt-fuzzer

for f in %{test_binaries}
do
    install -m 0755 %{_vpath_builddir}/bin/$f %{buildroot}%{_bindir}
done

# Remove testing of update utility tools
rm -rf test/tools/UpdateTestChecks

%multilib_fix_c_header --file %{_includedir}/llvm/Config/llvm-config.h

# Install libraries needed for unittests
%if 0%{?__isa_bits} == 64
%global build_libdir %{_vpath_builddir}/lib64
%else
%global build_libdir %{_vpath_builddir}/lib
%endif

install %{build_libdir}/libLLVMTestingSupport.a %{buildroot}%{_libdir}

%global install_srcdir %{buildroot}%{_datadir}/llvm/src
%global lit_cfg test/%{_arch}.site.cfg.py
%global lit_unit_cfg test/Unit/%{_arch}.site.cfg.py
%global lit_fedora_cfg %{_datadir}/llvm/lit.fedora.cfg.py

# Install gtest sources so clang can use them for gtest
install -d %{install_srcdir}
install -d %{install_srcdir}/utils/
cp -R utils/unittest %{install_srcdir}/utils/

# Clang needs these for running lit tests.
cp utils/update_cc_test_checks.py %{install_srcdir}/utils/
cp -R utils/UpdateTestChecks %{install_srcdir}/utils/

# One of the lit tests references this file
install -d %{install_srcdir}/docs/CommandGuide/
install -m 0644 docs/CommandGuide/dsymutil.rst %{install_srcdir}/docs/CommandGuide/

# Generate lit config files.  Strip off the last lines that initiates the
# test run, so we can customize the configuration.
head -n -2 %{_vpath_builddir}/test/lit.site.cfg.py >> %{lit_cfg}
head -n -2 %{_vpath_builddir}/test/Unit/lit.site.cfg.py >> %{lit_unit_cfg}

# Install custom fedora config file
cp %{SOURCE4} %{buildroot}%{lit_fedora_cfg}

# Patch lit config files to load custom fedora config:
for f in %{lit_cfg} %{lit_unit_cfg}; do
  echo "lit_config.load_config(config, '%{lit_fedora_cfg}')" >> $f
done

install -d %{buildroot}%{_libexecdir}/tests/llvm
install -m 0755 %{SOURCE3} %{buildroot}%{_libexecdir}/tests/llvm

# Install lit tests.  We need to put these in a tarball otherwise rpm will complain
# about some of the test inputs having the wrong object file format.
install -d %{buildroot}%{_datadir}/llvm/

# The various tar options are there to make sur the archive is the same on 32 and 64 bit arch, i.e.
# the archive creation is reproducible. Move arch-specific content out of the tarball
mv %{lit_cfg} %{install_srcdir}/%{_arch}.site.cfg.py
mv %{lit_unit_cfg} %{install_srcdir}/%{_arch}.Unit.site.cfg.py
tar --sort=name --mtime='UTC 2020-01-01' -c test/ | gzip -n > %{install_srcdir}/test.tar.gz

# Install the unit test binaries
mkdir -p %{build_llvm_libdir}
cp -R %{_vpath_builddir}/unittests %{build_llvm_libdir}/
rm -rf `find %{build_llvm_libdir} -iname 'cmake*'`

# Install libraries used for testing
install -m 0755 %{build_libdir}/BugpointPasses.so %{buildroot}%{_libdir}
install -m 0755 %{build_libdir}/LLVMHello.so %{buildroot}%{_libdir}

# Install test inputs for PDB tests
echo "%{_datadir}/llvm/src/unittests/DebugInfo/PDB" > %{build_llvm_libdir}/unittests/DebugInfo/PDB/llvm.srcdir.txt
mkdir -p %{buildroot}%{_datadir}/llvm/src/unittests/DebugInfo/PDB/
cp -R unittests/DebugInfo/PDB/Inputs %{buildroot}%{_datadir}/llvm/src/unittests/DebugInfo/PDB/

%if %{with gold}
# Add symlink to lto plugin in the binutils plugin directory.
%{__mkdir_p} %{buildroot}%{_libdir}/bfd-plugins/
ln -s %{_libdir}/LLVMgold.so %{buildroot}%{_libdir}/bfd-plugins/
%endif

%else

# Add version suffix to binaries
mkdir -p %{buildroot}/%{_bindir}
for f in %{buildroot}/%{install_bindir}/*; do
  filename=`basename $f`
  ln -s ../../../%{install_bindir}/$filename %{buildroot}/%{_bindir}/$filename%{exec_suffix}
done

# Move header files
mkdir -p %{buildroot}/%{pkg_includedir}
ln -s ../../../%{install_includedir}/llvm %{buildroot}/%{pkg_includedir}/llvm
ln -s ../../../%{install_includedir}/llvm-c %{buildroot}/%{pkg_includedir}/llvm-c

# Fix multi-lib
mv %{buildroot}%{_bindir}/llvm-config{%{exec_suffix},%{exec_suffix}-%{__isa_bits}}
%multilib_fix_c_header --file %{install_includedir}/llvm/Config/llvm-config.h

# Create ld.so.conf.d entry
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
cat >> %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf << EOF
%{pkg_libdir}
EOF

# Add version suffix to man pages and move them to mandir.
mkdir -p %{buildroot}/%{_mandir}/man1
for f in %{build_install_prefix}/share/man/man1/*; do
  filename=`basename $f | cut -f 1 -d '.'`
  mv $f %{buildroot}%{_mandir}/man1/$filename%{exec_suffix}.1
done

# Remove opt-viewer, since this is just a compatibility package.
rm -Rf %{build_install_prefix}/share/opt-viewer

%endif


%check
# TODO: Fix test failures on arm
# FIXME: use %%cmake_build instead of %%__ninja
#LD_LIBRARY_PATH=%{buildroot}/%{_libdir}  %{__ninja} check-all -C %{_vpath_builddir} || \
#%ifarch %{arm}
#  :
#%else
#  false
#%endif

%ldconfig_scriptlets libs

%if %{without compat_build}

%post devel
%{_sbindir}/update-alternatives --install %{_bindir}/llvm-config llvm-config %{_bindir}/llvm-config-%{__isa_bits} %{__isa_bits}

%postun devel
if [ $1 -eq 0 ]; then
  %{_sbindir}/update-alternatives --remove llvm-config %{_bindir}/llvm-config-%{__isa_bits}
fi

%endif

%files
%license LICENSE.TXT
%exclude %{_mandir}/man1/llvm-config*
%{_mandir}/man1/*
%{_bindir}/*

%if %{without compat_build}
%exclude %{_bindir}/llvm-config
%exclude %{_bindir}/llvm-config-%{__isa_bits}
%exclude %{_bindir}/not
%exclude %{_bindir}/count
%exclude %{_bindir}/yaml-bench
%exclude %{_bindir}/lli-child-target
%exclude %{_bindir}/llvm-isel-fuzzer
%exclude %{_bindir}/llvm-opt-fuzzer
%{_datadir}/opt-viewer
%else
%exclude %{pkg_bindir}/llvm-config
%{pkg_bindir}
%endif

%files libs
%license LICENSE.TXT
%{pkg_libdir}/libLLVM-%{maj_ver}.so
%if %{without compat_build}
%if %{with gold}
%{_libdir}/LLVMgold.so
%{_libdir}/bfd-plugins/LLVMgold.so
%endif
%{_libdir}/libLLVM-%{maj_ver}.%{min_ver}*.so
%{_libdir}/libLTO.so*
%else
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%if %{with gold}
%{_libdir}/%{name}/lib/LLVMgold.so
%endif
%{pkg_libdir}/libLLVM-%{maj_ver}.%{min_ver}*.so
%{pkg_libdir}/libLTO.so*
%exclude %{pkg_libdir}/libLTO.so
%endif
%{pkg_libdir}/libRemarks.so*

%files devel
%license LICENSE.TXT
%if %{without compat_build}
%ghost %{_bindir}/llvm-config
%{_bindir}/llvm-config-%{__isa_bits}
%{_mandir}/man1/llvm-config*
%{_includedir}/llvm
%{_includedir}/llvm-c
%{_libdir}/libLLVM.so
%{_libdir}/cmake/llvm
%else
%{_bindir}/llvm-config%{exec_suffix}-%{__isa_bits}
%{pkg_bindir}/llvm-config
%{_mandir}/man1/llvm-config%{exec_suffix}.1.gz
%{install_includedir}/llvm
%{install_includedir}/llvm-c
%{pkg_includedir}/llvm
%{pkg_includedir}/llvm-c
%{pkg_libdir}/libLTO.so
%{pkg_libdir}/libLLVM.so
%{pkg_libdir}/cmake/llvm
%endif

%files doc
%license LICENSE.TXT
%doc %{_pkgdocdir}/html

%files static
%license LICENSE.TXT
%if %{without compat_build}
%{_libdir}/*.a
%exclude %{_libdir}/libLLVMTestingSupport.a
%else
%{_libdir}/%{name}/lib/*.a
%endif

%if %{without compat_build}

%files test
%license LICENSE.TXT
%{_libexecdir}/tests/llvm/
%{llvm_libdir}/unittests/
%{_datadir}/llvm/src/unittests
%{_datadir}/llvm/src/test.tar.gz
%{_datadir}/llvm/src/%{_arch}.site.cfg.py
%{_datadir}/llvm/src/%{_arch}.Unit.site.cfg.py
%{_datadir}/llvm/lit.fedora.cfg.py
%{_datadir}/llvm/src/docs/CommandGuide/dsymutil.rst
%{_bindir}/not
%{_bindir}/count
%{_bindir}/yaml-bench
%{_bindir}/lli-child-target
%{_bindir}/llvm-isel-fuzzer
%{_bindir}/llvm-opt-fuzzer
%{_libdir}/BugpointPasses.so
%{_libdir}/LLVMHello.so

%files googletest
%license LICENSE.TXT
%{_datadir}/llvm/src/utils
%{_libdir}/libLLVMTestingSupport.a

%endif

%changelog
* Sat Nov 02 2019 Mihai Vultur <xanto@egaming.ro>
- Now that they have migrated to github, change to official source url.

* Sun Oct 06 2019 Mihai Vultur <xanto@egaming.ro>
- Architecture specific builds might run asynchronous.
- This might cause that same package build for x86_64 will be different when
-  built for i686. This is problematic when we want to install multilib packages. 
- Convert the specfile to template and use it to generate the actual script.
- This will prevent the random failues and mismatch between arch versions.

* Fri Sep 27 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-2
- Remove unneeded BuildRequires: libstdc++-static

* Sun Jul 14 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.
- Based on spec files from 'GloriousEggroll' and 'che' coprs.

* Thu Jun 02 2016 Rudolf Kastl <rkastl@redhat.com> 3.9.0-0.1.r
- using a random svn checkout of 3.9
- removed CppBackend
- updated files section
