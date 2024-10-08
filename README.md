# Message-Broker-Using-Postgres

## Introduction

This is a simple message broker system that uses Postgres as the message broker. The system is composed of two services, the producer and the consumer. The producer sends messages to the message broker and the consumer reads the messages from the message broker. The producer and the consumer are implemented in Python and the message broker is implemented in Postgres.

![Flow](docs/flow.png)




## Setting up an Cron Job in Ubuntu

Ubuntu Docker

Install ubuntu docker image
```bash
docker pull ubuntu
```

Run the ubuntu docker image
```bash
docker run -it ubuntu bash
```

### Install the cron package
```bash
apt-get install cron
```

Download the script

```bash
wget -O myscript https://raw.githubusercontent.com/MercyShark/Message-Broker-Using-Postgres/main/cronjobscript.sh
```

Add the Environment Variables to the script
```bash
nano myscript.sh
```

Permission to execute the script
```bash
chmod +x myscript.sh
```

Add the script to the crontab
```bash
crontab -e
```

Add the following line to the crontab to run the script every minute
```bash
* * * * * /myscript.sh
```

```bash
service cron restart
service cron status
```



