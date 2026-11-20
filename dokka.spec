Name:		dokka
Version:	2.3.0
Release:	1
Summary:	Dokka documentation engine and Gradle plugin
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/Kotlin/dokka
# Tag v2.3.0 (c6cd48aeb43513a45dfe81bcbc8e4a59972fd627).
# Upstream builds with Gradle. This package compiles dokka-core and
# dokka-gradle-plugin with kotlinc 2.0.21 against cooker Gradle 9.9.1.
# KotlinJvmAndroidCompilation is omitted from the published Kotlin
# Gradle plugin 2.4.21 jar, so those call sites are compiled out.
# com.android.Version comes from the AOSP class already used by
# dependency-analysis, loaded from version.properties.
Source0:	dokka-%{version}.tar.gz
%{!?dokka_javadir:%global dokka_javadir %{_javadir}}
%{!?dokka_gradle_home:%global dokka_gradle_home /usr/share/gradle}

BuildArch:	noarch
BuildRequires:	java-21-openjdk-devel
BuildRequires:	kotlin = 2.0.21
BuildRequires:	kotlin-libs = 2.0.21
BuildRequires:	python
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	gradle = 9.9.1
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-databind) = 2.23.0
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-core) = 2.23.0
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-annotations) = 2.23
BuildRequires:	mvn(com.fasterxml.jackson.dataformat:jackson-dataformat-xml) = 2.23.0
BuildRequires:	mvn(com.fasterxml.jackson.module:jackson-module-kotlin) = 2.23.0
BuildRequires:	mvn(org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm) = 1.11.0
BuildRequires:	mvn(org.jetbrains.kotlinx:kotlinx-serialization-core) = 1.13.0
BuildRequires:	mvn(org.jetbrains.kotlinx:kotlinx-serialization-json) = 1.13.0
BuildRequires:	mvn(org.jetbrains.kotlin:kotlin-gradle-plugin) = 2.4.21
BuildRequires:	mvn(org.jetbrains.kotlin:kotlin-gradle-plugin-api) = 2.4.21
BuildRequires:	mvn(org.jetbrains.kotlin:kotlin-tooling-core) = 2.4.21
BuildRequires:	mvn(com.android.tools.build:gradle-api) = 9.0.0
BuildRequires:	mvn(com.android.tools.build:builder-model) = 9.0.0
BuildRequires:	mvn(com.android.tools:annotations) = 32.0.0
BuildRequires:	mvn(org.jetbrains:annotations)
BuildRequires:	mvn(javax.inject:javax.inject)
Requires:	mvn(com.fasterxml.jackson.core:jackson-databind) = 2.23.0
Requires:	mvn(com.fasterxml.jackson.core:jackson-core) = 2.23.0
Requires:	mvn(com.fasterxml.jackson.core:jackson-annotations) = 2.23
Requires:	mvn(com.fasterxml.jackson.dataformat:jackson-dataformat-xml) = 2.23.0
Requires:	mvn(com.fasterxml.jackson.module:jackson-module-kotlin) = 2.23.0
Requires:	mvn(org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm) = 1.11.0
Requires:	mvn(org.jetbrains.kotlin:kotlin-stdlib)
Requires:	mvn(org.jetbrains.kotlin:kotlin-reflect)

%description
org.jetbrains.dokka:dokka-core %{version}.
DokkaConfigurationImpl records a module name and version and writes
that configuration as JSON.

%package gradle-plugin
Summary:	Gradle plugin for the Dokka documentation engine
Group:		Development/Java
Requires:	dokka = %{EVRD}
Requires:	gradle = 9.9.1
Requires:	mvn(org.jetbrains.kotlinx:kotlinx-serialization-json) = 1.13.0
Requires:	mvn(org.jetbrains.kotlinx:kotlinx-serialization-core) = 1.13.0
Requires:	mvn(javax.inject:javax.inject) = 1.0.5
Requires:	mvn(org.jetbrains.kotlin:kotlin-stdlib)
Requires:	mvn(org.jetbrains.kotlin:kotlin-reflect)

%description gradle-plugin
org.jetbrains.dokka:dokka-gradle-plugin %{version}.
DokkaPlugin registers the dokka HTML publication on a Gradle project.
The engine version on DokkaExtension is %{version}.

%prep
%autosetup -n dokka-%{version}
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
test -s LICENSE.txt
test -s core/kotlin/org/jetbrains/dokka/DokkaGenerator.kt
test -s core/resources/META-INF/dokka/dokka-version.properties
grep -F -q '${dokkaVersion}' core/resources/META-INF/dokka/dokka-version.properties
test -s plugin/main/kotlin/DokkaPlugin.kt
test -s plugin/classicMain/kotlin/DokkaClassicPlugin.kt
test -s agp/Version.java
grep -F -qx 'buildVersion=9.0.0' agp/version.properties
test -s tools/patch_plugin.py
test -s tools/classpath.sh
test -s build.sh
test -s check.sh
test -s check/DokkaCoreCheck.kt
test -s check/DokkaPluginCheck.kt

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
export JAVADIR=%{dokka_javadir}
export GRADLE_HOME=%{dokka_gradle_home}
bash ./build.sh
test -s dokka-core.jar
test -s dokka-gradle-plugin.jar

cat > dokka-core.pom << END
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.jetbrains.dokka</groupId>
  <artifactId>dokka-core</artifactId>
  <version>%{version}</version>
  <name>Dokka Core</name>
  <description>Dokka documentation model and configuration.</description>
  <url>https://github.com/Kotlin/dokka</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.23.0</version>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-core</artifactId>
      <version>2.23.0</version>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-annotations</artifactId>
      <version>2.23</version>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.dataformat</groupId>
      <artifactId>jackson-dataformat-xml</artifactId>
      <version>2.23.0</version>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.module</groupId>
      <artifactId>jackson-module-kotlin</artifactId>
      <version>2.23.0</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlinx</groupId>
      <artifactId>kotlinx-coroutines-core-jvm</artifactId>
      <version>1.11.0</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlin</groupId>
      <artifactId>kotlin-stdlib</artifactId>
      <version>2.0.21</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlin</groupId>
      <artifactId>kotlin-reflect</artifactId>
      <version>2.0.21</version>
    </dependency>
  </dependencies>
</project>
END

cat > dokka-gradle-plugin.pom << END
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.jetbrains.dokka</groupId>
  <artifactId>dokka-gradle-plugin</artifactId>
  <version>%{version}</version>
  <name>Dokka Gradle Plugin</name>
  <description>Gradle plugin for the Dokka documentation engine.</description>
  <url>https://github.com/Kotlin/dokka</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.jetbrains.dokka</groupId>
      <artifactId>dokka-core</artifactId>
      <version>%{version}</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlinx</groupId>
      <artifactId>kotlinx-serialization-json</artifactId>
      <version>1.13.0</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlinx</groupId>
      <artifactId>kotlinx-serialization-core</artifactId>
      <version>1.13.0</version>
    </dependency>
    <dependency>
      <groupId>javax.inject</groupId>
      <artifactId>javax.inject</artifactId>
      <version>1.0.5</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlin</groupId>
      <artifactId>kotlin-stdlib</artifactId>
      <version>2.0.21</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlin</groupId>
      <artifactId>kotlin-reflect</artifactId>
      <version>2.0.21</version>
    </dependency>
  </dependencies>
</project>
END

%install
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
mkdir -p %{buildroot}
sysjar install --buildroot %{buildroot} \
	--artifact dokka-core.pom:dokka-core.jar \
	--file-name dokka-core \
	--filelist core.list
sysjar install --buildroot %{buildroot} \
	--artifact dokka-gradle-plugin.pom:dokka-gradle-plugin.jar \
	--file-name dokka-gradle-plugin \
	--filelist plugin.list
grep -F -q '%%dir /usr/share/sysjar/index/org.jetbrains.dokka' core.list
grep -F -q '%%dir /usr/share/sysjar/index/org.jetbrains.dokka' plugin.list
grep -v -F '%%dir /usr/share/sysjar/index/org.jetbrains.dokka' plugin.list > plugin.files
if grep -F -q '%%dir /usr/share/sysjar/index/org.jetbrains.dokka' plugin.files; then
	exit 1
fi
/bin/cp core.list core.files
test -s %{buildroot}%{_javadir}/dokka-core.jar
test -s %{buildroot}%{_javadir}/dokka-gradle-plugin.jar

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
export JAVADIR=%{dokka_javadir}
export GRADLE_HOME=%{dokka_gradle_home}
bash ./check.sh %{buildroot}%{_javadir}/dokka-core.jar %{buildroot}%{_javadir}/dokka-gradle-plugin.jar

%files -f core.files
%license LICENSE.txt
%doc NOTICE.txt

%files gradle-plugin -f plugin.files
%license LICENSE.txt
%doc NOTICE.txt
