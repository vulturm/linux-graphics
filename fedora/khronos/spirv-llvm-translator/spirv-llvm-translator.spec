%define package_name spirv-llvm-translator
%global build_branch master

%global build_repo https://github.com/KhronosGroup/SPIRV-LLVM-Translator
%global version_file https://raw.githubusercontent.com/KhronosGroup/SPIRV-LLVM-Translator/{}/CMakeLists.txt
%global version_string_regex reg_beg set \(BASE_LLVM_VERSION ([0-9.]+)\) reg_end

%define version_string 14.0.0

%define commit 4ccb1b29bbdd0b37ce369d82fa52f8305c7c032c
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20210907
%global gitrel .%{commit_date}.git%{shortcommit}


Name:           %{package_name}
Version:        %{version_string}
Release:        0.2%{?gitrel}%{?dist}
Summary:        LLVM to SPIRV Translator

License:        NCSA
URL:            %{build_repo}
Source0:        %{build_repo}/archive/%{commit}.tar.gz#/SPIRV-LLVM-Translator-%{commit}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  llvm-devel

%description
Khronos LLVM to SPIRV Translator. This is a library
to be used by Mesa for OpenCL support. It translate
LLVM IR to Khronos SPIR-V. It also includes a
standalone tool used for building libclc.

%package devel
Summary: Development files for LLVM to SPIRV Translator
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains libraries and header files for
developing against %{name}

%package tools
Summary: Standalone llvm to spirv translator tool
Requires: %{name}%{?_isa} = %{version}-%{release}

%description tools
This package contains the standalone llvm to spirv tool.

%prep
#force downloading the project, seems that copr dist-cache is poisoned with bogus archive
curl -Lo %{_sourcedir}/SPIRV-LLVM-Translator-%{commit}.tar.gz %{build_repo}/archive/%{commit}.tar.gz#/SPIRV-LLVM-Translator-%{commit}.tar.gz
%autosetup -n SPIRV-LLVM-Translator-%{commit}

%build
%cmake -B "%{_vpath_builddir}" \
       -GNinja \
       -DLLVM_BUILD_TOOLS=ON \
       -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DCMAKE_INSTALL_RPATH:BOOL=";" 

%ninja_build -C "%{_vpath_builddir}"

%install
%ninja_install -C "%{_vpath_builddir}"

%files
%doc README.md
%{_libdir}/libLLVMSPIRVLib.so.*

%files tools
%{_bindir}/llvm-spirv

%files devel
%dir %{_includedir}/LLVMSPIRVLib/
%{_includedir}/LLVMSPIRVLib/*
%{_libdir}/libLLVMSPIRVLib.so
%{_libdir}/pkgconfig/LLVMSPIRVLib.pc

%changelog

