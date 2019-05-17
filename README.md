#### PyQuil Intermediate

PyQuil HTTPs job queueing server
Authors: Nikolai Norona, Auguste Hirth, Robert Smith

Composed of three main components: 
1. A job queueing server in node, daemonized by pm2
2. A job storage database in mongodb, daemonized with service
3. A job processor python script (with pyquil), run periodically with crontab

#### Setup

1. Clone Repo to directory of your choice
2. Setup and start server.js as a daemon
```
cd node_server
npm install
npm install pm2 -g
sudo pm2 start server.js
sudo pm2 startup
sudo pm2 save
```
3. Setup and start mongodb
Install mongodb (version 4.0) with official documentation. The following may change with distribution type/version
Start mongodb with:
```
sudo service mongod start
```
4. Prepare Python environment
```
cd job_processor
mkdir venv
python3 -m venv venv/
source venv/bin/activate
pip install flask
pip install pyquil
pip install pymongo
```
Set python script to run periodically, either with the exec_on_engage.sh script, or crontab.

