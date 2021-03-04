FROM ubuntu:latest

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata && apt-get install -y build-essential default-jre default-jdk cmake python3-venv debconf-utils git rpl supervisor systemctl curl python2
RUN apt-get install -y sudo

RUN groupadd user1
RUN echo "ubuntu:ubuntu:1101:1001:ubuntu:/home/ubuntu:/bin/bash" > user.txt
RUN newusers user.txt

RUN echo "ubuntu  ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu

WORKDIR /home/ubuntu
COPY . /home/ubuntu/OJ_CodeExecutor

RUN chown -R root:ubuntu /home/ubuntu

USER ubuntu
WORKDIR /home/ubuntu/OJ_CodeExecutor/OJExec-Python/
CMD /bin/bash -c "source setup_worker_docker.sh && tail -f /dev/null"
