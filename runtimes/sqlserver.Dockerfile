FROM ubuntu:18.04

# Required packages to install SQL Server Driver
RUN apt-get update -qq && apt-get install -y curl gnupg2

# Update package list manually to install SQL Server Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Required packages to enable Kerberos Authentication
RUN apt-get install -y unixodbc-dev krb5-user
RUN yes | apt-get install -y mssql-tools

ENV PATH=${PATH}:/opt/mssql-tools/bin

# Required packages for the Application
RUN apt-get install -y vim python3-pip git
RUN mkdir /works
ADD requirements.txt /works
WORKDIR /works

# Install libraries the Application will use
RUN pip3 install --default-timeout=1000 -r requirements.txt
