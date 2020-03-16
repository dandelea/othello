#!/usr/bin/env bash
trap 'exit 0' SIGTERM
while true
do 
    python worker.py reset
    echo '''
* * * * * /usr/local/bin/python /app/worker.py ai >> /app/log
* * * * * (sleep 10; /usr/local/bin/python /app/worker.py ai >> /app/log)
* * * * * (sleep 20; /usr/local/bin/python /app/worker.py ai >> /app/log)
* * * * * (sleep 30; /usr/local/bin/python /app/worker.py ai >> /app/log)
* * * * * (sleep 40; /usr/local/bin/python /app/worker.py ai >> /app/log)
* * * * * (sleep 50; /usr/local/bin/python /app/worker.py ai >> /app/log)
* * * * * /usr/local/bin/python /app/worker.py purge >> /app/log
    ''' > crontab.script
    touch /app/log
    crontab crontab.script
    service cron restart
    tail -f /app/log
done

