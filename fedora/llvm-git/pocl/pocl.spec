%global build_branch master
%global proj_name pocl
%global build_repo https://github.com/pocl/pocl

%global maj_ver %(curl -s https://raw.githubusercontent.com/%{proj_name}/%{proj_name}/%{build_branch}/CMakeLists.txt | grep MAJOR_VERSION | head -1 | grep -oP '[0-9]+')
%global min_ver %(curl -s https://raw.githubusercontent.com/%{proj_name}/%{proj_name}/%{build_branch}/CMakeLists.txt | grep MINOR_VERSION | head -1 | grep -oP '[0-9]+')

%define commit %(git ls-remote %{build_repo} | grep -w "refs/heads/%{build_branch}" | awk '{print $1}')
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date %(date +"%Y%m%d.%H")
%global gitrel .%{commit_date}.git%{shortcommit}
%global _default_patch_fuzz 2


%global sover 2
%global with_tests 1

Summary:        Portable Computing Language - an OpenCL implementation
Name:           %{proj_name}
Version:	%{maj_ver}.%{min_ver}
Release:	0.1%{?gitrel}%{?dist}

# The whole code is under MIT
# except include/utlist.h which is under BSD (and unbundled) and
# except lib/kernel/vecmath which is under GPLv3+ or LGPLv3+ (and unbundled in future)
License:        MIT and BSD and (GPLv3+ or LGPLv3+)

URL:            %{build_repo}
Source0:        %url/archive/%{commit}.tar.gz#/%{name}-%{commit}.tar.gz

# FIXME: link
Patch1001:      0001-wrap-more-stuff-for-64-bit-atomics.patch

# ppc64le builds fine, but: 97% tests passed, 4 tests failed out of 120
# ppc64 builds fine, but: 87% tests passed, 16 tests failed out of 120
# s390x builds fine, but: 15% tests passed, 102 tests failed out of 120
ExclusiveArch:  %{arm} aarch64 %{ix86} x86_64

BuildRequires:  cmake
BuildRequires:  clang clang-devel
BuildRequires:  compiler-rt
BuildRequires:  llvm llvm-devel
BuildRequires:  hwloc-devel
BuildRequires:  libtool
BuildRequires:  libtool-ltdl-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  ocl-icd-devel
BuildRequires:  uthash-devel
BuildRequires:  zlib-devel
BuildRequires:  libedit-devel
BuildRequires:  glew-devel
#BuildRequires:  vecmath-devel
# https://bugzilla.redhat.com/show_bug.cgi?id=1082364
Requires:       libstdc++-devel%{?_isa}
# Runtime dependency, because libm.so is required for kernels
Requires:       glibc-devel%{?_isa}

%description
Pocl's goal is to become an efficient open source (MIT-licensed) implementation
of the OpenCL 1.2 (and soon OpenCL 2.0) standard.

In addition to producing an easily portable open-source OpenCL implementation,
another major goal of this project is improving performance portability of
OpenCL programs with compiler optimizations, reducing the need for
target-dependent manual optimizations.

At the core of pocl is the kernel compiler that consists of a set of LLVM
passes used to statically transform kernels into work-group functions with
multiple work-items, even in the presence of work-group barriers. These
functions are suitable for parallelization in multiple ways (SIMD, VLIW,
superscalar,...).

%package devel
Summary:        Portable Computing Language development files
Requires:       %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       ocl-icd-devel%{?_isa}
Requires:       clang%{?_isa}
Requires:       opencl-filesystem
Requires:       uthash-devel

%description devel
Portable Computing Language development files.

%prep
%autosetup -p1 -n %{name}-%{commit}

# Unbundle uthash
find . -depth -name utlist* -print -delete


%build
mkdir %{_target_platform}
pushd %{_target_platform}
# CPU detection fails on ARM, so we need to manually specify the CPU as generic.
%cmake .. \
    -DENABLE_ICD=1 \
    -DPOCL_INSTALL_ICD_VENDORDIR=%{_sysconfdir}/OpenCL/vendors \
    -DEXTRA_KERNEL_CXX_FLAGS="%{optflags} -std=c++11" \
%ifarch %{ix86} x86_64
    -DKERNELLIB_HOST_CPU_VARIANTS=distro \
%endif
%ifarch aarch64 %{arm}
    -DLLC_HOST_CPU="generic" \
%endif
    -DPOCL_ICD_ABSOLUTE_PATH=OFF \
    %{nil}
    # -DENABLE_TESTSUITES=all Requires clBLAS
popd
%make_build -C %{_target_platform}

%install
%make_install -C %{_target_platform}

# Unbundle vecmath
#rm -vf %%{buildroot}/%%{_libdir}/pocl/vecmath/
#ln -vs %%{_includedir}/vecmath %%{buildroot}/%%{_libdir}/pocl/vecmath
# <visit0r> but you need to run the .py to generate the files under the pocl dir

%if 0%{?with_tests}
%check
pushd %{_target_platform}
# https://github.com/pocl/pocl/issues/602
# https://github.com/pocl/pocl/issues/603
  ctest -VV \
  %ifarch %{ix86} %{arm}
    || :
  %else
    ;
  %endif
popd
%endif

%ldconfig_scriptlets

%files
%doc README doc/sphinx/source/*.rst
%{_sysconfdir}/OpenCL/vendors/%{name}.icd
%{_libdir}/lib%{name}.so.%{sover}*
%{_datadir}/%{name}/

%files devel
%{_bindir}/poclcc
%{_libdir}/lib%{name}.so
%{_libdir}/%{name}/
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Tue Jul 16 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.

* Tue Feb 19 2019 sguelton@redhat.com - 1.2-4
- Rebuild for llvm 8.0.0rc2, moving to top-of-tree version

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 17 2018 sguelton@redhat.com - 1.2-2
- Rebuilt for llvm 7.0.1

* Tue Nov 27 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.2-1
- Update to 1.2

* Tue Nov 27 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.2~rc1-1
- Use tilde versioning

* Wed Aug 15 2018 Tom Stellard <tstellar@redhat.com> - 1.2-0.2.rc1
- Update to 1.2-rc1

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Mar 26 2018 Peter Robinson <pbrobinson@fedoraproject.org> 1.1-2
- Minor spec updates/cleanups
- Enable aarch64

* Fri Mar 23 2018 Tom Stellard <tstellar@redhat.com> - 1.1-1
- Update to 1.1

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 31 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.0-3
- Switch to %%ldconfig_scriptlets

* Fri Jan 12 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.0-2
- Re-enable arm

* Mon Jan 01 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.0-1
- Update to 1.0

* Tue Oct 24 2017 Tom Stellard <tstellar@redhat.com> - 0.15-0.1.20171023git53ef5e8
- Rebase to latest master branch for LLVM 5.0 support

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.14-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.14-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri May 26 2017 Peter Robinson <pbrobinson@fedoraproject.org> 0.14-2
- Add upstream patch to fix ARM arch detection

* Wed Apr 12 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.14-1
- Update to 0.14

* Tue Mar 28 2017 Tom Stellard <tstellar@redhat.com> - 0.14-0.6.gitd56ab93
- Rebase to latest release_0_14 branch

* Fri Mar 10 2017 Tom Stellard <tstellar@redhat.com> - 0.14-0.5.gite05a24b
- Rebase to latest release_0_14 branch

* Fri Mar 03 2017 Dave Airlie <airlied@redhat.com> - 0.14-0.4.gite4f7002
- rebase to latest pocl master

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.14-0.3.git3fef5b5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Nov 24 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.14-0.2.git3fef5b5
- Update to latest git
- Move /usr/share into main package

* Fri Oct 28 2016 Dave Airlie <airlied@redhat.com> - 0.14-0.1
- pocl 0.14-pre, just use a pocl snapshot for now

* Thu Oct 27 2016 Dave Airlie <airlied@redhat.com> - 0.13-8
- Rebuild + backport for llvm 3.9

* Wed Aug 31 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.13-7
- Couple of fixes

* Wed Aug 31 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.13-6
- Rebuild for OpenCL 2.1

* Sun Aug 14 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.13-5
- Remove virtual provides for opencl-icd

* Fri Apr 08 2016 Björn Esser <fedora@besser82.io> - 0.13-4
- add virtual Provides for ocl-icd (RHBZ #1317605)

* Fri Apr 08 2016 Björn Esser <fedora@besser82.io> - 0.13-3
- changes as suggested in rhbz #1324438
- enable builds for %%{arm}
- fix spelling error in devel-pkg %%description and %%summary
- fix rpmlint warnings for spec-file and srpm

* Tue Apr 05 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.13-2
- use -DKERNELLIB_HOST_CPU_VARIANTS=distro
- add --output-on-failure for ctest invocation

* Tue Apr 05 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.13-1
- Update to 0.13 (RHBZ #1323866)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 27 2016 Adam Jackson <ajax@redhat.com> 0.12-2
- Rebuild for llvm 3.7.1 library split

* Thu Nov 05 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.12-1
- 0.12 release

* Tue Oct 06 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.12-0.1.git20151006.eb665eb
- Todays snapshot (eb665eb)

* Thu Sep 17 2015 Dave Airlie <airlied@redhat.com> 0.11-3
- snapshot pocl master - for llvm 3.7 support

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Apr 13 2015 Björn Esser <bjoern.esser@gmail.com> - 0.11-1
- temporarily ignore testsuite fails on fc >= 23

* Fri Apr 10 2015 Björn Esser <bjoern.esser@gmail.com> - 0.11-1
- pocl 0.11
- adds support for LLVM >= 3.5

* Fri Apr 10 2015 Björn Esser <bjoern.esser@gmail.com> - 0.10-3
- rebuild for libLLVM-3.6.so

* Tue Oct 28 2014 Adam Jackson <ajax@redhat.com> 0.10-2
- BuildRequires: libedit-devel
- Rebuild for llvm 3.5

* Tue Oct 14 2014 Adam Jackson <ajax@redhat.com> 0.10-1
- pocl 0.10

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 22 2014 Björn Esser <bjoern.esser@gmail.com> - 0.9-5
- require uthash-devel instead of uthash
- small cleanups

* Mon Apr 07 2014 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9.4
- Provide isas for correct requires rhbz#1082364

* Mon Mar 31 2014 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-3
- Add glibc-devel requirement

* Fri Jan 31 2014 Rex Dieter <rdieter@fedoraproject.org> 0.9-2
- rebuild (llvm 3.4 again)

* Wed Jan 29 2014 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-1
- Update to 0.9

* Fri Jan 17 2014 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-0.9.rc2
- Update to 0.9RC2

* Wed Jan 15 2014 Dave Airlie <airlied@redhat.com> 0.9-0.8.git20131209.9374f32
- bump for rebuild against llvm 3.4

* Mon Dec 09 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-0.7.git20131209.9374f32
- Enable LLVM API mode

* Mon Dec 09 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-0.6.git20131209.7fc5dd0
- Update to a working snapshot
- Drop utlist.h from Makefile
- Set LLC_HOST_CPU to workaround incorrect CPU detection/missing LLVM support

* Mon Nov 11 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-0.5.git20131111.8a26561
- Fix Requirement

* Mon Nov 11 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-0.4.git20131111.8a26561
- Add BR on gcc-c++ temporarily
- Update to a newer snapshot

* Mon Oct 07 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-0.3.git20131007.94d0cce
- Update to 94d0cce4b368bdc963e97952ccf88e55e6a8b4ba
- Includes implementations for clSetEventCallback

* Wed Oct 02 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.9-0.2.git20130925.b190740
- Update package summary to include OpenCL

* Tue Oct 01 2013 Björn Esser <bjoern.esser@gmail.com> - 0.9-0.1.git20130925.b190740
- update to recent git-snapshot
- minor cleanup
- include some more documentation

* Sun Sep 29 2013 Dan Horák <dan[at]danny.cz> - 0.8-8
- switch to ExclusiveArch as it needs explicit porting to new arches

* Wed Aug 28 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.8-7
- Add requirements on opencl-filesystem and uthash
- Remove uthash sources during prep
- Fix license field

* Mon Aug 19 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.8-6
- Move includedir to base package. This is required to build
  kernels at runtime.

* Thu Aug 15 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.8-5
- Unbundle uthash
- Updated licenses

* Wed Aug 14 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.8-4
- Drop -libs subpackage
- Fix -devel BR on base package

* Wed Aug 14 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.8-3
- Add check
- Enforce ICD usage
- Fix duplicate file warnings

* Tue Aug 13 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.8-2
- Own some dirs
- Fix -devel libraries
- Add hwloc, llvm, mesa-libGL BR
- Glob for bc and type files
- ExcludeArch armv7hl

* Mon Aug 12 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.8-1
- Update to 0.8
- Better description
- Fix SourceUrl

* Sun Aug 11 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.8pre-0.2
- Updated bzr snapshot

* Wed Feb 27 2013 Dave Airlie <airlied@redhat.com> - 0.8pre-0.1
- first import

