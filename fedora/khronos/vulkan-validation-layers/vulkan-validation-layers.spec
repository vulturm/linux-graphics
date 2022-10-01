%define package_name vulkan-validation-layers
%global build_branch master

%global build_repo https://github.com/KhronosGroup/Vulkan-ValidationLayers
%global version_file https://raw.githubusercontent.com/KhronosGroup/Vulkan-ValidationLayers/{}/.gitignore
%global version_tag_regex reg_beg sdk-(.*) reg_end

%define version_string 1.3.224.1

%define commit db898178ffb64f88756124cf97738f6419019a8b
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20221001
%global gitrel .%{commit_date}.%{shortcommit}


Name:           %{package_name}
Version:        %{version_string}
Release:        0.2%{?gitrel}%{?dist}
Summary:        Vulkan validation layers

License:        ASL 2.0
URL:            %{build_repo}
Source0:        %{build_repo}/archive/%{commit}.tar.gz#/%{name}-%{commit}.tar.gz
Patch0:         fix_shared.patch


BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake3
BuildRequires:  glslang-devel
BuildRequires:  ninja-build
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  spirv-tools-devel
BuildRequires:  vulkan-loader-devel
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xcb)

%description
Vulkan validation layers

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vulkan-headers

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -p1 -n Vulkan-ValidationLayers-%{commit}


%build
# Decrease debuginfo verbosity to reduce memory consumption even more
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')


%cmake3 -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DGLSLANG_INSTALL_DIR=%{_prefix} \
        -DBUILD_LAYER_SUPPORT_FILES:BOOL=ON \
        -DCMAKE_INSTALL_INCLUDEDIR=%{_includedir}/vulkan/ .
%cmake3_build


%install
%cmake3_install


%ldconfig_scriptlets


%files
%license LICENSE.txt
%doc README.md CONTRIBUTING.md
%{_datadir}/vulkan/explicit_layer.d/*.json
%{_libdir}/libVkLayer_*.so

%files devel
%{_includedir}/vulkan/

%changelog
* Tue Aug 11 2020 Mihai Vultur <xanto@egaming.ro>
- Fix CMake to do out-of-source builds: https://fedoraproject.org/wiki/Changes/CMake_to_do_out-of-source_builds

* Sun Jul 28 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.

* Tue Jun 25 2019 Dave Airlie <airlied@redhat.com> - 1.1.108.0-1
- Update valdiation layers to 1.1.108.0

* Wed Mar 06 2019 Dave Airlie <airlied@redhat.com> - 1.1.101.0-1
- Update valdiation layers to 1.1.101.0

* Wed Feb 13 2019 Dave Airlie <airlied@redhat.com> - 1.1.97.0-1
- Update validation layers to 1.1.97.0

* Wed Feb 13 2019 Dave Airlie <airlied@redhat.com> - 1.1.92.0-1
- Update validation layers to 1.1.92.0

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.82.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Aug 07 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.82.0-1
- Update to 1.1.82.0

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.77.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 26 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-3
- Workaround i686 build issue

* Tue Jun 26 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-2
- Exclude i686 due to 'virtual memory exhausted' FTBFS

* Sat Jun 23 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-1
- Initial package
