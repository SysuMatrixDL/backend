# SysuMatrixDL 的 后端 + 集中控制器

`docker-compose.yml` 仅用于开发环境，不用于生产环境

## 控制节点

扮演三个角色：
- 控制所有工作节点的 controler
- 负责数据库运行、存储
- 运行后端服务为前端提供 api 接口

内容包括：
- FastAPI 提供给前端必要的 api 接口，位于 `api` 目录下
- 远程管理和控制 docker 容器、镜像，位于 `controler` 目录下
- 通用程序，位于 `common` 目录下
  - `connect.py` 管理 openGauss 数据库
  - ......

## 数据库

见 `sql` 文件夹

`sql/open-gauss` 提供启动OpenGauss的docker-compose

`sql/init.sql` 提供初始化数据库的SQL语句，完成必要的建表操作

`sql/content.sql` 初始化数据库内容，包括设备、公有镜像等设置

## 调试运行

确保数据库正在运行（测试服），在 `config.py` 中定义了如何连接数据库的参数，主要注意 `DB_HOST`，本地调试时可通过环境变量设置测试服数据库：

```shell
export DB_HOST=172.18.198.206
```

需要 [ASGI](https://asgi.readthedocs.io/en/latest/) 服务器启动。这里使用 [uvicorn](https://www.uvicorn.org/)

```shell
pip install -r ./requirements.txt
# 自动重载
uvicorn main:app --reload
# 手动重载
uvicorn main:app
```
