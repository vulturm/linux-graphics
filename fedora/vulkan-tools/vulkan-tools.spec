%global build_repo https://github.com/KhronosGroup/Vulkan-Tools

%global latest_data %(git ls-remote %{build_repo} | grep 'refs/tags/sdk-' | sort -Vrk 2 | head -1)
%global numeric_ver %(echo %{latest_data} | grep -oP 'sdk.*' | grep -oP '[0-9.]+')
%global commit_date %(date +"%Y%m%d.%H")
%global rel_build %{commit_date}.rel%{numeric_ver}

Name:           vulkan-tools
Version:        %{numeric_ver}
Release:        %{rel_build}
Summary:        Vulkan tools

License:        ASL 2.0
URL:            %{build_repo}
Source0:        %url/archive/sdk-%{version}.tar.gz#/Vulkan-Tools-%{version}.tar.gz       

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake3
BuildRequires:  glslang
BuildRequires:  ninja-build
BuildRequires:  python%{python3_pkgversion}
BuildRequires:  vulkan-loader-devel
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xcb)

Provides:       vulkan-demos%{?_isa} = %{version}-%{release}
Obsoletes:      vulkan-demos < %{version}-%{release}

%description
Vulkan tools

%prep
%autosetup -n Vulkan-Tools-sdk-%{version}


%build
%cmake3 -GNinja -DCMAKE_BUILD_TYPE=Release -DGLSLANG_INSTALL_DIR=%{_bindir} .
%ninja_build


%install
%ninja_install
#mv %{buildroot}%{_bindir}/cube %{buildroot}%{_bindir}/vulkan-cube
#mv %{buildroot}%{_bindir}/cubepp %{buildroot}%{_bindir}/vulkan-cubepp


%files
%license LICENSE.txt
%doc README.md CONTRIBUTING.md
%{_bindir}/*

%changelog
* Tue Jul 16 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.

