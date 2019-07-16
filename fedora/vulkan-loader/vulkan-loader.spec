%global build_repo https://github.com/KhronosGroup/Vulkan-Loader

%global latest_data %(git ls-remote %{build_repo} | grep 'refs/tags/sdk-' | sort -Vrk 2 | head -1)
%global numeric_ver %(echo %{latest_data} | grep -oP 'sdk.*' | grep -oP '[0-9.]+')
%global commit_date %(date +"%Y%m%d.%H")
%global rel_build %{commit_date}.rel%{numeric_ver}

Name:           vulkan-loader
Version:        %{numeric_ver}
Release:        %{rel_build}
Summary:        Vulkan ICD desktop loader

License:        ASL 2.0
URL:            %{build_repo}
Source0:        %url/archive/sdk-%{version}.tar.gz#/Vulkan-Loader-%{version}.tar.gz       

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake3
BuildRequires:  ninja-build
BuildRequires:  python%{python3_pkgversion}
BuildRequires:  vulkan-headers >= 1.1.108
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xrandr)

Provides:       vulkan%{?_isa} = %{version}-%{release}
Provides:       vulkan = %{version}-%{release}
Obsoletes:      vulkan < %{version}-%{release}
Provides:       vulkan-filesystem = %{version}-%{release}
Obsoletes:      vulkan-filesystem < %{version}-%{release}

%if 0%{?fedora} <= 27
%ifarch x86_64 i686 
Recommends:       mesa-vulkan-drivers%{?_isa}
%endif
%else
Recommends:       mesa-vulkan-drivers%{?_isa}
%endif

%description
This project provides the Khronos official Vulkan ICD desktop 
loader for Windows, Linux, and MacOS.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vulkan-headers
Provides:       vulkan-devel%{?_isa} = %{version}-%{release}
Provides:       vulkan-devel = %{version}-%{release}
Obsoletes:      vulkan-devel < %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%autosetup -n Vulkan-Loader-%{version}


%build
%cmake3 -GNinja -DCMAKE_BUILD_TYPE=Release .
%ninja_build


%install
%ninja_install

# create the filesystem
mkdir -p %{buildroot}%{_sysconfdir}/vulkan/{explicit,implicit}_layer.d/ \
%{buildroot}%{_datadir}/vulkan/{explicit,implicit}_layer.d/ \
%{buildroot}{%{_sysconfdir},%{_datadir}}/vulkan/icd.d


%ldconfig_scriptlets


%files
%license LICENSE.txt
%doc README.md CONTRIBUTING.md
%dir %{_sysconfdir}/vulkan/
%dir %{_sysconfdir}/vulkan/explicit_layer.d/
%dir %{_sysconfdir}/vulkan/icd.d/
%dir %{_sysconfdir}/vulkan/implicit_layer.d/
%dir %{_datadir}/vulkan/
%dir %{_datadir}/vulkan/explicit_layer.d/
%dir %{_datadir}/vulkan/icd.d/
%dir %{_datadir}/vulkan/implicit_layer.d/
%{_libdir}/*.so.*

%files devel
%{_libdir}/pkgconfig/vulkan.pc
%{_libdir}/*.so


%changelog
* Tue Jul 16 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.

* Tue Aug 07 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.82.0-1
- Update to 1.1.82.0

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.77.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jun 27 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-4
- Fix update path

* Tue Jun 26 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-3
- Add conditional for mesa-vulkan-drivers requires

* Tue Jun 26 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-2
- Improve description and summary
- Set release

* Sat Jun 23 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-1
- Initial package
