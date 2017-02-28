FROM ubuntu:16.04



# install hyperbrowser dependencies
RUN apt-get update && apt-get install -y \
   python2.7 \
   perl \
   r-base \
   libcairo2-dev \
   libzmq-dev \
   xvfb \
   libmagickcore-dev \
   rsync \
   python2.7-dev \
   libpq-dev \
   libglu1-mesa-dev

# install postgresql
#   database: hbdb
#   username: hbuser
#     use "database_connection = postgres://hbuser@localhost:5432/hbdb" in cfg
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
   postgresql-9.5 \
   postgresql-contrib-9.5 \
   postgresql-9.5-postgis-2.2 \
   libpq-dev \
   sudo
RUN echo "local all  postgres  peer " >  /etc/postgresql/9.5/main/pg_hba.conf && \
   echo  "local all  all       trust" >> /etc/postgresql/9.5/main/pg_hba.conf && \
   /etc/init.d/postgresql start && \
   sudo -u postgres createuser -s hbuser && \
   sudo -u postgres createdb -O hbuser hbdb
