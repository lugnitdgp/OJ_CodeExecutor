#!/bin/sh
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
sudo rpl path-to-dir $PWD executor.conf
sudo rpl path-to-dir $PWD executorbeat.conf
# user=$USER
user=ubuntu # for default root
sudo rpl root-user $user executor.conf
sudo rpl root-user $user executorbeat.conf
sudo cp executor.conf /etc/supervisor/conf.d/executor.conf
sudo cp executorbeat.conf /etc/supervisor/conf.d/executorbeat.conf
sudo touch /var/log/executor.log
sudo touch /var/log/executorbeat.log
sudo systemctl stop supervisor.service
sudo supervisord -c /etc/supervisor/supervisord.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart executor
