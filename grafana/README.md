# grafana 魔改版

grafana的默认管理员账号admin，密码admin

利用 docker/dockerfile构建魔改版的grafana镜像

- `docker/grafana.db`会被复制到容器内`/var/lib/grafana/grafana.db`

  其中配置了open-gauss数据库连接配置、dashboard的默认配置，实现仪表盘的开箱即用

- `docker/defaults.ini`会被复制到容器内`/usr/share/grafana/conf/defaults.ini`

  这是grafana的配置文件，主要修改是允许grafana被iframe嵌入并且能够被匿名访问

  [参考文献](https://blog.csdn.net/qq_41538097/article/details/121272955)