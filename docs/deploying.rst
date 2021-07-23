=========
Deploying
=========

Most of the quick setup and installation of the required package was covered in
the :doc:`Get Started<./get_started>` section. So in this section, we will
continue the deployment steps.

After you have installed all package requirements, Redis, Memcached, setting
.env file, you can do the following.

Install Supervisord: ::

    sudo apt install supervisor

Copy Supervisord config files to ``/etc/supervisor/conf.d/``: ::

    sudo cp conf/supervisor/*.conf /etc/supervisor/conf.d/

Edit the config files ``bulletin.conf``, ``bulletin_celery.conf``, and
``bulletin_celerybeat.conf`` according to your needs, particularly the path to
the bulletin project directory.

Make a directory to store runtime logs: ::

    sudo mkdir -p /var/log/bulletin

Reread and update Supervisord configs: ::

    sudo supervisorctl reread
    sudo supervisorctl update

Check if your services have running: ::

    sudo supervisorctl status

We can now proceed to setup Nginx server.

Install Nginx if you haven't installed yet: ::

    sudo apt install nginx

Copy Nginx config file: ::

    sudo cp conf/nginx/bulletin.conf /etc/nginx/site-available/

Edit ``bulletin.conf`` according to your need. For current version, we use port
``9056`` as convention for our web services.

Enable the site: ::

    sudo ln -s /etc/nginx/site-available/bulletin.conf /etc/nginx/site-enabled/bulletin.conf

Finally, reload Nginx configuration: ::

    sudo systemctl reload nginx

Test if our web services have running. For example: ::

    curl -v 'http://192.168.0.43:9056'

If you see the following response, your web services have successfully deployed:

.. literalinclude:: ./data/index.json
    :language: json
  
