## jenkins数据迁移
centos 7.9

### 配置目录
默认在主目录下的.jenkins目录

config.xml 配置信息
jobs 工程项目任务目录, 打包排除builds构建目录
    tar -cvf jobs.tar jobs/ --exclude 'builds'
users 用户账号信息
plugins 插件目录


### 新机部署
拷贝旧机的以下包
jdk-8u171-linux-x64.tar.gz
apache-maven-3.5.2-bin.tar.gz
apache-tomcat-8.5.24.tar.gz
jenkins.war

=>

/data/jdk1.8.0_171
/data/apache-maven-3.5.2
/data/apache-tomcat-8.5.24
/data/apache-tomcat-8.5.24/webapps/jenkins.war

编辑/etc/profile

```sh
export JAVA_HOME=/data/jdk1.8.0_171
export CLASSPATH=.:${JAVA_HOME}/lib
export MAVEN_HOME=/data/apache-maven-3.5.2
export PATH=$PATH:$JAVA_HOME/bin:$MAVEN_HOME/bin
```

将备份的config.xml, jobs, users, plugins拷贝到 /data/jenkins 目录下
拷贝原settings.xml到/data/apache-maven-3.5.2/conf/settings.xml

在主目录下创建软链接
```sh
ln -s /data/jenkins .jenkins
ln -s /data/m2/ .m2
```

启动tomcat即可以原账户密码登录新Jenkins, 且保留原有的job任务, 不过发现git账号信息以及服务器配置信息丢失, 可能还缺配置, 不过因为是新机部署，也是需要重新配置, 所以不影响


