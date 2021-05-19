# OJ_CodeExecutor

A server side application to process requests to run code submitted by the user thorugh th OJ frontend.

## Production instructions without Docker (strongly unrecommended):

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

To setup docker swarm, first install docker to the server using `sudo apt install docker.io` on each worker and manager server and also install `docker-compose` fom [here](https://docs.docker.com/compose/install/) on the manager server.

Docker swarm requires an image to be deployed so we will need to keep a temporary storage to store them, which we fulfill using registry.

To run registry first we need to run the command:
`sudo docker service create --name registry --publish published=5000,target=5000 registry:2`
 and make sure you expose port 5000 of the manager node else the worker nodes wont be able to access it.

To build the image use 
`sudo docker-compose -f docker-compose.prod.yml build`
and to push it use `sudo docker-compose -f docker-compose.prod.yml push`.

On manager node:
```
docker swarm init
```
Copy the provided command and type that to worker nodes to join the swarm.

To start the service using the image we uploaded:

```
sudo docker stack deploy -c docker-compose.prod.yml executor
```

Note: The deploy configurantion contains the default number of replicase which in this case is `3` and is just taken as an example any number can be put there, but keep in mind the threshold of your server. We have assumed for safety purposes to allocate around 500 MB for each worker, so in a 2 GB RAM server you should have at max 4 workers running.

### Swarm updates

Scaling
```
docker service scale executor_executor=5
``` 
if you want the direct command but since we are using `docker stack` we can just modify the number of replicas inside the local `docker-compose.prod.yml` and update the service using `sudo docker stack deploy -c docker-compose.prod.yml executor` and check using `sudo docker stack services executor`.

Note: Use the service you want to scale like in our case it was `executor`

Updating the image
```
sudo docker stack deploy -c docker-compose.prod.yml executor
```
as `stack deploy` is both used to create and update a stack.

Remove a stack
```
sudo docker stack rm executor
```

Leaving the swarm(Can be run on any node)
```
docker swarm leave
```

### Debug 
To join the docker container to debug, first get the container id using `docker ps`.
```
sudo docker exec -it CONTAINERID /bin/bash
```
