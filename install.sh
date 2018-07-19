#!/bin/bash

LOGPATH=/srv/www/hazyblue.me/logs
VENV_BIN="/home/dmaczka/.virtualenvs/hugo-web-hook/bin"

tmp=$(mktemp -d)
echo $tmp

files=("etc/systemd/system/ssg-backend.service" "etc/systemd/system/ssg-worker.service" "etc/systemd/system/ssg-services.target" "etc/rsyslog.d/ssg-worker.conf")

cp -r etc ${tmp}/
cd ${tmp}

sed -i -e "s|LOGPATH|${LOGPATH}|g"\
    -e "s|USER|${USER}|g"\
    -e "s|VENV_BIN|${VENV_BIN}|g"\
        ${files[*]}

cp ${tmp}/etc/systemd/system/ssg-backend.service /etc/systemd/system/
cp ${tmp}/etc/systemd/system/ssg-worker.service /etc/systemd/system/
cp ${tmp}/etc/systemd/system/ssg-services.target /etc/systemd/system/
cp ${tmp}/etc/rsyslog.d/ssg-worker.conf /etc/rsyslog.d/

rm -rf {$tmp}

systemctl enable ssg-backend.service
systemctl enable ssg-worker.service

systemctl start ssg-services.target
systemctl enable ssg-services.target

systemctl restart rsyslog

