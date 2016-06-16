#
# Conditional build:
%bcond_without	tests		# build without tests

%define pkgname redis
Summary:	A Ruby client library for Redis
Name:		ruby-%{pkgname}
Version:	3.2.2
Release:	1
License:	MIT
Group:		Development/Languages
Source0:	https://rubygems.org/gems/%{pkgname}-%{version}.gem
# Source0-md5:	859aed903d225d98ed2476f29bfe1ad3
Source1:	redis-test.conf
Patch0:		rubygem-redis-3.2.2-minitest.patch
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

%build
# write .gemspec
%__gem_helper spec

%if %{with tests}
# Install our test.conf file. Upstream dynamically generates this with Rake.
# To avoid using rake, we use a static file.
cp -p %{SOURCE1} test/test.conf

## Running Redis server, which does not support IPv6, nc cannot connect to it using localhost.
## https://bugzilla.redhat.com/show_bug.cgi?id=978964
## Use 127.0.0.1 instead or else it hangs while testing.
## https://bugzilla.redhat.com/show_bug.cgi?id=978284#c2
sed -i "s/localhost/127.0.0.1/" test/publish_subscribe_test.rb

## Start a testing redis server instance
/usr/sbin/redis-server test/test.conf
sleep 1
kill -0 `cat test/db/redis.pid`
tail test/db/stdout

## Set locale because two tests fail in mock.
## https://github.com/redis/redis-rb/issues/345
export LC_ALL=en_US.UTF-8

## Problems continue to surface with Minitest 5, so I've asked upstream how
## they want to proceed. https://github.com/redis/redis-rb/issues/487
ruby -Ilib -e 'Dir.glob "./test/**/*_test.rb", &method(:require)'

## Kill redis-server
kill -INT `cat test/db/redis.pid`
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