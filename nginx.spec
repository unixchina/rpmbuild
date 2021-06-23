Name: nginx          
Version: 1.21.0      
Release: 1%{?dist}
Summary: Nginx-1.21.0.tar.gz to nginx-1.21.0.rpm include 3rd module
License: 2-clause BSD-like
URL: http://nginx.org/			   
Packager: liuxing <daihaijun@gmail.com>	  
Vendor:   liuxing		 		
Source0: %{name}-%{version}.tar.gz     
									   
Source1: nginx.service                 
Source2: nginx.conf                    
Source3: allmod.conf

Source11: luajit2.1.zip
Source12: lua-nginx-module-0.10.14.tar.gz
Source13: nginx-echo-module-0.62.tar.gz
Source14: nginx-http-concat-1.2.2.tar.gz
Source15: nginx-http-footer-filter-1.2.2.tar.gz
Source16: nginx-module-sysguard.zip
Source17: nginx-module-vts-0.1.18.tar.gz
Source18: nginx_upstream_check_module.zip
Source19: ngx-waf-5.3.2.tar.gz
Source20: ngx_http_substitutions_filter_module-0.6.4.tar.gz


BuildRoot: %_topdir/BUILDROOT			

BuildRequires: gcc,make		
#Requires: openssl,openssl-devel,pcre-devel,pcre,uthash-devel,libsodium-devel

%description              
Base nginx-1.21.0.tar.gz,add some 3rd modules: nginx-module-lua-0.10.14,nginx-module-vts-0.1.18,
nginx-module-echo-0.62,nginx_upstream_check_module,ngx_http_substitutions_filter_module-0.6.4,
nginx-module-sysguard,ngx_waf-5.3.2

# Define macros
%define nginx_user      nginx
%define nginx_group     %{nginx_user}
%define nginx_home      /var/lib/nginx
%define nginx_home_tmp  %{nginx_home}/tmp
%define nginx_logdir    /var/log/nginx
%define nginx_confdir   %{_sysconfdir}/nginx	
%define nginx_datadir   /usr/local/nginx		
%define nginx_webroot   %{nginx_datadir}/html	
%define __requires_exclude libluajit-5.1.so.*


%prep 		 
# 提前把各种需要用到的文件拷贝到%{_sourcedir}目录里,yum安装包都可以提前做掉,尽量不要让spec来做
# Default path: %_builddir -- ~/rpmbuild/BUILD
#%setup -q
rm -fr %{name}-%{version}
ls %_sourcedir/*.tar.gz|xargs -n1 tar xzf
ls %_sourcedir/*.zip | xargs -n1 unzip -q -o -d %_builddir/
[[ -d "%{name}-%{version}" ]] && mkdir -p %{name}-%{version}/add-modules || { echo "%{name}-%{version} NOT exits";exit 1; }

# 目录名规范
mv -f lua-nginx-module-0.10.14 %{name}-%{version}/add-modules/nginx-module-lua-0.10.14
mv -f echo-nginx-module-0.62 %{name}-%{version}/add-modules/nginx-module-echo-0.62
mv -f nginx_upstream_check_module-master %{name}-%{version}/add-modules/nginx_upstream_check_module
mv -f nginx-module-sysguard-master %{name}-%{version}/add-modules/nginx-module-sysguard
mv -f ngx_waf-5.3.2 ngx_http_substitutions_filter_module-0.6.4 %{name}-%{version}/add-modules/
mv -f nginx-module-vts-0.1.18 nginx-http-concat-1.2.2 nginx-http-footer-filter-1.2.2 %{name}-%{version}/add-modules/

cd %{name}-%{version}
patch -p1 < add-modules/nginx_upstream_check_module/check_1.16.1+.patch

# prepare job1: install luajit2,这部分工作可以提前在构建机器环境中安装好也可以,因为相对还是费点时间的
#./install-luajit.sh %{source11}
#export LUAJIT_LIB=/usr/local/luajit/lib
#export LUAJIT_INC=/usr/local/luajit/include/luajit-2.1

# prepare job2: ngx-waf module
#yum install -y -q uthash-devel libsodium-devel		
\cp -a %_sourcedir/libinjection add-modules/ngx_waf-5.3.2/inc/
 

###  3.The Build Section 编译制作阶段，这一节主要用于配置和编译源码
%build
cd %{name}-%{version}
./configure --prefix=/usr/local/nginx --conf-path=/etc/nginx/nginx.conf --modules-path=/usr/lib64/nginx/modules  \
--http-log-path=/var/log/nginx/access.log  --error-log-path=/var/log/nginx/error.log --sbin-path=/usr/sbin/nginx \
--pid-path=/var/run/nginx.pid --lock-path=/var/lock/subsys/nginx --user=nginx --group=nginx --with-file-aio --with-http_ssl_module --with-http_v2_module  \
--with-http_addition_module --with-http_sub_module --with-http_dav_module --with-http_flv_module --with-http_slice_module --with-http_stub_status_module \
--with-http_mp4_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_random_index_module --with-http_secure_link_module \
--with-http_degradation_module --with-mail_ssl_module --with-pcre --with-pcre-jit --with-debug --with-http_realip_module --with-http_xslt_module=dynamic \
--with-http_image_filter_module=dynamic --with-http_geoip_module=dynamic --with-http_perl_module=dynamic --with-mail=dynamic  --with-stream=dynamic --with-stream_ssl_module \
--add-module=add-modules/nginx_upstream_check_module --add-module=add-modules/ngx_http_substitutions_filter_module-0.6.4 \
--add-module=add-modules/nginx-http-footer-filter-1.2.2/ --add-dynamic-module=add-modules/nginx-module-lua-0.10.14 --add-module=add-modules/nginx-module-vts-0.1.18 \
--add-module=add-modules/nginx-http-concat-1.2.2 --add-module=add-modules/nginx-module-echo-0.62 --add-dynamic-module=add-modules/nginx-module-sysguard/ \
--add-dynamic-module=add-modules/ngx_waf-5.3.2 --with-cc-opt='-std=gnu99'

make %{?_smp_mflags}            

###  4.Install section  这一节主要用于完成实际安装软件必须执行的命令，可包含4种类型脚本

%install
rm -rf %{buildroot}/*
mkdir -p %{buildroot}/%{_sbindir}
cd %{_builddir}/%{name}-%{version}

make install DESTDIR=%{buildroot}
# 创建相关目录,下面已经用install命令代替
#mkdir %{buildroot}/%{nginx_confdir}/{conf.d,default.d,ssl}
find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} \;
find %{buildroot} -type f -empty -exec rm -f {} \;
# 编译完成后会生成一些.default配置文件,都是冗余的,这里都把这些冗余的删除.
rm -fr %{buildroot}/etc/nginx/fastcgi.conf.default
rm -fr %{buildroot}/etc/nginx/fastcgi_params.default
rm -fr %{buildroot}/etc/nginx/mime.types.default
rm -fr %{buildroot}/etc/nginx/scgi_params.default
rm -fr %{buildroot}/etc/nginx/uwsgi_params.default

# 创建目录和拷贝预先准备好的配置模板
install -m 0755 -d %{buildroot}/%{nginx_confdir}/{conf.d,default.d,modules,ssl}
install -p -D %{_sourcedir}/nginx.service %{buildroot}/usr/lib/systemd/system/nginx.service
install -p -D %{_sourcedir}/nginx.conf %{buildroot}/%{nginx_confdir}/nginx.conf					
install -p -D %{_sourcedir}/nginx.conf %{buildroot}/%{nginx_confdir}/nginx.conf.default
install -p -D %{_sourcedir}/allmod.conf %{buildroot}/%{nginx_confdir}/modules/allmod.conf

# %doc部分需要用到
install -p -D LICENSE CHANGES README %{_builddir}/

%pre
# $1有3个值，代表动作，安装类型，处理类型
# 1：表示安装
# 2：表示升级 
# 0：表示卸载
if [ $1 -eq 1 ];then                                                         
    mkdir -p /var/lib/nginx /var/log/nginx
    id -u nginx &>/dev/null
    [[ $? -eq 1 ]] && /usr/sbin/useradd -r nginx -s /sbin/nologin -d /var/lib/nginx 2> /dev/null \
	|| echo user 'nginx' already exists           	
fi                                                                                
                                                                            
%post
if [ $1 -eq 1 ];then
	chown -R nginx:nginx /var/log/nginx /var/lib/nginx %{nginx_datadir}
	systemctl daemon-reload
	#systemctl enable nginx
        #systemctl start nginx
fi

%preun
if [ $1 -eq 0 ];then
    systemctl stop nginx > /dev/null 2>&1
    #/usr/sbin/userdel -r nginx 2> /dev/null
fi

%postun
if [ $1 -eq 0 ];then
	[[ ! `ps -Ao user|grep -w "nginx"` ]] && /usr/sbin/userdel -r nginx 2> /dev/null
fi


#%clean
###  5.clean section 清理段,clean的主要作用就是删除BUILD.可以不指定
#rm -rf %{buildroot}


%files              
###  6.file section 文件列表段，这个阶段是把前面已经编译好的内容要打包了,其中exclude是指要排除什么不打包进来。
%defattr(-,root,root,0755)
%dir %{nginx_confdir}
%dir %{nginx_confdir}/default.d				
%dir %{nginx_confdir}/conf.d
%dir %{nginx_confdir}/modules
%dir %{nginx_confdir}/ssl

%doc LICENSE CHANGES README
%{nginx_datadir}							
%{_sbindir}/nginx				
/usr/lib64/nginx
%config(noreplace) %{nginx_confdir}/nginx.conf
%config(noreplace) %{nginx_confdir}/nginx.conf.default
%config(noreplace) %{nginx_confdir}/modules/allmod.conf
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/win-utf
/usr/lib/systemd/system/nginx.service
/usr/local/lib64/perl5
/usr/local/share/man/man3/nginx.3pm


###  7.chagelog section  日志改变段， 这一段主要描述软件的开发记录

%changelog
*  Mon Jun  8 2021 liuxing <daihaijun@gmail.com> - 1.21.0-1
- Initial version,dependent package is luajit2,exact module:libluajit-5.1.so.2
- add these module: nginx-module-echo-0.62,nginx_upstream_check_module,ngx_http_substitutions_filter_module-0.6.4
- nginx-module-vts-0.1.18, nginx-module-echo-0.62, nginx-module-sysguard, ngx_waf-5.3.2
