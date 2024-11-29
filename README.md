# Controler

SysuMatrixDL的后端控制器

主要由python实现：

- 提供必要的api接口
- 远程管理和控制docker
- 管理openGauss数据库

## 数据库

见`sql`文件夹

`sql/open-gauss`提供启动OpenGauss的docker-compose

`sql/init.sql`提供初始化数据库的SQL语句，完成必要的建表操作

`sql/content.sql`初始化数据库内容，包括设备、公有镜像等设置