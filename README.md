# master-o-meter

With inspiration and some code from https://github.com/joapaspe/tesismometro and https://github.com/Wheest/thesis-o-meter. 


## About the project

## Implementation

This is mostly for myself remembering what I did in a month from now.

### Hosting and Network stuff
I use my raspberry pi as my own webserver for hosting this project. Therefore one has to forward the ports 80 
and 443 of the router, to make the server reachable from the internet. Now with the ip from my pi one can reach the server, but the ip changes about every day. The solution I use is the dynamic DNS service https://dynv6.com/. My router sends automatically the new ip to this service when it changes which updates the DNS entry.

Configuring https is easy with certbot. See here https://upcloud.com/resources/tutorials/install-lets-encrypt-apache.


### Measuring progress
Texcount, crontab

### Django Apache Setup
Restarting the server after changes: sudo systemctl restart apache2