%global pkg_name compiler-rt


%global build_repo https://github.com/llvm/llvm-project

%global maj_ver 14
%global min_ver 0
%global patch_ver 0

%define commit d5166f86a33d718437a1f1d75a9d0efbe5f36e1f
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20210907

%global gitrel .%{commit_date}.git%{shortcommit}
%define _unpackaged_files_terminate_build 0
%global _default_patch_fuzz 2


%ifarch s390 s390x
# only limited set of libs available on s390(x) and the existing ones (stats, ubsan) don't provide debuginfo
%global debug_package %{nil}
%endif

%global crt_srcdir llvm-project-%{commit}/compiler-rt

Name:		%{pkg_name}
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	0.1%{?gitrel}%{?dist}
Summary:	LLVM "compiler-rt" runtime libraries

License:	NCSA or MIT
URL:      https://llvm.org
Source0:  %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz

Patch0:		0001-PATCH-std-thread-copy.patch

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:  ninja-build
BuildRequires:	python3
# We need python3-devel for pathfix.py.
BuildRequires:	python3-devel
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-static = %{version}
BuildRequires:	llvm-test = %{version}

%description
The compiler-rt project is a part of the LLVM project. It provides
implementation of the low-level target-specific hooks required by
code generation, sanitizer runtimes and profiling library for code
instrumentation, and Blocks C language extension.

%prep
%autosetup -n %{crt_srcdir} -p1

pathfix.py -i "%{__python3} %{py3_shbang_opts}" -p -n .
pathfix.py -i "%{__python3} %{py3_shbang_opts}" -p -n \
  lib/hwasan/scripts/hwasan_symbolize

%build
%cmake  -B "%{_vpath_builddir}" \
  -GNinja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DLLVM_CONFIG_PATH:FILEPATH=%{_bindir}/llvm-config-%{__isa_bits} \
  \
%if 0%{?__isa_bits} == 64
  -DLLVM_LIBDIR_SUFFIX=64 \
%else
  -DLLVM_LIBDIR_SUFFIX= \
%endif
  -DCOMPILER_RT_INCLUDE_TESTS:BOOL=OFF # could be on?

%ninja_build -C "%{_vpath_builddir}"

%install

%ninja_install -C "%{_vpath_builddir}"

# move blacklist/abilist files to where clang expect them
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/share
mv -v %{buildroot}%{_datadir}/*list.txt  %{buildroot}%{_libdir}/clang/%{version}/share/

# move sanitizer libs to better place
%global libclang_rt_installdir lib/linux
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib
mv -v %{buildroot}%{_prefix}/%{libclang_rt_installdir}/*clang_rt* %{buildroot}%{_libdir}/clang/%{version}/lib
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib/linux/
pushd %{buildroot}%{_libdir}/clang/%{version}/lib
for i in *.a *.so
do
  ln -s ../$i linux/$i
done

# multilib support: also create symlink from lib to lib64, fixes rhbz#1678240
# the symlinks will be dangling if the 32 bits version is not installed, but that should be fine
%ifarch x86_64

mkdir -p %{buildroot}/%{_exec_prefix}/lib/clang/%{version}/lib/linux
for i in *.a *.so
do
  target=`echo "$i" | sed -e 's/x86_64/i386/'`
  ln -s ../../../../../lib/clang/%{version}/lib/$target ../../../../%{_lib}/clang/%{version}/lib/linux/
done
 
%endif
 
popd

%check
#make check-all -C _build

%files
%license LICENSE.TXT
%{_includedir}/*
%{_libdir}/clang/%{version}

%changelog
* Mon Jul 20 2020 sguelton@redhat.com
- Use modern cmake macros

* Sat Jan 18 2020 Mihai Vultur <xanto@egaming.ro>
- Fix ambigous python shebang.

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

* Wed Mar 20 2019 sguelton@redhat.com - 8.0.0-1
- 8.0.0 final

* Tue Mar 12 2019 sguelton@redhat.com - 8.0.0-0.4.rc4
- 8.0.0 Release candidate 4

* Mon Mar 4 2019 sguelton@redhat.com - 8.0.0-0.3.rc3
- 8.0.0 Release candidate 3

* Fri Feb 22 2019 sguelton@redhat.com - 8.0.0-0.2.rc2
- 8.0.0 Release candidate 2

* Mon Feb 11 2019 sguelton@redhat.com - 8.0.0-0.1.rc1
- 8.0.0 Release candidate 1

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 7.0.1-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jan 18 2019 sguelton@redhat.com - 7.0.1-2
- GCC-9 compatibility

* Mon Dec 17 2018 sguelton@redhat.com - 7.0.1-1
- 7.0.1 Release

* Tue Dec 04 2018 sguelton@redhat.com - 7.0.0-2
- Ensure rpmlint passes on specfile

* Mon Sep 24 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-1
- 7.0.0-1 Release

* Wed Sep 12 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.4.rc3
- 7.0.0-rc3 Release

* Fri Sep 07 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.3.rc1
- Use python3 for build scripts

* Thu Sep 06 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.2.rc1
- Drop BuildRequires: python2

* Tue Aug 14 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.1.rc1
- 7.0.0-rc1 Release

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jun 28 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-1
- 6.0.1 Release

* Mon Mar 19 2018 Iryna Shcherbina <ishcherb@redhat.com> - 6.0.0-2
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Mar 08 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-1
- 6.0.0 Release

* Tue Feb 13 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.4.rc2
- 6.0.0-rc2 Release

* Tue Feb 13 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.3.rc1
- Fix build on AArch64

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.0-0.2.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 25 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.1.rc1
- 6.0.0-rc1 Release

* Wed Jan 17 2018 Tom Stellard <tstellar@redhat.com> - 5.0.1-2
- Build libFuzzer with gcc

* Wed Dec 20 2017 Tom Stellard <tstellar@redhat.com> - 5.0.1-1
- 5.0.1 Release

* Fri Oct 13 2017 Tom Stellard <tstellar@redhat.com> - 5.0.0-1
- 5.0.0 Release

* Mon Sep 25 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-6
- Fix AArch64 build with glibc 2.26

* Tue Sep 12 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-5
- Package libFuzzer

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jun 23 2017 Tom Stellard <tstelar@redhat.com> - 4.0.1-2
- Fix build with newer glibc

* Fri Jun 23 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-1
- 4.0.1 Release

* Tue Mar 14 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-1
- compiler-rt 4.0.0 Final Release

* Thu Mar 02 2017 Dave Airlie <airlied@redhat.com> - 3.9.1-1
- compiler-rt 3.9.1

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 21 2016 Dan Horak <dan[at]danny.cz> - 3.9.0-3
- disable debuginfo on s390(x)

* Wed Nov 02 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-2
- build for new arches.

* Wed Oct 26 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-1
- compiler-rt 3.9.0 final release

* Mon May  2 2016 Tom Callaway <spot@fedoraproject.org> 3.8.0-2
- make symlinks to where the linker thinks these libs are

* Thu Mar 10 2016 Dave Airlie <airlied@redhat.com> 3.8.0-1
- compiler-rt 3.8.0 final release

* Thu Mar 03 2016 Dave Airlie <airlied@redhat.com> 3.8.0-0.2
- compiler-rt 3.8.0rc3

* Thu Feb 18 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.1
- compiler-rt 3.8.0rc2

* Fri Feb 05 2016 Dave Airlie <airlied@redhat.com> 3.7.1-3
- fix compiler-rt paths - from rwindz0@gmail.com - #1304605

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Oct 06 2015 Jan Vcelak <jvcelak@fedoraproject.org> 3.7.0-100
- initial version using cmake build system
