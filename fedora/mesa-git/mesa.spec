%define package_name mesa
%global build_branch master
%bcond_with patented_video_codecs 0
%global _default_patch_fuzz 2
#global __meson_auto_features disabled

%global build_repo https://gitlab.freedesktop.org/mesa/mesa
%define version_string 25.1.0
%global version_major %(ver=%{version_string}; echo ${ver%.*.*})

%define commit 2a56afed8dc5003614818872550bc6026c28fffe
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20250306.14
%global gitrel .%{commit_date}.%{shortcommit}

%global hw_video_codecs_free vc1dec,av1dec,av1enc,vp9dec
%global hw_video_codecs_patented ,h264dec,h264enc,h265dec,h265enc

%ifnarch s390x
%global with_hardware 1
%global with_vulkan_hw 1
%global with_vdpau 1
%global with_va 1
%if !0%{?rhel}
%global with_nine 1
%global with_nvk %{with vulkan_hw}
%global with_opencl 1
%global with_opencl_rust 1
%endif
%global base_vulkan ,amd
%endif

%ifarch %{ix86} x86_64
%global with_crocus 1
%global with_i915   1
%global with_intel_clc 1
%global with_iris   1
%global with_xa     1
%global intel_platform_vulkan ,intel,intel_hasvk
%endif

%ifarch x86_64
%global with_intel_vk_rt 1
%endif

%ifarch aarch64 x86_64 %{ix86}
%if !0%{?rhel}
%global with_lima      1
%global with_vc4       1
%endif
%global with_etnaviv   1
%global with_freedreno 1
%global with_kmsro     1
%global with_panfrost  1
%global with_tegra     1
%global with_v3d       1
%global with_xa        1
%global extra_platform_vulkan ,broadcom,freedreno,panfrost,imagination-experimental
%endif

%ifnarch s390x
%if !0%{?rhel}
%global with_r300 1
%global with_r600 1
%endif
%global with_radeonsi 1
%global with_vmware 1
%endif

%if !0%{?rhel}
%global with_libunwind 1
%global with_lmsensors 1
%endif

%ifarch %{valgrind_arches}
%bcond_without valgrind
%else
%bcond_with valgrind
%endif

%global with_vulkan_overlay 1
%global vulkan_drivers swrast%{?base_vulkan}%{?intel_platform_vulkan}%{?extra_platform_vulkan}%{?with_nvk:,nouveau}

Name:           %{package_name}
Summary:        Mesa 3D Graphics Library, git version
Version:        %{version_string}
Release:        0.3%{?gitrel}%{?dist}

License:        MIT
URL:            http://www.mesa3d.org

Source0:        %{build_repo}/-/archive/%{commit}.tar.gz#/mesa-%{commit}.tar.gz
# src/gallium/auxiliary/postprocess/pp_mlaa* have an ... interestingly worded license.
# Source1 contains email correspondence clarifying the license terms.
# Fedora opts to ignore the optional part of clause 2 and treat that code as 2 clause BSD.
Source1:        Mesa-MLAA-License-Clarification-Email.txt


# Disable rgb10 configs by default:
# https://bugzilla.redhat.com/show_bug.cgi?id=1560481
#Patch7:         0001-gallium-Disable-rgb10-configs-by-default.patch
Patch1:         001-disable-proc_macro2-unstable-features.patch

BuildRequires:  meson >= 1.3.0
BuildRequires:  cbindgen
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gettext
%if 0%{?with_hardware}
BuildRequires:  kernel-headers
%endif
# We only check for the minimum version of pkgconfig(libdrm) needed so that the
# SRPMs for each arch still have the same build dependencies. See:
# https://bugzilla.redhat.com/show_bug.cgi?id=1859515
BuildRequires:  pkgconfig(libdrm) >= 2.4.97
%if 0%{?with_libunwind}
BuildRequires:  pkgconfig(libunwind)
%endif
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(zlib) >= 1.2.3
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(libselinux)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.8
BuildRequires:  pkgconfig(wayland-client) >= 1.11
BuildRequires:  pkgconfig(wayland-server) >= 1.11
BuildRequires:  pkgconfig(wayland-egl-backend) >= 3
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xdamage) >= 1.1
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xcb-glx) >= 1.8.1
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xcb-dri2) >= 1.8
BuildRequires:  pkgconfig(xcb-dri3)
BuildRequires:  pkgconfig(xcb-present)
BuildRequires:  pkgconfig(xcb-sync)
BuildRequires:  pkgconfig(xshmfence) >= 1.1
BuildRequires:  pkgconfig(dri2proto) >= 2.8
BuildRequires:  pkgconfig(glproto) >= 1.4.14
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcb-randr)
BuildRequires:  pkgconfig(xrandr) >= 1.3
BuildRequires:  python3-pycparser
BuildRequires:  bison
BuildRequires:  flex
%if 0%{?with_lmsensors}
BuildRequires:  lm_sensors-devel
%endif
%if 0%{?with_vdpau}
BuildRequires:  pkgconfig(vdpau) >= 1.1
%endif
%if 0%{?with_va}
BuildRequires:  pkgconfig(libva) >= 0.38.0
%endif
BuildRequires:  pkgconfig(libelf)
BuildRequires:  pkgconfig(libglvnd) >= 1.3.2
BuildRequires:  llvm-devel >= 7.0.0
%if 0%{?with_opencl} || 0%{?with_nvk}
BuildRequires:  clang-devel
BuildRequires:  bindgen
BuildRequires:  rustfmt
BuildRequires:  rust-packaging
BuildRequires:  pkgconfig(libclc)
BuildRequires:  pkgconfig(SPIRV-Tools)
BuildRequires:  pkgconfig(LLVMSPIRVLib)
%endif
%if 0%{?with_nvk}
BuildRequires:  (crate(paste/default) >= 1.0.0 with crate(paste/default) < 2.0.0~)
BuildRequires:  (crate(proc-macro2) >= 1.0.56 with crate(proc-macro2) < 2)
BuildRequires:  (crate(quote) >= 1.0.25 with crate(quote) < 2)
BuildRequires:  (crate(syn/clone-impls) >= 2.0.15 with crate(syn/clone-impls) < 3)
BuildRequires:  (crate(unicode-ident) >= 1.0.6 with crate(unicode-ident) < 2)
%endif
%if %{with valgrind}
BuildRequires:  pkgconfig(valgrind)
%endif
BuildRequires:  python3-devel
BuildRequires:  python3-yaml
BuildRequires:  python3-mako
%if 0%{?with_intel_clc}
BuildRequires:  python3-ply
%endif
BuildRequires:  vulkan-headers
BuildRequires:  glslang
%if 0%{?with_vulkan_hw}
BuildRequires:  pkgconfig(vulkan)
%endif


%description
%{summary}.

%package filesystem
Summary:        Mesa driver filesystem
Provides:       mesa-dri-filesystem = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-omx-drivers < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-libglapi < %{?epoch:%{epoch}:}%{version}-%{release}

%description filesystem
%{summary}.

%package libGL
Summary:        Mesa libGL runtime libraries
Requires:       libglvnd-glx%{?_isa} >= 1:1.3.2
Recommends:     %{name}-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description libGL
%{summary}.

%package libGL-devel
Summary:        Mesa libGL development package
Requires:       %{name}-libGL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libglvnd-devel%{?_isa} >= 1:1.3.2
Provides:       libGL-devel
Provides:       libGL-devel%{?_isa}

%description libGL-devel
%{summary}.

%package libEGL
Summary:        Mesa libEGL runtime libraries
Requires:       libglvnd-egl%{?_isa} >= 1:1.3.2
Requires:       %{name}-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Recommends:     %{name}-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      egl-icd < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      libOSMesa < %{?epoch:%{epoch}:}%{version}-%{release}

%description libEGL
%{summary}.

%package libEGL-devel
Summary:        Mesa libEGL development package
Requires:       %{name}-libEGL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libglvnd-devel%{?_isa} >= 1:1.3.2
Requires:       %{name}-khr-devel%{?_isa}
Provides:       libEGL-devel
Provides:       libEGL-devel%{?_isa}
Obsoletes:      libOSMesa-devel < %{?epoch:%{epoch}:}%{version}-%{release}


%description libEGL-devel
%{summary}.

%package dri-drivers
Summary:        Mesa-based DRI drivers
Requires:       %{name}-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
%if 0%{?with_va}
Recommends:     %{name}-va-drivers%{?_isa}
%endif

%description dri-drivers
%{summary}.

%if 0%{?with_va}
%package        va-drivers
Summary:        Mesa-based VA-API video acceleration drivers
Requires:       %{name}-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      %{name}-vaapi-drivers < 22.2.0-5

%description va-drivers
%{summary}.
%endif

%if 0%{?with_vdpau}
%package        vdpau-drivers
Summary:        Mesa-based VDPAU drivers
Requires:       %{name}-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description vdpau-drivers
%{summary}.
%endif

%package libgbm
Summary:        Mesa gbm runtime library
Provides:       libgbm
Provides:       libgbm%{?_isa}
Recommends:     %{name}-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description libgbm
%{summary}.

%package libgbm-devel
Summary:        Mesa libgbm development package
Requires:       %{name}-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libgbm-devel
Provides:       libgbm-devel%{?_isa}

%description libgbm-devel
%{summary}.

%if 0%{?with_xa}
%package libxatracker
Summary:        Mesa XA state tracker
Provides:       libxatracker
Provides:       libxatracker%{?_isa}

%description libxatracker
%{summary}.

%package libxatracker-devel
Summary:        Mesa XA state tracker development package
Requires:       %{name}-libxatracker%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libxatracker-devel
Provides:       libxatracker-devel%{?_isa}

%description libxatracker-devel
%{summary}.
%endif

%if 0%{?with_opencl}
%package libOpenCL
Summary:        Mesa OpenCL runtime library
Requires:       ocl-icd%{?_isa}
Requires:       libclc%{?_isa}
Requires:       %{name}-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       opencl-filesystem

%description libOpenCL
%{summary}.

%package libOpenCL-devel
Summary:        Mesa OpenCL development package
Requires:       %{name}-libOpenCL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description libOpenCL-devel
%{summary}.
%endif

%if 0%{?with_nine}
%package libd3d
Summary:        Mesa Direct3D9 state tracker

%description libd3d
%{summary}.

%package libd3d-devel
Summary:        Mesa Direct3D9 state tracker development package
Requires:       %{name}-libd3d%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description libd3d-devel
%{summary}.
%endif

%package vulkan-drivers
Summary:        Mesa Vulkan drivers
Requires:       vulkan%{_isa}
Obsoletes:      mesa-vulkan-devel < %{?epoch:%{epoch}:}%{version}-%{release}

%description vulkan-drivers
The drivers with support for the Vulkan API.


%prep
%setup -q -c
%autosetup -n mesa-%{commit} -p1
cp %{SOURCE1} docs/

%build
# ensure standard Rust compiler flags are set
export RUSTFLAGS="%build_rustflags"

%if 0%{?with_nvk}
export MESON_PACKAGE_CACHE_DIR="%{cargo_registry}/"
# So... Meson can't actually find them without tweaks
%define inst_crate_nameversion() %(basename %{cargo_registry}/%{1}-*)
%define rewrite_wrap_file() sed -e "/source.*/d" -e "s/%{1}-.*/%{inst_crate_nameversion %{1}}/" -i subprojects/%{1}.wrap

%rewrite_wrap_file paste
%rewrite_wrap_file proc-macro2
%rewrite_wrap_file quote
%rewrite_wrap_file syn
%rewrite_wrap_file unicode-ident
%endif 

# We've gotten a report that enabling LTO for mesa breaks some games. See
# https://bugzilla.redhat.com/show_bug.cgi?id=1862771 for details.
# Disable LTO for now
%define _lto_cflags %{nil}

%meson \
  -Dplatforms=x11,wayland \
%if 0%{?with_hardware}
  -Dgallium-drivers=swrast,virgl,nouveau%{?with_r300:,r300}%{?with_crocus:,crocus}%{?with_i915:,i915}%{?with_iris:,iris}%{?with_vmware:,svga}%{?with_radeonsi:,radeonsi}%{?with_r600:,r600}%{?with_freedreno:,freedreno}%{?with_etnaviv:,etnaviv}%{?with_tegra:,tegra}%{?with_vc4:,vc4}%{?with_v3d:,v3d}%{?with_lima:,lima}%{?with_panfrost:,panfrost}%{?with_vulkan_hw:,zink} \
%else
  -Dgallium-drivers=swrast,virgl \
%endif
  -Dgallium-vdpau=%{?with_vdpau:enabled}%{!?with_vdpau:disabled} \
  -Dgallium-va=%{?with_va:enabled}%{!?with_va:disabled} \
  -Dgallium-xa=%{?with_xa:enabled}%{!?with_xa:disabled} \
  -Dgallium-nine=%{?with_nine:true}%{!?with_nine:false} \
  -Dgallium-opencl=%{?with_opencl:icd}%{!?with_opencl:disabled} \
 %if 0%{?with_opencl_rust}
  -Dgallium-rusticl=true \
 %endif
  -Dvulkan-drivers=%{?vulkan_drivers} \
  -Dvulkan-layers=device-select%{?with_vulkan_overlay:,overlay} \
  -Dshared-glapi=enabled \
  -Dgles1=enabled \
  -Dgles2=enabled \
  -Dopengl=true \
  -Dgbm=enabled \
  -Dglx=dri \
  -Degl=enabled \
  -Dglvnd=enabled \
%if 0%{?with_intel_clc}
  -Dintel-clc=enabled \
%endif
  -Dintel-rt=%{?with_intel_vk_rt:enabled}%{!?with_intel_vk_rt:disabled} \
  -Dmicrosoft-clc=disabled \
  -Dllvm=enabled \
  -Dshared-llvm=enabled \
  -Dvalgrind=%{?with_valgrind:enabled}%{!?with_valgrind:disabled} \
  -Dbuild-tests=false \
  -Dselinux=true \
%if !0%{?with_libunwind}
  -Dlibunwind=disabled \
%endif
%if !0%{?with_lmsensors}
  -Dlmsensors=disabled \
%endif
  -Dandroid-libbacktrace=disabled \
%ifarch %{ix86}
  -Dglx-read-only-text=true \
%endif
  -Dvideo-codecs=%{?hw_video_codecs_free}%{?with_patented_video_codecs:%{hw_video_codecs_patented}} \
  %{nil}
%meson_build

%install
%meson_install

# libvdpau opens the versioned name, don't bother including the unversioned
rm -vf %{buildroot}%{_libdir}/vdpau/*.so
# likewise glvnd
rm -vf %{buildroot}%{_libdir}/libGLX_mesa.so
rm -vf %{buildroot}%{_libdir}/libEGL_mesa.so
# XXX can we just not build this
rm -vf %{buildroot}%{_libdir}/libGLES*

# glvnd needs a default provider for indirect rendering where it cannot
# determine the vendor
ln -s %{_libdir}/libGLX_mesa.so.0 %{buildroot}%{_libdir}/libGLX_system.so.0

# this keeps breaking, check it early.  note that the exit from eu-ftr is odd.
pushd %{buildroot}%{_libdir}
for i in libGL*.so ; do
    sleep 1
    eu-findtextrel $i && exit 1
done
popd

%files filesystem
%doc docs/Mesa-MLAA-License-Clarification-Email.txt
%dir %{_libdir}/dri
%if 0%{?with_hardware}
%if 0%{?with_vdpau}
%dir %{_libdir}/vdpau
%endif
%endif

%files libGL
%{_libdir}/libGLX_mesa.so.0*
%{_libdir}/libGLX_system.so.0*
%files libGL-devel
%{_includedir}/GL/*
%{_libdir}/pkgconfig/dri.pc


%files libEGL
%{_datadir}/glvnd/egl_vendor.d/50_mesa*.json
%{_libdir}/libEGL_mesa.so.0*
%files libEGL-devel
%dir %{_includedir}/EGL
%{_includedir}/EGL/*.h

%files libgbm
%{_libdir}/gbm/dri_gbm.so
%{_libdir}/libgbm.so.1
%{_libdir}/libgbm.so.1.*
%files libgbm-devel
%{_libdir}/libgbm.so
%{_includedir}/gbm.h
%{_libdir}/pkgconfig/gbm.pc

%if 0%{?with_xa}
%files libxatracker
%if 0%{?with_hardware}
%{_libdir}/libxatracker.so.2
%{_libdir}/libxatracker.so.2.*
%endif

%files libxatracker-devel
%if 0%{?with_hardware}
%{_libdir}/libxatracker.so
%{_includedir}/xa_tracker.h
%{_includedir}/xa_composite.h
%{_includedir}/xa_context.h
%{_libdir}/pkgconfig/xatracker.pc
%endif
%endif

%if 0%{?with_opencl}
%files libOpenCL
%{_libdir}/libMesaOpenCL.so.*
%if 0%{?with_opencl_rust}
%{_libdir}/libRusticlOpenCL.so.*
%endif
%{_sysconfdir}/OpenCL/vendors/mesa.icd
%if 0%{?with_opencl_rust}
%{_sysconfdir}/OpenCL/vendors/rusticl.icd
%endif
%files libOpenCL-devel
%{_libdir}/libMesaOpenCL.so
%if 0%{?with_opencl_rust}
%{_libdir}/libRusticlOpenCL.so
%endif
%endif

%if 0%{?with_nine}
%files libd3d
%dir %{_libdir}/d3d/
%{_libdir}/d3d/*.so.*

%files libd3d-devel
%{_libdir}/pkgconfig/d3d.pc
%{_includedir}/d3dadapter/
%{_libdir}/d3d/*.so
%endif

%files dri-drivers
%dir %{_datadir}/drirc.d
%{_datadir}/drirc.d/*.conf
%{_libdir}/dri/kms_swrast_dri.so
%{_libdir}/dri/swrast_dri.so
%{_libdir}/dri/virtio_gpu_dri.so

%if 0%{?with_hardware}
  %if 0%{?with_r300}
    %{_libdir}/dri/r300_dri.so
  %endif
  %if 0%{?with_radeonsi}
    %if 0%{?with_r600}
      %{_libdir}/dri/r600_dri.so
    %endif
  %{_libdir}/dri/radeonsi_dri.so
%endif
%ifarch %{ix86} x86_64
  %{_libdir}/dri/crocus_dri.so
  %{_libdir}/dri/i915_dri.so
  %if 0%{?with_iris}
    %{_libdir}/dri/iris_dri.so
  %endif
%endif

%ifarch aarch64 x86_64 %{ix86}
  %{_libdir}/dri/ingenic-drm_dri.so
  %{_libdir}/dri/imx-drm_dri.so
  %{_libdir}/dri/imx-lcdif_dri.so
  %{_libdir}/dri/kirin_dri.so
  %{_libdir}/dri/komeda_dri.so
  %{_libdir}/dri/mali-dp_dri.so
  %{_libdir}/dri/mcde_dri.so
  %{_libdir}/dri/mxsfb-drm_dri.so
  %{_libdir}/dri/panel-mipi-dbi_dri.so
  %{_libdir}/dri/rcar-du_dri.so
  %{_libdir}/dri/sti_dri.so
  %{_libdir}/dri/stm_dri.so
%endif
%if 0%{?with_vc4}
%{_libdir}/dri/vc4_dri.so
%endif
%if 0%{?with_v3d}
%{_libdir}/dri/v3d_dri.so
%endif
%if 0%{?with_freedreno}
%{_libdir}/dri/kgsl_dri.so
%{_libdir}/dri/msm_dri.so
%endif
%if 0%{?with_etnaviv}
%{_libdir}/dri/etnaviv_dri.so
%endif
%if 0%{?with_tegra}
%{_libdir}/dri/tegra_dri.so
%endif
%if 0%{?with_lima}
%{_libdir}/dri/lima_dri.so
%endif
%if 0%{?with_panfrost}
%{_libdir}/dri/panfrost_dri.so
%{_libdir}/dri/hdlcd_dri.so
%endif
%{_libdir}/dri/nouveau_dri.so
%if 0%{?with_vmware}
%{_libdir}/dri/vmwgfx_dri.so
%endif
%endif
%if 0%{?with_hardware}
%dir %{_libdir}/gallium-pipe
%{_libdir}/gallium-pipe/*.so
%{_libdir}/dri/libdril_dri.so
%{_libdir}/libgallium-*.so
%endif

# old kmsro drivers
%{_libdir}/dri/armada-drm_dri.so
%{_libdir}/dri/exynos_dri.so
%{_libdir}/dri/gm12u320_dri.so
%{_libdir}/dri/hx8357d_dri.so
%{_libdir}/dri/ili9163_dri.so
%{_libdir}/dri/ili9225_dri.so
%{_libdir}/dri/ili9341_dri.so
%{_libdir}/dri/ili9486_dri.so
%{_libdir}/dri/imx-dcss_dri.so
%{_libdir}/dri/mediatek_dri.so
%{_libdir}/dri/meson_dri.so
%{_libdir}/dri/mi0283qt_dri.so
%{_libdir}/dri/panthor_dri.so
%{_libdir}/dri/pl111_dri.so
%{_libdir}/dri/repaper_dri.so
%{_libdir}/dri/rockchip_dri.so
%{_libdir}/dri/rzg2l-du_dri.so
%{_libdir}/dri/ssd130x_dri.so
%{_libdir}/dri/st7586_dri.so
%{_libdir}/dri/st7735r_dri.so
%{_libdir}/dri/sun4i-drm_dri.so
%{_libdir}/dri/udl_dri.so
%{_libdir}/dri/vkms_dri.so
%{_libdir}/dri/zynqmp-dpsub_dri.so
%{_libdir}/dri/zink_dri.so
# kmsro end

%if 0%{?with_hardware}
%if 0%{?with_va}
%files va-drivers
%{_libdir}/dri/nouveau_drv_video.so
%if 0%{?with_r600}
%{_libdir}/dri/r600_drv_video.so
%endif
%if 0%{?with_radeonsi}
%{_libdir}/dri/radeonsi_drv_video.so
%endif
%{_libdir}/dri/virtio_gpu_drv_video.so
%endif

%if 0%{?with_vdpau}
%files vdpau-drivers
%{_libdir}/vdpau/libvdpau_nouveau.so.1*
%if 0%{?with_r600}
%{_libdir}/vdpau/libvdpau_r600.so.1*
%endif
%if 0%{?with_radeonsi}
%{_libdir}/vdpau/libvdpau_radeonsi.so.1*
%endif
%endif
%{_libdir}/vdpau/libvdpau_virtio_gpu.so.1*
%endif

%files vulkan-drivers
%{_libdir}/libvulkan_lvp.so
%{_datadir}/vulkan/icd.d/lvp_icd.*.json
%if 0%{?with_vulkan_overlay}
%{_bindir}/mesa-overlay-control.py
%{_libdir}/libVkLayer_MESA_overlay.so
%{_datadir}/vulkan/explicit_layer.d/VkLayer_MESA_overlay.json
%endif
%{_libdir}/libVkLayer_MESA_device_select.so
%{_datadir}/vulkan/implicit_layer.d/VkLayer_MESA_device_select.json

%if 0%{?with_vulkan_hw}
%{_libdir}/libvulkan_radeon.so
%{_datadir}/vulkan/icd.d/radeon_icd.*.json
%if 0%{?with_nvk}
%{_libdir}/libvulkan_nouveau.so
%{_datadir}/vulkan/icd.d/nouveau_icd.*.json
%endif
%ifarch %{ix86} x86_64
  %{_libdir}/libvulkan_intel.so
  %{_libdir}/libvulkan_intel_hasvk.so
  %{_datadir}/vulkan/icd.d/intel_icd.*.json
  %{_datadir}/vulkan/icd.d/intel_hasvk_icd.*.json
%endif
%ifarch aarch64 x86_64 %{ix86}
  %{_libdir}/libvulkan_broadcom.so
  %{_datadir}/vulkan/icd.d/broadcom_icd.*.json
  %{_libdir}/libvulkan_freedreno.so
  %{_datadir}/vulkan/icd.d/freedreno_icd.*.json
  %{_libdir}/libvulkan_panfrost.so
  %{_datadir}/vulkan/icd.d/panfrost_icd.*.json
  %{_libdir}/libpowervr_rogue.so
  %{_libdir}/libvulkan_powervr_mesa.so
  %{_datadir}/vulkan/icd.d/powervr_mesa_icd.*.json
%endif
%endif

%changelog
* Thu Mar 06 2025 Mihai Vultur <xanto@egaming.ro>
  Remove references to osmesa as it has been removed after:
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/33836

* Fri Jan 24 2025 Mihai Vultur <xanto@egaming.ro>
  Remove references to libglapi as it is no longer generated by mesa after:
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/32789

* Fri Sep 20 2024 Mihai Vultur <xanto@egaming.ro>
  New dri_gbm.so after: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/31074

* Fri Sep 13 2024 Mihai Vultur <xanto@egaming.ro>
  libgallium_drv_video and libvdpau_gallium are no longer being generated.

* Tue Sep 10 2024 Mihai Vultur <xanto@egaming.ro>
  Remove references to OMX as it was removed from mesa.

* Fri Aug 02 2024 Mihai Vultur <xanto@egaming.ro>
  Compile mesa without patented codecs, as per COPR System Team request.

* Fri Aug 02 2024 Mihai Vultur <xanto@egaming.ro>
  Remove kmsro option after: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/30463

* Wed Jul 24 2024 Mihai Vultur <xanto@egaming.ro>
  Enable 'intel-rt' for x64 bit targets.

* Mon Jul 22 2024 Mihai Vultur <xanto@egaming.ro>
  'rustfmt' has become a build dependency.

* Fri Jul 19 2024 Mihai Vultur <xanto@egaming.ro>
  Adaptations for commit d5ec3a89

* Fri Jul 19 2024 Mihai Vultur <xanto@egaming.ro>
  Commit d709b421 removed zink_dri.so

* Tue Apr 09 2024 Mihai Vultur <xanto@egaming.ro>
  NVK depends on cbindgen and rust-paste now. Adjust dependencies.

* Thu Feb 29 2024 Mihai Vultur <xanto@egaming.ro>
  NVK got vulkan conformance, 'nouveau-experimental', becomes 'nouveou' now.

* Mon Feb 19 2024 Mihai Vultur <xanto@egaming.ro>
  Disable intel-rt until the issue with 32bit compilation is fixed.
  Bugzilla: https://gitlab.freedesktop.org/mesa/mesa/-/issues/10629

* Tue Feb 13 2024 Mihai Vultur <xanto@egaming.ro>
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/27593
  If we do a native build, regardless of the host architecture and we
  build Anv or Iris, we need intel-clc. So force building that tool.
 
* Sun Feb 04 2024 Mihai Vultur <xanto@egaming.ro>
  Enable imagination-experimental (PowerVR) Vulkan Driver.
  Enable nouveau-experimental for Nvidia Drivers. For Kernel 6.7+

* Sat Jan 27 2024 Mihai Vultur <xanto@egaming.ro>
  Add ssd130x to the list of kmsro drivers
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/27135

* Sun Jan 21 2024 Mihai Vultur <xanto@egaming.ro>
  Enable av1 dec/enc and vp9 dec codecs.

* Mon Nov 27 2023 José Expósitojexposit@redhat.com>
  Set glx-read-only-text on i386
  An update on the linker will now refuse to create binaries with a loadable
  memory segment that has read, write and execute permissions set.
  mesa creates one unless "glx-read-only-text" is enabled.
 
* Sat Nov 11 2023 Mihai Vultur <mihaivultur7@gmail.com>
  Add new drivers to the list: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/26129
 
* Wed Oct 25 2023 Mihai Vultur <mihaivultur7@gmail.com>
  Various modifications and adjustments to more closely follow the official spec.
  + hdlcd_dri.so
 
* Tue Feb 28 2023 Mihai Vultur <mihaivultur7@gmail.com>
  According to https://gitlab.freedesktop.org/mesa/mesa/-/commit/a06ab9849db7fdf8f5194412f0c5a15abd8ece9b
  Vdpau support for r300 has been dropped.

* Tue Feb 28 2023 Fabio Valentini <decathorpe@gmail.com>
  Ensure standard Rust compiler flags are set.

* Thu Jan 12 2023 Mihai Vultur <mihaivultur7@gmail.com>
  Introduce 'with_opencl_rust' and temporary disable rust opencl.

* Thu Jan 12 2023 Peter Robinson <pbrobinson@fedoraproject.org>
   Enable rusticl as an optional OpenCL engine

* Sat Dec 17 2022 Mihai Vultur <mihaivultur7@gmail.com>
  Use official freedesktop gitlab url for downloading source archive.
  .. for some reason it seems like mirroring to github is not working.

* Mon Dec 12 2022 Mihai Vultur <mihaivultur7@gmail.com>
  Use '-Dxmlconfig=enabled' otherwise drirc config files won't be generated..

* Wed Nov 16 2022 Mihai Vultur <mihaivultur7@gmail.com>
  Use '-Dcpp_std=gnu++17' to unbreak the build.

* Thu Oct 06 2022 Ibrahim Ansari <retrixe@users.noreply.github.com>
- The Intel ANV Vulkan driver no longer supports Gen7/8 integrated graphics,
  instead, the Vulkan support for these GPUs has been moved into a new "HASVK" driver.
- Enable 'intel_hasvk'.

* Thu Oct 06 2022 Mihai Vultur <xanto@egaming.ro>
- Carry over and adapt some patches from upstream:
 60b9e9d Rename mesa-vaapi-drivers to mesa-va-drivers
 07e1e0b mesa: split out vaapi drivers into separate package
 8a2edad Recommend mesa-dri-drivers from libGL, libEGL, and libgbm subpackages (rhbz#1900633)
 8d117d9 Remove old obsoletes

* Mon Aug 15 2022 Mihai Vultur <xanto@egaming.ro>
- Adjust specfile after eglextchromium.h removal
- MR https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/17815

* Sat Apr 30 2022 Mikhail Gavrilov <mikhail.v.gavrilov@gmail.com>
- Reenabling all hw implementations of video codecs which was disabled by
- MR https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/15258.

* Wed Mar 02 2022 Mihai Vultur <mihaivultur7@gmail.com>
- Also include 00-radv-defaults.conf in the list of bundled files.

* Thu Dec 16 2021 Mihai Vultur <mihaivultur7@gmail.com>
- Adjustments after dri-drivers deprecation in mesa 22

* Tue Jun 15 2021 Mihai Vultur <xanto@egaming.ro>
- Partially revert the modifications done in Apr 11:
- Regenerate vulkan-devel package but with no files
- This provides a lean upgrade path

* Wed May 05 2021 Mihai Vultur <xanto@egaming.ro>
- After https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/10554
- also consider i830_dri.so

* Sun Apr 11 2021 Mihai Vultur <xanto@egaming.ro>
- Don't generate a separate vulkan-devel package anymore
- Since upstream commit:
-    commit 5e6db1916860ec217eac60903e0a9d10189d1c53
-    Author: Chad Versace <chad@kiwitree.net>
-    Message:
-       anv: Remove vkCreateDmaBufINTEL (v4)

* Fri Mar 26 2021 Mihai Vultur <xanto@egaming.ro>
- Set vulkan-layers=device-select,overlay since upstream commit 54fe5b04

* Fri Dec 11 2020 Mihai Vultur <xanto@egaming.ro>
- Set osmesa=true since upstream commit ee802372180a2b4460cc7abb53438e45c6b6f1e4 

* Wed Nov 25 2020 Mihai Vultur <xanto@egaming.ro>
- meson: __meson_auto_features default to disabled
- Issue: https://gitlab.freedesktop.org/mesa/mesa/-/issues/3873

* Mon Nov 23 2020 Mihai Vultur <xanto@egaming.ro>
- meson: drop deprecated EGL platform build options.
- Consequence of MR: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/5844

* Mon Apr 20 2020 Mihai Vultur <xanto@egaming.ro>
- Enable vulkan-device-select-layer.

* Sun Feb 09 2020 Mihai Vultur <xanto@egaming.ro>
- Enable zink.

* Sat Feb 08 2020 Mikhail Gavrilov <mikhail.v.gavrilov@gmail.com>
- Prevent radeonsi crashing when compiled with GCC10 on Rawhide.

* Thu Jan 23 2020 Tom Stellard <tstellar@redhat.com>
- Link against libclang-cpp.so
- https://fedoraproject.org/wiki/Changes/Stop-Shipping-Individual-Component-Libraries-In-clang-lib-Package

* Sat Dec 14 2019 Mihai Vultur <xanto@egaming.ro>
- new mesa-overlay-control.py script added to the install list

* Sun Nov 03 2019 Peter Robinson <pbrobinson@gmail.com>
- adjust mesa-khr-devel requires now provided by libglvnd

* Sun Oct 06 2019 Mihai Vultur <xanto@egaming.ro>
- Architecture specific builds might run asynchronous.
- This might cause that same package build for x86_64 will be different when
-  built for i686. This is problematic when we want to install multilib packages. 
- Convert the specfile to template and use it to generate the actual script.
- This will prevent the random failues and mismatch between arch versions.

* Sun Sep 08 2019 Mihai Vultur <xanto@egaming.ro>
- Merge the two implementations.

* Sun Jul 07 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.

* Thu Jul 04 2019 Mihai Vultur <xanto@egaming.ro>
- Modified to point to Valve's Radeon ACO compiler patches from https://github.com/daniel-schuermann/mesa.

* Mon Oct 10 2016 Rudolf Kastl <rudolf@redhat.com>
- Synced with Leighs spec.
