#
# Conditional build:
%bcond_without	tests		# build without tests

%define	pkgname	redis
Summary:	A Ruby client that tries to match Redis' API one-to-one
Name:		ruby-%{pkgname}
Version:	5.4.1
Release:	2
License:	MIT
Group:		Development/Languages
Source0:	http://rubygems.org/downloads/%{pkgname}-%{version}.gem
# Source0-md5:	0104a574036021f2b86a343e4ea59ca7
URL:		http://github.com/redis/redis-rb
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.665
BuildRequires:	ruby-devel
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A Ruby client that tries to match Redis' API one-to-one.

%package rdoc
Summary:	HTML documentation for %{name}
Summary(pl.UTF-8):	Dokumentacja w formacie HTML dla %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description rdoc
HTML documentation for %{name}.

%description rdoc -l pl.UTF-8
Dokumentacja w formacie HTML dla %{name}.

%package ri
Summary:	ri documentation for %{name}
Summary(pl.UTF-8):	Dokumentacja w formacie ri dla %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description ri
ri documentation for %{name}.

%description ri -l pl.UTF-8
Dokumentacji w formacie ri dla %{name}.

%prep
%setup -q -n %{pkgname}-%{version}

%build
%__gem_helper spec

rdoc --ri --op ri lib
rdoc --op rdoc lib
rm ri/created.rid
rm ri/cache.ri

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{ruby_vendorlibdir},%{ruby_specdir},%{ruby_ridir},%{ruby_rdocdir},%{_examplesdir}/%{name}-%{version}}

cp -a lib/* $RPM_BUILD_ROOT%{ruby_vendorlibdir}
cp -p %{pkgname}-%{version}.gemspec $RPM_BUILD_ROOT%{ruby_specdir}
cp -a ri/* $RPM_BUILD_ROOT%{ruby_ridir}
cp -a rdoc $RPM_BUILD_ROOT%{ruby_rdocdir}/%{name}-%{version}

# Examples
if [ -d examples ]; then
	cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
	find $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version} -type f -name "*.rb" | xargs sed -i -e '1s,/usr/bin/env ruby,%{__ruby},'
	# Fix other possible shebangs
	find $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version} -type f | xargs grep -l "/usr/bin/env ruby" | xargs -r sed -i -e '1s,/usr/bin/env ruby,%{__ruby},'
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md
%{ruby_vendorlibdir}/redis
%{ruby_vendorlibdir}/redis.rb
%{ruby_specdir}/%{pkgname}-%{version}.gemspec
%{_examplesdir}/%{name}-%{version}

%files rdoc
%defattr(644,root,root,755)
%{ruby_rdocdir}/%{name}-%{version}

%files ri
%defattr(644,root,root,755)
%{ruby_ridir}/Redis
