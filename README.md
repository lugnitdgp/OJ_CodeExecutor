# OJ_CodeExecutor

A server side application to process requests to run code submitted by the user thorugh th OJ frontend.

## Build/Run Instructions (Go)
cd into the ojserver directory and run 

```
go mod tidy
go build
```

Then run
```
./ojserver
```

## Production instructions

```
cd OJExec-Python
source setup-worker.sh
```

Edit the .env file with necessary details and restart the executor worker by the following command:
``` 
sudo supervisorctl restart executor
```

## Safeexec Submodule

The sandbox environment has been submoduled to the original repo so the changes immediately reflect back here.
To work with submodules:

```
1. git submodule init
2. git submodule update
3. cd safeexec
4. cmake .
5. make
```
From next time onwards, we need to check if the submodules have been updated, to do that:

```
git pull --recurse-submodules
```