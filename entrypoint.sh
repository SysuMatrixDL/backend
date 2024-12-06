#!/bin/bash

# 启动 grafana 监控数据同步到 OpenGauss 数据库的脚本
/app/top &

# 启动后端
/app/main &

# 等待所有后台进程
wait