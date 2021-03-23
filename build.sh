#!/bin/sh
BUILDER_VERSION = "0.1"

#  Installing redis
# Downloading redis
redisurl="http://download.redis.io/redis-stable.tar.gz"
# Installing curl
sudo apt install curl
curl -s -o redis-stable.tar.gz $redisurl
sudo su root
# Configuring Redis
mkdir -p /usr/local/lib/
chmod a+w /usr/local/lib/
tar -C /usr/local/lib/ -xzf redis-stable.tar.gz
rm redis-stable.tar.gz
cd /usr/local/lib/redis-stable/
make && make install
# Getting redis version to verify installtion
redis-cli --version
mkdir -p /etc/redis/
touch /etc/redis/6379.conf

printf "# /etc/redis/6379.conf

port              6379
daemonize         yes
save              60 1
bind              127.0.0.1
tcp-keepalive     300
dbfilename        dump.rdb
dir               ./
rdbcompression    yes" >> /etc/redis/6379.conf

#  Installing python packages
pip install redis