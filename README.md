# VK Pixel Battle 2019 Botnet
A tool written for BAGOSI during the VK Pixel Battle 2019 annual event.\
Some of the features remains unpolished so they are not going to be in this release.

**Authors:** @kumfc & @3vilWind

\
![](https://github.com/kumfc/pixel-battle-botnet/raw/master/pxb-botnet.png)


**Deploying on single machine:**\
*Deploying it on multiple machines is pointless until you have 1000+ bots*

0. Set client node role to manager

1. Init
```
docker swarm init
docker service create --name registry --publish published=5000,target=5000 registry:2
iptables -I DOCKER-USER -p tcp --destination-port 5000 -j DROP
```

 2. Start 
```
docker-compose -f /root/pixel-battle-botnet-dev/docker-compose.deploy.yml build
docker-compose -f /root/pixel-battle-botnet-dev/docker-compose.deploy.yml push
docker stack deploy -c /root/pixel-battle-botnet-dev/docker-compose.deploy.yml pixel
```

 3. Kill 
```
docker stack rm pixel
```
