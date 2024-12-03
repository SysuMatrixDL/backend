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

## 启动运行

需要 [ASGI](https://asgi.readthedocs.io/en/latest/) 服务器启动。这里使用 [uvicorn](https://www.uvicorn.org/)

```shell
pip install -r ./requirements.txt
# 自动重载
uvicorn main:app --reload
# 手动重载
uvicorn main:app
```
