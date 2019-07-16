Name:       example
Version:	1.0.0
Release:	1%{?dist}
Summary:	This is a simple example to test copr

Group:		Applications/File
License:	GPLv2+
URL:		http://github.com/blog-tutorial-make-srpm
Source0:	%{name}-%{version}.tar.gz

# simulated dependencies
#BuildRequires:  desktop-file-utils
#BuildRequires:  gtk2-devel gettext

%description
Simple example to demonstrate copr's abilites.


%prep
%setup -q


%build
make %{?_smp_mflags}


%install
install -d %{buildroot}%{_sbindir}
cp -a main %{buildroot}%{_sbindir}/main


%files
%doc

%{_sbindir}/main

%changelog
* Sat Dec 15 2015 clime <clime@redhat.com> 1.0.0-1
- Initial version
