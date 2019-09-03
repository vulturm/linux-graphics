%global build_repo https://github.com/KhronosGroup/Vulkan-ValidationLayers

%global latest_data %(git ls-remote %{build_repo} | grep 'refs/tags/sdk-' | sort -Vrk 2 | head -1)
%global numeric_ver %(echo %{latest_data} | grep -oP 'sdk.*' | grep -oP '[0-9.]+')
%global commit_date %(date +"%Y%m%d")
%global rel_build %{commit_date}%{?dist}


Name:           vulkan-validation-layers
Version:        %{numeric_ver}
Release:        %{rel_build}
Summary:        Vulkan validation layers

License:        ASL 2.0
URL:            %{build_repo}
Source0:        %url/archive/sdk-%{version}.tar.gz#/Vulkan-ValidationLayers-sdk-%{version}.tar.gz
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
%autosetup -p1 -n Vulkan-ValidationLayers-sdk-%{version}


%build
# Decrease debuginfo verbosity to reduce memory consumption even more
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')


%cmake3 -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DGLSLANG_INSTALL_DIR=%{_bindir} \
        -DCMAKE_INSTALL_INCLUDEDIR=%{_includedir}/vulkan/ .
%ninja_build


%install
%ninja_install


%ldconfig_scriptlets


%files
%license LICENSE.txt
%doc README.md CONTRIBUTING.md
%{_datadir}/vulkan/explicit_layer.d/*.json
%{_libdir}/libVkLayer_*.so

%files devel
%{_includedir}/vulkan/

%changelog
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
