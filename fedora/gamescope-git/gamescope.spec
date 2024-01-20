%global build_repo https://github.com/ValveSoftware/gamescope.git

%global build_branch master

%define build_shortcommit %(git ls-remote %{build_repo} | grep "refs/heads/%{build_branch}" | cut -c1-8)
%define numeric_ver %(git ls-remote --refs --tags --sort='v:refname' %{build_repo} | cut --delimiter='/' --fields=3 | tail -1)
%global build_timestamp %(date +"%Y%m%d")

%global rel_build %{build_timestamp}.%{build_shortcommit}%{?dist}

%global libliftoff_minver 0.4.1

Name:           gamescope
Version:        %{numeric_ver}
Release:        %{rel_build}
Summary:        Micro-compositor for video games on Wayland

License:        BSD
URL:            https://github.com/ValveSoftware/gamescope

# upstream doesn't include a default pc file, so we need to provide one otherwise pkg-config won't find stb
# https://github.com/nothings/stb/issues/1191
Source1:        stb.pc

BuildRequires:  meson >= 0.54.0
BuildRequires:  ninja-build
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  glm-devel
BuildRequires:  google-benchmark-devel
BuildRequires:  libXmu-devel
BuildRequires:  pkgconfig(libavif)
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xdamage)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pkgconfig(xtst)
BuildRequires:  pkgconfig(xres)
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.17
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  (pkgconfig(wlroots) >= 0.17.0 with pkgconfig(wlroots) < 0.18.0)
BuildRequires:  (pkgconfig(libliftoff) >= 0.4.1 with pkgconfig(libliftoff) < 0.5)
BuildRequires:  stb-devel
BuildRequires:  stb_image_resize-devel
BuildRequires:  vkroots-devel
BuildRequires:  /usr/bin/glslangValidator
BuildRequires:  git

# libliftoff hasn't bumped soname, but API/ABI has changed for 0.2.0 release
Requires:       libliftoff%{?_isa} >= %{libliftoff_minver}
Requires:       xorg-x11-server-Xwayland
Recommends:     mesa-dri-drivers
Recommends:     mesa-vulkan-drivers

%description
%{name} is the micro-compositor optimized for running video games on Wayland.

%prep
git clone %{build_repo} --recursive --depth 1
cd gamescope
mkdir -p pkgconfig
cp %{SOURCE1} pkgconfig/stb.pc

%build
cd gamescope
export PKG_CONFIG_PATH=pkgconfig
%meson -Dpipewire=enabled -Denable_gamescope=true -Denable_gamescope_wsi_layer=true -Denable_openvr_support=true -Dforce_fallback_for=[]
%meson_build

%install
cd gamescope
%meson_install --skip-subprojects

%files
%license gamescope/LICENSE
%doc gamescope/README.md
%{_libdir}/*.so
%{_datadir}/vulkan/implicit_layer.d/*
%attr(0755, root, root) %caps(cap_sys_nice=ep) %{_bindir}/gamescope

%changelog
{{{ git_dir_changelog }}}
