# Base image - ubuntu
FROM ubuntu:18.04

#Setting timezone
ENV TZ Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#Construct the home directory and work directory
RUN addgroup --gid 1001 app 
RUN useradd -u 1001 \
            -G app \
            -d /home/app/workdir \
            -s /sbin/nologin \
            -g app \
            app

#Install python, Set timezone and relation 
RUN apt-get update \
    && apt-get install tzdata \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && apt-get install -y python3.6 \
    python3.7-dev \
    python3-pip \
    && apt-get clean \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 

#Create an app user for the application usage
ENV HOME=/home/app/
ENV APP_HOME=$HOME/workdir/

RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME
RUN chown -R app:app $APP_HOME

#Install python packages
COPY ./requirements.txt $APP_HOME/requirements.txt
RUN pip3 --no-cache-dir install -r $APP_HOME/requirements.txt

#Project data and code
# ALL FILE Into image: COPY . /home/app/workdir/
#COPY . $APP_HOME
COPY . $APP_HOME/

#Change User - app
USER app

ENV PROJECT_PATH=$APP_HOME

#Run api code
CMD python3 main.py
