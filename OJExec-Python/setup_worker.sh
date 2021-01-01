#!/bin/sh
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
sudo supervisord
