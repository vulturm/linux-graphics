%define package_name gamemode

%global build_repo https://github.com/FeralInteractive/gamemode
%define version_string 1.6

%define commit 7515c640c33a45f1d6c43e0e11cb172117803c66
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20200315
%global gitrel .%{commit_date}.git%{shortcommit}

Name:		  %{package_name}
Version:	%{version_string}
Release:	0.1%{?gitrel}%{?dist}
Summary:	Optimize system performance for games on demand
License:	BSD
URL:		  %{build_repo}
Source0:  https://github.com/FeralInteractive/gamemode/archive/%{commit}.tar.gz#/%{package_name}-%{commit}.tar.gz

BuildRequires: gcc
BuildRequires: asciidoc
BuildRequires: meson
BuildRequires: pkgconfig(dbus-1)
BuildRequires: pkgconfig(systemd)
BuildRequires: pkgconfig(libsystemd)
BuildRequires: polkit-devel
BuildRequires: systemd

%description
GameMode is a daemon/lib combo for GNU/Linux that allows games to
request a set of optimizations be temporarily applied to the host OS.
GameMode was designed primarily as a stop-gap solution to problems
with the Intel and AMD CPU "powersave" or "ondemand" governors, but
is now able to launch custom user defined plugins, and is intended
to be expanded further, as there are a wealth of automation tasks
one might want to apply.

%package devel
Summary: Development package for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Files for development with %{name}.

%prep
#force downloading the project, seems that copr dist-cache is poisoned with bogus archive
git clone --recursive %{build_repo} %{_builddir}/%{package_name}-%{commit}

%autosetup -p1 -D -T -n %{package_name}-%{commit}

%build
%meson
%meson_build

%check
%meson_test

%install
%meson_install

%ldconfig_scriptlets

%files
%license LICENSE.txt
%doc	 README.md
%{_bindir}/gamemoded
%{_bindir}/gamemoderun
%{_libexecdir}/cpugovctl
%{_libexecdir}/gpuclockctl
%{_datadir}/polkit-1/actions/com.feralinteractive.GameMode.policy
%{_datadir}/dbus-1/services/com.feralinteractive.GameMode.service
%{_libdir}/libgamemode*.so.*
%{_libdir}/libgamemode*.so
%{_userunitdir}/gamemoded.service
%{_mandir}/man8/gamemoded.8*

%files devel
%{_includedir}/gamemode_client.h
%{_libdir}/pkgconfig/gamemode*.pc


%changelog
* Thu Dec 05 2019 Mihai Vultur <xanto@egaming.ro> - git
- Build git version.

* Sun Jul 21 2019 Christian Kellner <christian@kellner.me> - 1.4-1
- New upstream release (1.4)
- Add dbus-1 dependency, required by the client library.
- Includes a new gamemoderun script to easily invoke gamemode
- Installs another helper tool to control GPU settings (gpuclockctl)

* Tue Apr 16 2019 Adam Williamson <awilliam@redhat.com> - 1.2-4
- Rebuild with Meson fix for #1699099

* Mon Apr  8 2019 Christian Kellner <christian@kellner.me> - 1.2-3
- Ship unversioned .so in main package, because old games require that one.
  Resolves: rhbz#1697460

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jul 23 2018 Christian Kellner <christian@kellner.me> - 1.2-1
- New upstream release
  Resolves: #1607099
- Drop all patches (all upstreamed)

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jun 28 2018 Christian Kellner <christian@kellner.me>  - 1.1-1
- Initial package
  Resolves: #1596293
- Patch to move manpage to section 8
  Upstream commit 28fcb09413bbf95507788024b98b675cbf656f6c
- Patch for dbus auto-activation
  Merged PR https://github.com/FeralInteractive/gamemode/pull/62
- Patch for proper library versioning
  Merged PR https://github.com/FeralInteractive/gamemode/pull/63

