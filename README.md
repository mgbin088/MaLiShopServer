# MaLiShop

#### 项目介绍
码力小程序商城后台，配合码力小程序使用

#### 软件架构
linux 下 python3  postgresql9.5  


#### 安装教程  debain 9.5下的。

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



####  安装ubuntu 16.04 下的
 安装环境为ubuntu 16.04
安装 数据库参考  https://www.postgresql.org/download/linux/ubuntu/

Create the file /etc/apt/sources.list.d/pgdg.list and add a line for the repository+

deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main

Import the repository signing key, and update the package lists

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

sudo apt-get update

#我安装的是9.5，如果您机器配置够建议完全按照上边的官方链接安装 
sudo apt-get install postgresql-9.5      安装 9.5的命令
我这里安装好会有一行红字，提示的是安装的路径和日志路径
9.5 main    5432 down   postgres /var/lib/postgresql/9.5/main /var/log/postgresql/postgresql-9.5-main.log
如果您打算要远程连接数据库查看数据的话，那就要设置postgresql.conf，不打算远程就不用设置postgresql.conf

cd /etc/postgresql/9.5/main    
sudo vim postgresql.conf    
看到59行左右   #listen_addresses = 'localhost' 
改为listen_addresses = '*'    这表示允许任何地址连接本数据库 
改好保存退出   
接下来要设置pg_hba.conf
也是在/etc/postgresql/9.5/main    这个路径下
 sudo vim pg_hba.conf

把host    all             all             127.0.0.1/32     md5   的这个md5改为trust  表示将md加密改为不验证连接。
如果要使用远程的，就在最底多加一行   
host    all             all             0.0.0.0/0              md5    表示允许任何ip连接，以md5加密方式验证
改好保存退出
接下来设置密码
sudo su - postgres
psql   输入这个就看到   postgres=#
输入   ALTER USER postgres with encrypted password 'your_password';    这条命令改密码
修改成功返回   ALTER ROLE
然后退出，输入    \q   回车

然后安装项目所需的软件包
sudo apt-get update
sudo apt-get install gcc wget git 
sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3

cd /var
 sudo mkdir games   #因为默认没有这个目录就要建一下
cd games   

 sudo git clone https://github.com/eoen/MaLiShop-Server.git
sudo vim config.py
CLIENT_NAME = 'MaLiShop-Server'  确认项目名已修改。
scott='postgres'#用户名    您上边的    ALTER USER postgres  这个postgres就行
tiger = 'your_password'#密码
host = '127.0.0.1'#地址  这个就行
修改完，保存退出。
现在恢复数据库。新建一个名叫MaLiShop-Server数据库
然后从项目的sql目录下的数据备份文件恢复到MaLiShop-Server数据库
注意：云服务器的防火墙要放进放出5432
我是在windows下用pgadmin3连接数据库进行恢复的。
然后运行    pip3 install -r requirements.txt      安装相关依赖包。
开始最后配置apache了。
注意参考：https://dormousehole.readthedocs.io/en/latest/deploying/mod_wsgi.html     这个flask官方的。

如果修改端口 cd  /etc/apache2   sudo vim ports.conf    修改   Listen 80    这一行。注意这里的端口要与下边的虚拟端口一致
然后  cd /etc/apache2/sites-enabled/       sudo vim 000-default.conf     这里默认只有这一个文件
注意，如果上边修改了端口，那<VirtualHost *:80>  这个80也要改成刚才修改的那个端口。
然后在   DocumentRoot /var/www/html   下边添加以下配置
 WSGIDaemonProcess MaLiShop-Server threads=5
        WSGIScriptAlias / /var/games/MaLiShop-Server/run.py                                                                                                     
        <Directory /var/games/MaLiShop-Server>
                WSGIProcessGroup MaLiShop-Server
                WSGIApplicationGroup %{GLOBAL}
                WSGIScriptReloading On
                Require all granted

        </Directory>
然后保存退出
重启postgrsql   和apache2服务
 sudo service postgresql restart
 sudo service apache2 restart

#### 使用说明

打开链接，http://127.0.0.1/admin/login/   看到登录界面(注意，第一个打开会有点慢，等等就行)，就行了。
登录用户名  malishop  密码  12345678
更多的使用，请自行研究。
如果是生产环境,建议采用nginx代理，apache开多端口，负载均衡。这样更耐操。要是还想超耐操，只要服务器配置够强，可以在一台服务器同时安装几个apache，这样做负载均衡，就绝对没问题了。

![image](https://cdn.maliapi.cn/image/maligithubdemo.png)

