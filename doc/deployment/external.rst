Deployment Quick Guide
======================

This page is intended for systems administrators who are experienced with 
installing web server applications and want to get LImBuS up and running 
quickly.

This guide makes use of the project's :code:`Dockerfile`. If you are unable to 
make use of Docker, then please refer to the full installation guide.

Basic Requirements
------------------

Whilst these instructions have been tried and tested on Debian 10 Buster, Docker
and :code:`systemd` both work on pretty much every Linux distribution.

And of course, a working internet connection.

Setting up Docker
-----------------

If you are looking to set up LImBuS, the easiest way to do this is by using the
:code:`Dockerfile` provided in the repository. As I understand that not
everybody would have used containers before so....

What is a container?
~~~~~~~~~~~~~~~~~~~~

A container is a means of bundling up all of the libraries and runtimes
required by an application in order to run without having to worry about
versioning or underlying operating system. You're probably thinking to
yourself "wow, great! I don't have to do a single thing!" - but that sadly
isn't the case. Due to the immutable nature of a container, you're going to
have to set up your configuration beforehand - so a bit of work is required on
your end in order to get started.

Removing old versions
~~~~~~~~~~~~~~~~~~~~~

First of all, it's always a good idea to remove any old versions of Docker you
may have installed:

::

 sudo apt docker docker-engine docker.io containerd runc

There's no need to worry if :code:`apt` states that none of the above packages
are installed as this is just a precautionary step.

Setting up the official Docker repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First of all, run a quick :code:`apt update` to ensure that Debian's
repositories are updated:

::

  sudo apt update

Once that has completed, install the following packages - as so we can use a
repository securely over HTTPS:

::

 sudo apt install \
   apt-transport-https \
   ca-certificates \
   curl \
   gnupg-agent \
   software-properties-common

Depending on your internet connection, this may take a couple seconds to
complete. Once it has, add the GPG of the Docker project:

::

 curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -

Now ensure that the key is correct:

::

  sudo apt-key fingerprint 0EBFCD88

Now set up the Docker repository by running:

::

  sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

Once that has complete, update your package index again:

::

  sudo apt update

And now install Docker:

::

  sudo apt install docker-ce \
   docker-ce-cli \
   containerd.io \
   docker-compose

And now add your user to the docker-group (replacing :code:`<your_user>` with your
user information:

::

  sudo usermod -aG docker <your_user>



Getting LImBuS
--------------

When it comes to getting LImBuS, there are two options available to you:


Download from GitHub
~~~~~~~~~~~~~~~~~~~~

Simply download your required release from 
https://github.com/AberystwythSystemsBiology/limbus/releases and extract the
files to whichever directory you wish.

Version Control (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To simplify the upgrade process, we  **strongly recommend** that you retrieve 
LImBuS using version control. 

To get started, install :code:`git` via the official Debain repositories:
::

  sudo apt install git

Every release of LImBuS is staged as a branch. You don't really need to know 
what this is, but it means that an upgrade is only a couple of commands away 
once you get things up and running.

To retrieve the codebase from the git repository, use the following command - replacing :code:`<your_branch>` with whatever staged release you desire:
::

 git clone -b <your_branch> https://www.github.com/AbersystwythSystemsBiology/limbus
 
For example, if you would like to try out the development branch for testing 
purposes - you would simply enter:
::

  git clone -b dev https://www.github.com/AbersystwythSystemsBiology/limbus
  
And :code:`git` will retrieve that branch for you.

.. note::
   Please ensure that you only download LImBuS from an official source.
   
Setting up your environment
---------------------------

Now it's time to set up your environment. This is done by through the use of a
:code:`dotenv` file.

In the root directory of the project, you can find a :code:`.env.sample` file. It's strongly recommended that you use this as a starting point:

::

  cp .env.sample .env

Inside of this file you will find a number of environment variables:

* :code:`FLASK_CONFIG=` A choice between :code:`deployment` and :code:`production`. :code:`production` disables debugging and stops SQLAlchemy spamming the console.
* :code:`POSTGRES_USER=` The username of your PostgreSQL user. If you are using the :code:`docker-compose` file then this will be used within the :code:`db` container.
* :code:`POSTGRES_PASSWORD=` The password of your PostgreSQL user. If you are using the :code:`docker-compose` file then this will be used within the :code:`db` container.
* :code:`POSTGRES_HOST=` The database host address of your PostgreSQL server. If you are deploying the project through :code:`docker-compose` then ensure that the name matches what is found within the :code:`docker-compose.yml` file (this is usually :code:`db`).
* :code:`POSTGRES_DB=` The database name for of your PostgreSQL server. If you are deploying the project through :code:`docker-compose` then ensure that the name matches what is found within the :code:`docker-compose.yml` file (this is usually :code:`limbus`).
* :code:`SECRET_KEY=` A secret key to protect you against XSS. Please change this.
* :code:`WTF_CSRF_SECRET_KEY=` A secret key to protect forms against XSS. Please change this.
* :code:`DOCUMENT_DIRECTORY=` Where you want your encrypted document store to be located. If you are using the :code:`docker-compose` file, then please ensure that you mount your location appropriately.
* :code:`TEMPLATES_DIRECTORY=` Where you want your templates store to be located. If you are using the :code:`docker-compose` file, then please ensure that you mount your location appropriately.
* :code:`DEBUG=` If you require debug information. In most deployments this should be set to False.
* :code:`DOID_PATH=` Where you want your DOID file to be located. If you are using the :code:`docker-compose` file, then please ensure that you mount your location appropriately.


.. note::
   Please ensure that all secret keys and passwords are secure.


Do it for me
------------

No.