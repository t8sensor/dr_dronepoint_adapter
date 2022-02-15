Adapter for monitoring events stream from server and notify about new alarm objects.
For example, there is test server for receiving notifications.

###Prepare environment

install python 3.8
```
sudo apt install python3.8 python3.8-venv python3.8-dev
```
virtual environment
```
python3.8 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

###Example

main.py contain example of using adapter. Subscriber in a thread receives events, 
others have access to it due a queue. Notifier is a debug tool for sending notification 
to test server. Adapter monitors events and sends notifications, when new object 
obtains alarm category. Expect DR server in `https://127.0.0.1:5082/`, 
set credentials in lines 40-41.

Test server there is in `dr_dronpoint_adapter/dron_test_server.py`.
It is simple flask server for checking notifications from adapter.
Server starts on `http://127.0.0.1:50411/`

start dron server
```
python dr_dronpoint_adapter/dron_test_server.py
```
start adapter
```
python main.py
```
check events on the server `http://127.0.0.1:50411/alarm_list/`

Press `Ctrl-C` for stopping scripts execution.