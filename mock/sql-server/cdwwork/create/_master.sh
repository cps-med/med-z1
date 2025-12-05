#!/bin/zsh
source ~/swdev/med/med-insight/.env
sqlcmd -S 127.0.0.1,1433 -U sa -P ${CDWWORK_DB_PASSWORD} -i _master.sql