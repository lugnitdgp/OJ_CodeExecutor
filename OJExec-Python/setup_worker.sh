#!/bin/sh
cp .env.example .env
sudo apt-get update && sudo apt-get install build-essential
sudo apt install default-jre
sudo apt install default-jdk
sudo apt install cmake
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
git submodule init
git submodule update
cd safeexec
cmake .
make
cd ..
mkdir static
pip3 install -r requirements.txt
sudo apt-get install supervisor
sudo apt-get install rpl
rpl path-to-dir $PWD executor.conf
rpl path-to-dir $PWD executorbeat.conf
user=$USER
rpl root-user $user executor.conf
rpl root-user $user executorbeat.conf
sudo cp executor.conf /etc/supervisor/conf.d/executor.conf
sudo cp executorbeat.conf /etc/supervisor/conf.d/executorbeat.conf
sudo touch /var/log/executor.log
sudo touch /var/log/executorbeat.log
sudo systemctl stop supervisor.service
sudo supervisord -c /etc/supervisor/supervisord.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart executor

