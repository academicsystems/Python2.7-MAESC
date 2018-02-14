FROM ubuntu
MAINTAINER Academic Systems

# make sure root is user

USER root

# update, upgrade, & install packages

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y && apt-get install -y lighttpd python2.7 python-setuptools python-numpy python-scipy python-networkx wget
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python2.7 get-pip.py
RUN pip2.7 install python-Levenshtein munkres
RUN rm get-pip.py

# configure lighttpd

COPY assets/lighttpd.conf /etc/lighttpd/lighttpd.conf
RUN touch /var/log/lighttpd/error.log
RUN chmod 664 /var/log/lighttpd/error.log
RUN chown -R www-data:www-data /var/log/lighttpd
RUN rm -rf /var/www/html

# configure web.py server

RUN wget https://www.saddi.com/software/flup/dist/flup-1.0.2.tar.gz
RUN tar xzf flup-1.0.2.tar.gz && rm flup-1.0.2.tar.gz
RUN cd flup-1.0.2 && python2.7 setup.py install && cd ..

RUN wget http://webpy.org/static/web.py-0.38.tar.gz
RUN tar xzf web.py-0.38.tar.gz && rm web.py-0.38.tar.gz
RUN cd web.py-0.38 && python2.7 setup.py install && cd ..

COPY assets/qanswer.py /var/www/qanswer.py
COPY assets/pyserver.py /var/www/pyserver.py

RUN chown www-data:www-data /var/www/pyserver.py
RUN chmod 555 /var/www/pyserver.py

RUN chown www-data:www-data /var/www/qanswer.py
RUN chmod 555 /var/www/qanswer.py

# tmp folder for saving user generated files

RUN mkdir /var/www/tmp
RUN chown www-data:www-data /var/www/tmp
RUN chmod 770 /var/www/tmp

CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]

