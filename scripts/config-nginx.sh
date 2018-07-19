#!/bin/bash
set -e

hostname=$1
repo=$2
venv_bin_dir=$3

scripts_dir=`pwd`/scripts
part1=$scripts_dir/nginx_conf_part_1.conf
part2=$scripts_dir/nginx_conf_part_2.conf
    
echo "$venv_bin_dir/python $scripts_dir/write_nginx_conf.py $hostname $repo $part1"
    
sudo $venv_bin_dir/python $scripts_dir/write_nginx_conf.py $hostname $repo $part1
    
sudo service nginx reload
    
sudo ../letsencrypt/letsencrypt-auto certonly -q --webroot -w /usr/share/nginx/html/$repo -d $hostname
    
sudo $venv_bin_dir/python $scripts_dir/write_nginx_conf.py $hostname $repo $part2
    
sudo service nginx restart
