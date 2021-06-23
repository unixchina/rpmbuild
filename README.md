# Nginx rpm包构建

### 1. 说明

基于原生Nginx 1.21.0, 添加了许多第三方一些实用模块,比如vts监控模块,lua模块,echo模块,健康检查模块,stream模块等等

### 2. rpm包的安装
推荐安装方式：yum localinstall <nginx-1.21.0-xx.rpm>  
这样会提示并将依赖包一起安装

### 3. lua模块的使用
注意默认lua模块不启用,如果需要使用lua，请先安装luajit2引擎：  
yum install luajit  
然后注释掉allmod.conf里的ndk/lua两个模块