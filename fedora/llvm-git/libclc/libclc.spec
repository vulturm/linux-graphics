%global build_branch master
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

%global shortname clc

# this stop us generating an empty debuginfo
%global debug_package %{nil}

Name:           libclc
Version:        %{maj_ver}.%{min_ver}.%{patch_ver}
Release:        0.1%{?gitrel}%{?dist}
Summary:        An open source implementation of the OpenCL 1.1 library requirements

License:        BSD
URL:            https://llvm.org
Source0:        %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz
Patch0:         libclc-install.patch

ExclusiveArch:	%{ix86} x86_64 %{arm} aarch64 %{power64} s390x

BuildRequires:  clang-devel
BuildRequires:  libedit-devel
BuildRequires:  llvm-devel >= 3.9
BuildRequires:  python
BuildRequires:  zlib-devel
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  spirv-llvm-translator-tools

%description
libclc is an open source, BSD licensed implementation of the library
requirements of the OpenCL C programming language, as specified by the
OpenCL 1.1 Specification. The following sections of the specification
impose library requirements:

  * 6.1: Supported Data Types
  * 6.2.3: Explicit Conversions
  * 6.2.4.2: Reinterpreting Types Using as_type() and as_typen()
  * 6.9: Preprocessor Directives and Macros
  * 6.11: Built-in Functions
  * 9.3: Double Precision Floating-Point
  * 9.4: 64-bit Atomics
  * 9.5: Writing to 3D image memory objects
  * 9.6: Half Precision Floating-Point

libclc is intended to be used with the Clang compiler's OpenCL frontend.

libclc is designed to be portable and extensible. To this end, it provides
generic implementations of most library requirements, allowing the target
to override the generic implementation at the granularity of individual
functions.

libclc currently only supports the PTX target, but support for more
targets is welcome.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
#force downloading the project, seems that copr dist-cache is poisoned with bogus archive
curl -Lo %{_sourcedir}/llvm-project-%{commit}.tar.gz %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz
%autosetup -p0 -n llvm-project-%{commit}/%{name}

%build
export CFLAGS="%{build_cflags} -D__extern_always_inline=inline"
%set_build_flags
#./configure.py --prefix=%{_prefix} --libexecdir=%{_libdir}/%{shortname}/ --pkgconfigdir=%{_libdir}/pkgconfig/
%cmake  -B "%{_vpath_builddir}" \
  -G Ninja \
  -DCMAKE_INSTALL_INCLUDEDIR:PATH=%{_includedir} \
  -DCMAKE_INSTALL_DATADIR:PATH=%{_libdir}

%ninja_build -C "%{_vpath_builddir}"

%install
%ninja_install -C "%{_vpath_builddir}"

%files
%license LICENSE.TXT
%doc README.TXT CREDITS.TXT
%{_includedir}/%{shortname}

%files devel
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Tue Nov 26 2019 Rudolf Kastl <che666@gmail.com>
- Fix libclc install

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

* Wed Apr 03 2019 Dave Airlie <airlied@redhat.com> - 0.2.0-15.git9f6204e
- Update to latest upstream snapshot (prior to moving to cmake)

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.0-14.git1ecb16d
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Dec 04 2018 Dave Airlie <airlied@redhat.com> - 0.2.0-13.git1ecb16d
- Update to latest libclc snapshot

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.0-12.gitc45b9df
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.2.0-11.gitc45b9df
- Update to latest git snapshot

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.0-10.git1cb3fbf
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Dan Horak <dan[at]danny.cz> - 0.2.0-9.git1cb3fbf
- Drop build workarounds

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.0-8.git1cb3fbf
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 24 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.2.0-7.git1cb3fbf
- Update to latest git snapshot

* Sat Mar 11 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.2.0-6.git520743b
- Update to latest snapshot which supports LLVM 3.9

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.0-5.20160207gitdc330a3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Aug 10 2016 Dan Horak <dan[at]danny.cz> - 0.2.0-4.20160207gitdc330a3
- Build on s390x

* Sun Apr 10 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.2.0-3.20160207gitdc330a3
- Build on ARMv7

* Tue Apr 05 2016 Than Ngo <than@redhat.com> - 0.2.0-2.20160207gitdc330a3
- temporary disable stack-protector on powe64 as workaround due to the bug in llvm
  which causes the build failure on power64

* Sun Feb 07 2016 Fabian Deutsch <fabiand@fedoraproject.org> - 0.2.0-1.20160207gitdc330a3
- Update to latest upstream
- Dorp llvm-static BR

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.1-14.20150918git4346c30
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 21 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.0.1-13.20150918git4346c30
- Spell aarch64 correctly

* Thu Jan 21 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.0.1-12.20150918git4346c30
- Now supported on aarch64/Power64

* Fri Sep 18 2015 Dave Airlie <airlied@redhat.com> 0.0.1-11.20150918git4346c30
- latest snapshot - set build req to llvm 3.7

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.1-10.20140901gite822ae3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jan 08 2015 Adel Gadllah <adel.gadllah@gmail.com> - 0.0.1-9.20140901gite822ae3
- Rebuilt with newer llvm

* Tue Oct 28 2014 Peter Robinson <pbrobinson@fedoraproject.org> - 0.0.1-8.20140901gite822ae3
- Update to a newer snapshot

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.1-7.20140705git61127c5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jul 25 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.0.1-6
- Rebuild now llvm bits are fixed for gcc-4.9
- Minor cleanups

* Sat Jul 05 2014 Fabian Deutsch <fabiand@fedoraproject.org> - 0.0.1-5
- Update to latest snapshot to support AMD Kaveri APUs
- Move bitcode files to an arch dependent dir, as they are arch dependent

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.1-4.20140429git4341094
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Apr 29 2014 Fabian Deutsch <fabiand@fedoraproject.org> - 0.0.1-2.20140429git4341094
- Update to latest snapshot
- Support for AMD Kabini

* Mon Jan 13 2014 Fabian Deutsch <fabiand@fedoraproject.org> - 0.0.1-2.20140108gitc002f62
- Move headers to main package, needed by clover at runtime

* Wed Jan 08 2014 Fabian Deutsch <fabiand@fedoraproject.org> - 0.0.1-1.20140108gitc002f62
- Could not use latest master because it doesn't build
- Update to a fresher snapshot
- Limit to x86

* Sun Jul 14 2013 Fabian Deutsch <fabiand@fedoraproject.org> - 0.0.1-0.20130714git5217211
- Initial package

