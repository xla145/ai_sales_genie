# Module pom.xml Template

**Path**: `modules/{module}/pom.xml`

Every submodule uses Spring Boot as parent and depends on `generic-orm-archetype` + `system-management`.

## Standard Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.11</version>
        <relativePath/>
    </parent>

    <groupId>com.bytefactory.quchiv2</groupId>
    <artifactId>{ArtifactId}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <name>{ArtifactId}</name>
    <description>{中文模块描述}</description>

    <properties>
        <java.version>17</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <mybatis-plus.version>3.5.5</mybatis-plus.version>
        <lombok.version>1.18.42</lombok.version>
        <knife4j.version>4.4.0</knife4j.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Starter Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- 系统管理（提供 @Log 注解、JWT 工具等） -->
        <dependency>
            <groupId>com.bytefactory.quchiv2</groupId>
            <artifactId>system-management</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>

        <!-- Spring Boot Starter Validation -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Spring Boot Starter Security -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>

        <!-- MyBatis Plus -->
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
            <version>${mybatis-plus.version}</version>
        </dependency>

        <!-- H2 Database（仅测试用） -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <version>2.4.240</version>
            <scope>runtime</scope>
        </dependency>

        <!-- Knife4j OpenAPI -->
        <dependency>
            <groupId>com.github.xiaoymin</groupId>
            <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
            <version>${knife4j.version}</version>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>${lombok.version}</version>
            <scope>provided</scope>
        </dependency>

        <!-- Spring Boot Starter Test -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>

        <!-- ORM 实体层（共享 Entity + Mapper） -->
        <dependency>
            <groupId>com.bytefactory.quchiv2</groupId>
            <artifactId>generic-orm-archetype</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>

        <!-- 如果需要文件上传，取消注释 -->
        <!--
        <dependency>
            <groupId>com.bytefactory.quchiv2</groupId>
            <artifactId>file-upload</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>
        -->
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                    <encoding>UTF-8</encoding>
                </configuration>
            </plugin>
        </plugins>
    </build>

    <distributionManagement>
        <snapshotRepository>
            <id>bytefactory-maven</id>
            <name>Bytefactory Snapshot Repository</name>
            <url>https://maven.bytebroad.com/repository/maven-snapshots/</url>
        </snapshotRepository>
    </distributionManagement>
</project>
```

## Artifact Naming Convention

| Module folder | artifactId | description |
|---------------|------------|-------------|
| `announcement` | `Announcement` | 公告管理模块 |
| `user-feedback` | `UserFeedback` | 用户反馈模块 |
| `computing-management` | `ComputingManagement` | 算力管理模块 |

Rule: artifactId = PascalCase of the module name.

## Root pom.xml Registration

After creating the module pom.xml, also update the **root** `pom.xml`:

1. **In `<modules>` section**:
```xml
<module>modules/{module-folder-name}</module>
```

2. **In `<dependencyManagement><dependencies>` section**:
```xml
<dependency>
    <groupId>com.bytefactory.quchiv2</groupId>
    <artifactId>{ArtifactId}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</dependency>
```
