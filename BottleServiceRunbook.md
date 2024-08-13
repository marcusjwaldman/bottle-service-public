# **_Bottle Service_**<br>Runbook

**Sign in to Server**<br>
cd to .ssh<br>
cd ~/.ssh<br>
ssh -i "bottle-service-eb-dev" ubuntu@<current-name>.compute-1.amazonaws.com<br>



**Setup EC2**<br>
https://dev.to/awscommunity-asean/create-and-deploy-python-django-application-in-aws-ec2-instance-4hbm<br>
Add port 8000 to security group:<br>
Go to EC2 -> Security Group<br> 
Edit inbound rules<br>
Add Custom TCP – 8000 – 0.0.0.0/0<br>
Add Custom TCP – 3306 – 0.0.0.0/0<br>




**Clone Repo**:<br>
sudo apt update<br>
sudo apt install git<br> 
ssh-keygen -t rsa -b 4096 -C "`email`"<br>
eval "$(ssh-agent -s)"<br>
49  ssh-add ~/.ssh/id_rsa<br>
less ~/.ssh/id_rsa.pub -> copy<br>
ssh -T git@github.com<br>
git clone git@github.com:marcusjwaldman/bottle-service.git<br>



**Refresh Code from Repo**:<br>
Make sure work branch is main (git status)<br>
git pull<br>
cd bottle_service_app/<br>
pip install -r requirements.txt<br>
python3 manage.py migrate<br>
Make sure all static directories exist<br>
mkdir media<br>

**Set Environmental Variables**:<br>
This code will Generate a new Django secret key<br>
```python

import secrets
# Generate a 50-character random string for SECRET_KEY
SECRET_KEY = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
print(SECRET_KEY)
```
    

**Generated Key**:
Example Generated Key: `xz#24+mqi=$fkb#490$!w5((n^$l$4grmcexz_qr^b69=4zvv_`

create or edit file ~/.bash_profile<br>
export DJANGO_SETTINGS_MODULE=bottle_service_app.settings_aws<br>
export DJANGO_SECRET_KEY=xz#24+mqi=$fkb#490$!w5((n^$l$4grmcexz_qr^b69=4zvv_<br>

DJANGO_SECRET_KEY is an example. Please use your own and keep it secret

export DJANGO_ALLOWED_HOSTS="*"<br>
OR<br>
export DJANGO_ALLOWED_HOSTS="<IP Address>,<DNS>"<br>

After modifying bash_profile:<br>
source ~/.bash_profile<br>


**Versions**:<br>
Python 3.10.12<br>
Django==4.2.7<br>



**Run service – Django**<br>
python3 manage.py runserver 0:8000<br>
or in background<br>
nohup python3 manage.py runserver 0:8000 >> ../bottle_service.log &<br>




**Cloud Service**<br>
http://ec2-<ip underscored>.compute-1.amazonaws.com:8000/<br>



**Database**<br>
MariaDB 10.6<br>

**Connect from EC2 service**:<br>
mysql -u root -p -h `database URL`<br>

create database bottle_service_db;<br>
grant all privileges on bottle_service_db.* TO 'bottle_service_account'@'localhost' identified by 'PWD';<br>
flush privileges;<br>

To run tests:<br>
GRANT ALL PRIVILEGES ON test_BottleServiceMariaDB.* TO 'bottle_service_account'@'%';<br>

Change localhost to EC2 host.<br>

Run Django migration<br>

To pip install mysqlclient – need to first install dependencies on ubuntu service:<br>
sudo apt-get install mysql-client<br>
sudo apt-get install libmysqlclient-dev<br>
sudo apt-get install libssl-dev<br>
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential<br>
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config<br>


**Run Production**<br>
Update nginx config file with correct dns name if changed <br>
`sudo vi /etc/nginx/sites-available/bottle_service_app` <br>
nohup gunicorn bottle_service_app.wsgi:application>> ../bottle_service.log & <br>
sudo nginx -t <br>
sudo systemctl restart nginx <br>


**Make Production Ready** <br>
Obtain SSL Certs - key, csr, crt and dhparams <br>
_Temp SSL Creation_ <br>
openssl genpkey -algorithm RSA -out dyob_server.key <br>
openssl req -new -key dyob_server.key -out dyob_server.csr <br>
openssl x509 -req -days 365 -in dyob_server.csr -signkey dyob_server.key -out dyob_server.crt <br>
sudo openssl dhparam -out dyob-ssl-dhparams.pem 2048
Update nginx config file: <br>
sudo vi /etc/nginx/sites-available/bottle_service_app <br>
`server {
    listen 80;
    server_name <ec2 URL>;
    return 301 https://$host$request_uri;
}
server {
    listen 443 ssl;
    server_name <ec2 URL>;
    ssl_certificate /home/ubuntu/bottle-service/certs/dyob_server.crt;
    ssl_certificate_key /home/ubuntu/bottle-service/certs/dyob_server.key;
    ssl_dhparam /home/ubuntu/bottle-service/certs/dyob-ssl-dhparams.pem;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /bottle-service/bottle_service_app/media;
    }
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;  # Assuming Gunicorn is running on this port
    }
}` <br>
sudo nginx -t <br>
sudo systemctl restart nginx <br>

**Temp SSL** <br>
/home/ubuntu/bottle-service/certs/dyob_server.crt


**Rebuild Database**

Drop database bottle_service_db;<br>
create database bottle_service_db;<br>
drop user bottle_service_account@localhost; <br>
CREATE USER 'bottle_service_account'@'localhost' IDENTIFIED BY '&@';<br>
GRANT ALL PRIVILEGES ON bottle_service_db.* TO 'bottle_service_account'@'localhost'; <br>
GRANT ALL PRIVILEGES ON test_bottle_service_db.* TO 'bottle_service_account'@'localhost'; <br>
FLUSH PRIVILEGES; <br>