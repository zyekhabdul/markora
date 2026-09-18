Name:           markora
Version:        1.1.0
Release:        1%{?dist}
Summary:        Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI

License:        MIT
URL:            https://github.com/zyekhabdul/markora
Source0:        https://github.com/zyekhabdul/markora/archive/refs/tags/v%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3

%description
Markora is an ultra-lightweight, zero-dependency Markdown notebook,
task manager, and QuickNotes TUI designed for terminal power users.
Includes alias: td.

%prep
%autosetup

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md
%{_bindir}/markora
%{_bindir}/td
%{python3_sitelib}/markora/
%{python3_sitelib}/markora-*.egg-info/

%changelog
* Fri Sep 18 2026 zyekhabdul <zyekhabdulqadirjailani@gmail.com> - 1.1.0-1
- Bump to 1.1.0, prune legacy mo/todo aliases, streamline CLI commands

* Sat Sep 05 2026 zyekhabdul <zyekhabdulqadirjailani@gmail.com> - 1.0.0-1
- Initial release
