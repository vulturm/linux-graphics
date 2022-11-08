%define package_name glslang
%global build_branch master

%global build_repo https://github.com/KhronosGroup/glslang
%global version_file https://raw.githubusercontent.com/KhronosGroup/glslang/{}/.gitignore
%global version_tag_regex reg_beg ([0-9.]+[0-9]) reg_end

%define version_string 11.12.0

%define commit f4cba22d08241cad63a270e33f4ef3384979982e
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20221108
%global gitrel .%{commit_date}.%{shortcommit}


Name:           %{package_name}
Version:        %{version_string}
Release:        0.2%{?gitrel}%{?dist}
URL:            %{build_repo}
Source0:        %{build_repo}/archive/%{commit}.tar.gz


Summary:        OpenGL and OpenGL ES shader front end and validator

License:        BSD and GPLv3+ and ASL 2.0
#Patch1:         glslang-default-resource-limits_staticlib.patch
# Patch to build against system spirv-tools (rebased locally)
#Patch3:         https://patch-diff.githubusercontent.com/raw/KhronosGroup/glslang/pull/1722.patch#/0001-pkg-config-compatibility.patch
Patch3:         0001-pkg-config-compatibility.patch

BuildRequires:  cmake3
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  spirv-tools-devel

%description
%{name} is the official reference compiler front end for the OpenGL
ES and OpenGL shading languages. It implements a strict
interpretation of the specifications for these languages.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{name} is the official reference compiler front end for the OpenGL
ES and OpenGL shading languages. It implements a strict
interpretation of the specifications for these languages.

%prep
#force downloading the project, seems that copr dist-cache is poisoned with bogus archive
curl -Lo %{_sourcedir}/%{commit}.tar.gz %{build_repo}/archive/%{commit}.tar.gz
%autosetup -p1 -n glslang-%{commit}

# Fix rpmlint warning on debuginfo
find . -name '*.h' -or -name '*.cpp' -or -name '*.hpp'| xargs chmod a-x

%build
%__mkdir_p build
pushd build
%cmake3 -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
        -DCMAKE_SKIP_RPATH:BOOL=yes \
        -DBUILD_SHARED_LIBS=OFF \
        -GNinja ..
%{ninja_build}
popd

%install
%{ninja_install} -C build

# we don't want them in here
rm -rf %{buildroot}%{_includedir}/SPIRV

%ifnarch s390x ppc64
%check
pushd Test
./runtests localResults ../build/StandAlone/glslangValidator ../build/StandAlone/spirv-remap
popd
%endif

# Install libglslang-default-resource-limits.a
install -pm 0644 build/StandAlone/libglslang-default-resource-limits.a %{buildroot}%{_libdir}/

%files
%doc README.md README-spirv-remap.txt
%{_bindir}/glslangValidator
%{_bindir}/spirv-remap

%files devel
%{_includedir}/glslang/
%{_libdir}/libHLSL.a
%{_libdir}/libOGLCompiler.a
%{_libdir}/libOSDependent.a
%{_libdir}/libSPIRV.a
%{_libdir}/libSPVRemapper.a
%{_libdir}/libglslang.a
%{_libdir}/libglslang-default-resource-limits.a
%{_libdir}/pkgconfig/glslang.pc
%{_libdir}/pkgconfig/spirv.pc
%{_libdir}/cmake/*

%changelog
* Wed Jan 29 2020 Dave Airlie <airlied@redhat.com> - 8.13.3559-1
- Update to latest git snapshot

* Sun Aug 04 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.

* Mon Jun 10 01:27:27 CEST 2019 Robert-André Mauchin <zebob.m@gmail.com> - 7.11.3214-1
- Release 7.11.3214
- Add patch to build against system spirv-tools

* Fri Mar 29 2019 Dave Airlie <airlied@redhat.com> - 3.1-0.13.20190329.gite0d59bb
- Update for vulkan 1.1.101.0

* Tue Feb 12 2019 Dave Airlie <airlied@redhat.com> - 3.1-0.12.20190212.git05d12a9
- Update for vulkan 1.1.92.0

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.1-0.11.20180727.gite99a268
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Aug 07 2018 Leigh Scott <leigh123linux@googlemail.com> - 3.1-0.10.20180727.gite99a268
- Update for vulkan 1.1.82.0

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.1-0.9.20180416.git3bb4c48
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Apr 23 2018 Leigh Scott <leigh123linux@googlemail.com> - 3.1-0.8.20180416.git3bb4c48
- Update for vulkan 1.1.73.0

* Wed Mar 07 2018 Adam Williamson <awilliam@redhat.com> - 3.1-0.7.20180205.git2651cca
- Rebuild to fix GCC 8 mis-compilation
  See https://da.gd/YJVwk ("GCC 8 ABI change on x86_64")

* Fri Feb 09 2018 Leigh Scott <leigh123linux@googlemail.com> - 3.1-0.6.20180205.git2651cca
- Update for vulkan 1.0.68.0

* Fri Feb 09 2018 Leigh Scott <leigh123linux@googlemail.com> - 3.1-0.5.20171028.git715c353
- Use ninja to build

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.1-0.4.20171028.git715c353
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 03 2018 Leigh Scott <leigh123linux@googlemail.com> - 3.1-0.3.20171028.git715c353
- Exclude s390x and ppc64 from check section

* Wed Jan 03 2018 Leigh Scott <leigh123linux@googlemail.com> - 3.1-0.2.20171028.git715c353
- Add check section to run tests
- Split binaries into main package

* Thu Jul 13 2017 Leigh Scott <leigh123linux@googlemail.com> - 3.1-0.1.20171028.git715c353
- First build
