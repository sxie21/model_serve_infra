FROM jenkins/jenkins:lts

USER root

RUN jenkins-plugin-cli --plugins git pipeline pipeline-groovy pipeline-declarative workflow-aggregator docker-workflow blueocean job-dsl

USER jenkins

ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \ 
    JENKINS_USER="admin"  \
    JENKINS_PASS="admin"

COPY init-admin-user.groovy /usr/share/jenkins/ref/init.groovy.d/  

EXPOSE 8080
EXPOSE 50000

CMD ["java", "-jar", "/usr/share/jenkins/jenkins.war"]