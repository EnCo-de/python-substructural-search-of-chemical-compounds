#!/bin/bash
cd ~
wget https://github.com/EnCo-de/python-substructural-search-of-chemical-compounds/archive/refs/heads/deploy.zip
unzip deploy.zip
cd python-substructural-search-of-chemical-compounds-deploy
docker compose -p subs up -d