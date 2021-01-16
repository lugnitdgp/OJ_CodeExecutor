# OJ_CodeExecutor

A server side application to process requests to run code submitted by the user thorugh th OJ frontend.

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

## Docker Setup

Temporary docker image can be found at `phantsure/oj:latest` on docker hub.
Before creating docker image create/update the .env in `OJExec-Python`. To create image:

```
docker build -t oj/executor .
```
The image has to be pushed to docker hub or github packages. For docker hub:
```
docker login
docker tag oj/executor USERNAME/REPONAME:TAG
docker push USERNAME/REPONAME:TAG
```

To setup docker swarm, first install docker to the server using [this guide](https://docs.docker.com/engine/install/ubuntu/)
On manager/master node:
```
docker swarm init
docker swarm join-token worker
```
Copy the provided command and type that to worker/slave nodes to join the swarm.

To start the service using the image we uploaded
```
docker service create --replicas 3 --name executor USERNAME/REPONAME:TAG
```
Note: `3` is just taken as an example any number can be put there.

### Swarm updates
Scaling
```
docker service scale executor=5
```
Note: Use the service you want to scale like in our case it was `executor`

Updating the image
```
docker service update --image NEWIMAGE:TAG executor
```

Remove service
```
docker service rm executor
```

Leaving the swarm(Can be run on any node)
```
docker swarm leave
```

### Debug 
To join the docker container to debug, first get the container id using `docker ps`.
```
docker exec -it CONTAINERID /bin/bash
```
