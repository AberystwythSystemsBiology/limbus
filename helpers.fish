#!/bin/fish

function limbus-c 
    docker-compose run web sh -c "find limbus -type f -name '*.pyc' -exec rm end +"
end

function limbus-bwd 
    limbus-b
    limbus-deps
end

function limbus-deps 
    docker-compose run web sh -c "python3 -m venv venv && venv/bin/pip install -r requirements.txt && yarn install"
end

function limbus-b 
    docker-compose build
end

function limbus-s 
    docker-compose run --service-ports web sh -c "venv/bin/python limbus/run.py"
    limbus-c
end

function limbus-db-create 
    limbus-db-init
    limbus-db-migrate
    limbus-db-upgrade
end

function limbus-db-init 
    docker-compose run web sh -c "venv/bin/flask db init"

end

function limbus-db-migrate 
    docker-compose run web sh -c "venv/bin/flask db migrate"
end

function limbus-db-upgrade 
    docker-compose run web sh -c "venv/bin/flask db upgrade"
end