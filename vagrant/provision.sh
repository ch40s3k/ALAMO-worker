#!/usr/bin/env bash
# Install essential packages
apt-get update
apt-get upgrade
apt-get -y install mc vim git 2> /dev/null
apt-get -y install rabbitmq-server 2> /dev/null
apt-get -y install build-essential libbz2-dev libfreetype6-dev libgdbm-dev 2> /dev/null
apt-get -y install python3-pip 2> /dev/null

# Create virtualenv for python 3.4
pip3 install virtualenvwrapper
VIRTUALENVS='/home/vagrant/.virtualenvs'
if [ ! -d $VIRTUALENVS ]; then
mkdir /home/vagrant/.virtualenvs
fi
chown -R vagrant:vagrant $VIRTUALENVS
sudo -u vagrant bash -c "export WORKON_HOME=$VIRTUALENVS"
if [ `grep alamo /home/vagrant/.bashrc | wc -l` = 0 ]; then
echo "VIRTUALENVWRAPPER_PYTHON='/usr/bin/python3'" >> /home/vagrant/.bashrc
echo 'command' >> /home/vagrant/.bashrc
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> /home/vagrant/.bashrc
echo 'if [ `workon | grep alamo | wc -l` = 1 ]' >> /home/vagrant/.bashrc
echo 'then' >> /home/vagrant/.bashrc
echo 'workon alamo' >> /home/vagrant/.bashrc
echo 'else' >> /home/vagrant/.bashrc
echo 'mkvirtualenv alamo' >> /home/vagrant/.bashrc
echo 'fi' >> /home/vagrant/.bashrc
fi

# Install application environment
su -l vagrant -c '/home/vagrant/.virtualenvs/alamo/bin/pip install ipython tox'
su -l vagrant -c '/home/vagrant/.virtualenvs/alamo/bin/pip install asyncio asynqp'
