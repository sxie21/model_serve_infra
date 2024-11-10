sudo apt update
sudo apt install fontconfig openjdk-17-jre
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]" \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins

sudo systemctl start jenkins
sudo systemctl enable jenkins
sudo systemctl status jenkins


#add jenkins to docker group to run docker commands
sudo usermod -aG ubuntu jenkins

#add jenkins to host user group to manage project files
sudo usermod -aG docker jenkins #add jenkins to docker group to run docker commands

#install wrk for load testing
sudo apt install wrk