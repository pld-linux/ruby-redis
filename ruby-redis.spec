#
# Conditional build:
%bcond_with	tests		# build without tests

%define pkgname redis
Summary:	A Ruby client library for Redis
Name:		ruby-%{pkgname}
Version:	3.3.0
Release:	1
License:	MIT
Group:		Development/Languages
Source0:	https://rubygems.org/gems/%{pkgname}-%{version}.gem
# Source0-md5:	432fa72404066a33ed4189bbf05396c4
Source1:	redis-test.conf
Patch0:		tests-localhost.patch
Patch1:		rubygem-redis-3.2.2-minitest.patch
URL:		https://github.com/redis/redis-rb
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.665
%if %{with tests}
BuildRequires:	redis-server
BuildRequires:	rubygem(minitest)
%endif
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A Ruby client that tries to match Redis' API one-to-one, while still
providing an idiomatic interface. It features thread-safety,
client-side sharding, pipelining, and an obsession for performance.

%package doc
Summary:	Documentation for %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}
BuildArch:	noarch

%description doc
Documentation for %{name}.

%prep
%setup -q -n %{pkgname}-%{version}
#%patch0 -p1
#%patch1 -p1

# Install our test.conf file. Upstream dynamically generates this with Rake.
# To avoid using rake, we use a static file.
cp -p %{SOURCE1} test/test.conf

%build
# write .gemspec
%__gem_helper spec

%if %{with tests}
port=6381

sed -i -e "/^PORT/ s/6381/$port/" test/helper.rb
sed -i -e "/^port/ s/6381/$port/" test/test.conf

## Start a testing redis server instance
/usr/sbin/redis-server test/test.conf
sleep 1
cat test/db/stdout
kill -0 `cat test/db/redis.pid`
## configure kill for redis-server
trap 'kill -INT `cat test/db/redis.pid`' EXIT QUIT INT

## Set locale because two tests fail in mock.
## https://github.com/redis/redis-rb/issues/345
export LC_ALL=en_US.UTF-8

## Problems continue to surface with Minitest 5, so I've asked upstream how
## they want to proceed. https://github.com/redis/redis-rb/issues/487
ruby -Ilib -e 'Dir.glob "./test/**/*_test.rb", &method(:require)'
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{ruby_vendorlibdir},%{ruby_specdir}}
cp -a lib/* $RPM_BUILD_ROOT%{ruby_vendorlibdir}
cp -p %{pkgname}-%{version}.gemspec $RPM_BUILD_ROOT%{ruby_specdir}

# install examples
install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md LICENSE
%{ruby_vendorlibdir}/redis.rb
%{ruby_vendorlibdir}/redis
%{ruby_specdir}/%{pkgname}-%{version}.gemspec
%{_examplesdir}/%{name}-%{version}
