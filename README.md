# cs-messaging-branchintl

## instructions to run this project in your own device

1. clone it `git clone https://github.com/surajiyer26/cs-messaging-branchintl.git` or simply download and extract the zip file
2. ensure that python is installed in your device
3. go to the project directory, create a virtual environment `python -m venv venv`
4. activate the virtual environment `venv\Scripts\activate.bat` (in case of windows)
5. install the dependencies `pip install -r requirements.txt`
6. run `flask --app main.py run`

## features

1. a messaging web application that can respond to incoming queries sent by customers
2. multiple agents can log in at the **same time** and respond to incoming queries
3. work is divided amongst the agents **equally**, queries are assigned to agents with lesser work
4. incoming queries are preprocessed to calculate their **urgency level**
5. **queries are prioritized** on basis of their urgency levels and timestamps
6. a canned message feature that allows agents to quickly respond to enquiries using a set of **pre-configured stock messages**
7. interactive UI by leveraging **websockets**, so that new incoming messages can show up in **real time**

## video demonstration

 [youtube](https://youtu.be/IenwEZX-_pc) 
