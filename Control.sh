#!/bin/bash

dir=$(cd $(dirname $0); pwd)
log_dir=${dir}/src/logs
[ -d $log_dir ] || mkdir $log_dir
procname=$(grep '"ProcessName":' ${dir}/src/config.py | awk '{print $2}' | awk -F \" '{print $2}'|head -1)
pidfile=${log_dir}/${procname}.pid

case $1 in
start)
    if [ -f $pidfile ]; then
        if [[ $(ps aux | grep $(cat $pidfile) | grep -v grep | wc -l) -lt 1 ]]; then
            $(which python) -O ${dir}/src/Product.py &>> ${log_dir}/output.log &
            pid=$!
            echo $pid > $pidfile
            echo "$procname start over."
        fi
    else
        $(which python) -O ${dir}/src/Product.py &>> ${log_dir}/output.log &
        pid=$!
        echo $pid > $pidfile
        echo "$procname start over."
    fi
    ;;

stop)
    pid=$(cat $pidfile)
    kill $pid
    retval=$?
    rm -f $pidfile
    echo "$procname stop over."
    ;;

status)
    #pid=$(ps aux | grep $procname | grep -vE "grep|worker|Team.Api\." | awk '{print $2}')
    if [ ! -f $pidfile ]; then
        echo -e "\033[39;31m${procname} has stopped.\033[0m"
        exit
    fi
    pid=$(cat $pidfile)
    procnum=$(ps aux | grep -v grep | grep $pid | grep $procname | wc -l)
    if [[ "$procnum" != "1" ]]; then
        echo -e "\033[39;31m异常，pid文件与系统pid数量不相等。\033[0m"
        echo -e "\033[39;34m  pid数量：${procnum}\033[0m"
        echo -e "\033[39;34m  pid文件：${pid}($pidfile)\033[0m"
    else
        echo -e "\033[39;33m${procname}\033[0m":
        echo "  pid: $pid"
        echo -e "  state:" "\033[39;32mrunning\033[0m"
        echo -e "  process start time:" "\033[39;32m$(ps -eO lstart | grep $pid | grep $procname | grep -vE "worker|grep|Team.Api\." | awk '{print $6"-"$3"-"$4,$5}')\033[0m"
        echo -e "  process running time:" "\033[39;32m$(ps -eO etime| grep $pid | grep $procname | grep -vE "worker|grep|Team.Api\." | awk '{print $2}')\033[0m"
    fi
    ;;

restart)
    sh $0 stop
    sh $0 start
    ;;

*)
    sh $0 start
    ;;
esac
