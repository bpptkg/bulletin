===========
Get Started
===========

Install OS package requirements: ::

    sudo apt install python3-dev libmysqlclient-dev python3-virtualenv

Install Redis server for Celery broker: ::

    sudo apt install redis-server

Install Memcached for cache server: ::

    sudo apt install memcached

Clone the project from GitLab repository: ::

    git clone https://github.com/bpptkg/bulletin.git

Change directory to bulletin: ::

    cd bulletin

Create Python virtual environment and activate the virtual environment: ::

    virtualenv -p python3 venv
    source venv/bin/activate

Install package requirements: ::

    pip install -r requirements.txt

Create environment variable settings from template: ::

    cp .env.example .env
    vim .env

Edit .env file according to your need. We have included a description in each
variable setting. So, you know which required variable you have to edit. If you
are using Docker container, create .env file from .env.docker.example instead of
.env.example.

Migrate the database: ::

    python manage.py migrate

Run development server: ::

    python manage.py runserver

Run Celery worker: ::

    celery -A bulletin worker -l INFO

Run Celery beat scheduler: ::

    celery -A bulletin beat -l INFO
