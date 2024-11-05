FROM jenkins/jenkins:lts

# 运行时环境变量
ENV JAVA_OPTS=-Djenkins.install.runSetupWizard=false

# 安装任何额外的依赖
# 你可以在这里添加任何必要的安装命令，比如安装插件或其他工具
# RUN apt-get update && apt-get install -y somepackage

# 设置工作目录，如果有必要的话
WORKDIR /var/jenkins_home
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt

RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt

# 暴露端口
EXPOSE 8080
EXPOSE 50000

environment:
    - JAVA_OPTS=-Djenkins.install.runSetupWizard=false  # 禁用设置向导
    - JENKINS_USER=admin  # 设置管理员用户名
    - JENKINS_PASS=admin123  # 设置管理员密码    environment:
        - JAVA_OPTS=-Djenkins.install.runSetupWizard=false  # 禁用设置向导
        - JENKINS_USER=admin  # 设置管理员用户名
        - JENKINS_PASS=admin123  # 设置管理员密码

# 设置默认的启动命令（默认 Jenkins 镜像已经有这个命令）
CMD ["java", "-jar", "/usr/share/jenkins/jenkins.war"]



# 使用官方的 Jenkins LTS 镜像
FROM jenkins/jenkins:lts

# 运行时环境配置
USER root

# 禁用设置向导并预先安装一些常用的 Jenkins 插件
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false" 

# 复制初始化 Groovy 脚本，用于自动创建管理员用户
COPY init-admin-user.groovy /usr/share/jenkins/ref/init.groovy.d/

# 安装 Jenkins 插件
RUN /usr/local/bin/install-plugins.sh \
    git \
    docker-workflow \
    blueocean \
    workflow-aggregator \
    credentials-binding \
    pipeline-stage-view \
    ssh-agent \
    timestamper \
    mailer \
    workflow-job \
    configuration-as-code \
    job-dsl

# 恢复为 jenkins 用户
USER jenkins
