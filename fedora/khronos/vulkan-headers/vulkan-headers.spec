%global build_repo https://github.com/KhronosGroup/Vulkan-Headers

%global latest_data %(git ls-remote %{build_repo} | grep 'refs/tags/v' | sort -Vrk 2 | head -1)
%global numeric_ver %(echo %{latest_data} | grep -oP 'v.*' | grep -oP '[0-9.]+')
%global commit_date %(date +"%Y%m%d")
%global rel_build %{commit_date}%{?dist}

%global __python %{__python3}
Name:           vulkan-headers
Version:        %{numeric_ver}
Release:        %{rel_build}
Summary:        Vulkan Header files and API registry

License:        ASL 2.0
URL:            %{build_repo}
Source0:        %url/archive/v%{numeric_ver}.tar.gz#/Vulkan-Headers-%{numeric_ver}.tar.gz

BuildRequires:  cmake3
BuildArch:      noarch       

%description
Vulkan Header files and API registry

%prep
%autosetup -n Vulkan-Headers-%{version}


%build
%cmake3 -DCMAKE_INSTALL_LIBDIR=%{_libdir} .
%cmake3_build


%install
%cmake3_install


%files
%license LICENSE.txt
%doc README.md
%{_includedir}/vulkan/
%{_includedir}/vk_video/
%dir %{_datadir}/vulkan/
%{_datadir}/vulkan/registry/


%changelog
* Sat Jul 17 2021 Mihai Vultur <xanto@egaming.ro>
- Include vk_video folder

* Tue Jul 16 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.

* Thu Apr 18 2019 Dave Airlie <airlied@redhat.com> - 1.1.106.0-1
- Update to 1.1.106.0 headers

* Wed Mar 06 2019 Dave Airlie <airlied@redhat.com> - 1.1.101.0-1
- Update to 1.1.101.0 headers

* Wed Feb 13 2019 Dave Airlie <airlied@redhat.com> - 1.1.97.0-1
- Update to 1.1.97.0 headers

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.92.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 03 2018 Dave Airlie <airlied@redhat.com> - 1.1.92.0-1
- Update to 1.1.92.0

* Sat Oct 20 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.85.0-1
- Update to 1.1.85.0

* Tue Aug 07 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.82.0-1
- Update to 1.1.82.0

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.77.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 22 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-1
- Initial package
