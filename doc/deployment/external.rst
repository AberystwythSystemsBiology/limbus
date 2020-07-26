Deployment Quick Guide
======================

This page is intended for systems administrators who are experienced with 
installing web server applications and want to get LImBuS up and running 
quickly.

This guide makes use of the project's Dockerfile. If you are unable to make use
of Docker, then please refer to the full installation guide.

Basic Requirements
------------------

Whilst these instructions have been tried and tested on Debian 10 Buster, Docker
and systemd both work on pretty much every Linux distribution.

And of course, a working internet connection.


Setting up Docker
-----------------

Something about Docker.

Removing old versions
~~~~~~~~~~~~~~~~~~~~~

First of all, it's always a good idea to remove any old versions you may have 
installed:
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

Please refer to...


