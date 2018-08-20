# MaLiShop

#### 项目介绍
码力小程序商城后台，配合码力小程序使用

#### 软件架构
debian9.5下 python3  postgresql9.5  


#### 安装教程

debian9.5下配置项目.我是su到root下安装的，如不是root下，请加sudo
先安装数据库，参考https://www.postgresql.org/download/linux/debian/   我安装的是postgresql-9.5(钱不多，机器配置低，怕上10会卡)
因为表的敏感数据进行加密，还要安装postgresql-contrib
安装apache,mod_wsgi,python3(系统默认的是3.5可以用),pip3
apt-get install python3-pip apache2 libapache2-mod-wsgi-py3
mod_wsgi.so  的路径在 /usr/lib/apache2/modules/mod_wsgi.so   
记住这个路径。如果没有找到。那就find / -name mod_wsgi.so  找到这个就记住，下边配置apache处理py文件要用
安装好apache,mod_wsgi 直接到项目目录下 /vag/games/用git下载项目  debian默认是没有games目录
下载到项目，就进入目录（cd /var/games/MaLiShop/）用pip3安装依赖包  pip3 install -r requirements.txt 
安装好依赖开始配置apache.   我的配置文件路径  /etc/apache2/   

ESKTOP-0UBJBRH:/etc/apache2# vim sites-enabled/000-default.conf 
注意参考：https://dormousehole.readthedocs.io/en/latest/deploying/mod_wsgi.html     这个flask官方的。
############################### 看到配置文件的DocumentRoot /var/www/html  在这一行下边配置如下
       
```
 WSGIDaemonProcess MaLiShop threads=5
        WSGIScriptAlias / /var/games/MaLiShop/run.py                                                                                                             
        <Directory /var/games/MaLiShop>
                WSGIProcessGroup MaLiShop
                WSGIApplicationGroup %{GLOBAL}
                WSGIScriptReloading On
                Require all granted

        </Directory>
```


重启apache  service apache2 restart   如果重启没有提示错误，那就表示配置没有问题。


#### 使用说明

打开链接，http://127.0.0.1/admin/login/   看到登录界面(注意，第一个打开会有点慢，等等就行)，就行了。
登录用户名  malishop  密码  12345678
更多的使用，请自行研究。
如果是生产环境,建议采用nginx代理，apache开多端口，负载均衡。这样更耐操。要是还想超耐操，只要服务器配置够强，可以在一台服务器同时安装几个apache，这样做负载均衡，就绝对没问题了。

