#!/bin/bash

function limbus_create_kryten() {
    echo ">>>> Creating Kryten"
    docker-compose run web sh -c "flask cmd_setup create-kryten"
}

# This function allows the user to install a python package via 
# the pypi repository.
function limbus_pip_install() {
    echo "Enter the pip package you want to install:"
    read package
    echo "  >>> Now attempting to install $package:"
    docker-compose run web sh -c "pip3 install $package"

    echo "Do you want to save the changes to requirements.txt? (Y/N)"
    read answer

    if [ ${answer^^} == "Y" ]; then
        echo "  >>> Writing to requirements.txt:"
        docker-compose run web sh -c "pip3 freeze > requirements.txt"
    fi
}

function limbus_clear_binary_files() {
    echo "  >>> Cleaning binary files"
    docker-compose run web sh -c "find . -type f -name '*.pyc' -exec rm {} +"
}

function limbus_yarn_install() {
    echo ">>> Running yarn install:"
    docker-compose run web sh -c "yarn install"
}


function limbus_db_nuke() {
    echo "WARNING: THIS WILL DESTROY THE DATABASE, INCLUDING VERSIONS"

    echo "Are you sure you want todo this? (Y/N)"
    read answer
    if [ ${answer^^} == "Y" ]; then
        docker-compose run web sh -c "alembic stamp base"
        docker-compose run web sh -c "rm migrations/versions/*"
        docker-compose down -v
    fi
}

function limbus_db_create() {
    echo "CREATING DATABASE"

    if [ ! -d ./services/web/migrations/versions ]; then
        mkdir -p ./services/web/migrations/versions
    fi

    docker-compose run web sh -c "alembic revision --autogenerate -m 'Generating database'; alembic upgrade head"
}

function limbus_db_upgrade() {
    echo "Preparing datbase update"
    # A lil bit of fun 
    echo "alembic commit -m"
    read commit
    docker-compose run web sh -c "alembic revision --autogenerate -m '$commit'"
    docker-compose run web sh -c "alembic upgrade head"
}

function limbus_test_entrypoint() {
    docker-compose build
    limbus_yarn_install
    docker-compose run --service-ports web sh -c "nose2 -v"
}

function limbus_create_test_user() {
    docker-compose run web sh -c "flask cmd_setup create-testuser"

}

function limbus_setup_dev() {
    echo "WELCOME TO LIMBUS"
    echo "================="

    echo "Do you want to build from the Dockerfile? (Y/N)"
    read answer_one

    if [ ${answer_one^^} == "Y" ]; then
        echo ">>>> Building from Dockerfile"
        docker-compose build
    fi
    
    echo "Do you want to install yarn dependencies? (Y/N)"
    read answer_two

    if [ ${answer_two^^} == "Y" ]; then
        limbus_yarn_install
    fi
    
    echo "Do you want to set up the database? (Y/N)"
    read answer_three

    if [ ${answer_three^^} == "Y" ]; then
        limbus_db_nuke
        limbus_db_create
    fi

    echo "Creating Kryten"
    limbus_create_kryten

    echo "Creating dev user"


    echo "You should now be able to start up your dev environment by running:"
    echo "$ docker-compose up"

    echo "Happy hacking :)"
}  
