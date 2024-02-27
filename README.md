# My-Poll-App
This project aims to build a social decision app. 


My Poll App is a web application based on voting theory (Approval, Borda, Simpson, ...) , to help you to make a social decision easier.
This project was presented to defend my Bachelor's degree thesis in Computer Engineering at [UniFi](https://www.unifi.it/), and is the result of an internship carried out from August 2022 to February 2023 at the [MICC](http://www.micc.unifi.it/) in Florence.


**Overview**

The project folder contains several folders with various files that compose
govern the entire application. A brief overview is explained below:
- my_poll_app: This is the external root folder. It's the contain
tor for the project and we could give it any name. This folder
  contains the entire application.
- accounts: Our project contains two applications within it
  ( or Python package) and this directory is one of them, it is used primarily
useful in managing user movements (registrations, connections,
  access level).
- mbakop_polls: This folder contains the project settings,
  like settings.py and urls.py.
- polls: The second application inside our project and it is the most
  important because it contains all the necessary algorithms within it
  to the functioning of the surveys.
- templates: This contains two folders, accounts and polls, containing
  each all the hmtl files necessary for the front-end.
  The accounts folder contains the html files that users will browse
  at the time of connection, registration, voting.
  The polls folder in turn contains the hmtl files that will be used for the
  poll display (personal area, votes, results).
- venv: This is a folder created bynazionalenv (it is a tool for
  create isolated Python environments) which contains all the executables needed to use the packages our Python project would need.
- db.sqlite3: It is a lightweight SQL database file
  created with SQLite software. It's a database in a file itself and imple
mint a self-contained, complete and highly developed SQL database engine
  reliable.
