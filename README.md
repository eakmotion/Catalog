# Tournament Results

This project is a part of the Full Stack Web Developer Nanodegree through [Udacity](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

### About
This project is a website that provides a list of items within a variety of categories as well as provide a user registration and authentication system.
Registered users will have the ability to post, edit and delete their own items.

### Requirements

You will need these installed in your computer:
* [Vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/)
* [Google Developer Account](https://console.developers.google.com/)

## Running The Project

1. Clone the repository

2. Navigate to the project directory

3. Create new project on https://console.developers.google.com/

4. Now you should have client Id and secret from Google project. Type ID and Secret to client_secrets.json file

5. Run following command to setup Vagrant.

        > $vagrant up

6. Run following command to login to your Vagrant VM:

        > $vagrant ssh

7. Run following command to change to the shared folder:

        > $cd /vagrant

8. Run following command to setup database schema:

        > $python database_setup.py

        > $python data_seeder.py

9. Run following command to run the project:

        > $python main.py

10. App will start running on configured port.
