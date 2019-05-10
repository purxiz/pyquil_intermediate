#### PyQuil Intermediate

PyQuil HTTPs job queueing server
Authors: Nikolai Norona, Auguste Hirth

Composed of three main components: 
1. A job queueing server in node, daemonized by pm2
2. A job storage database in mongodb, daemonized with system
3. A job processor python script (with pyquil), run periodically with crontab

#### Setup

1. Clone Repo to directory of your choice
2. 
```
cd node_server
npm install
```

