#!/bin/bash

# 启动 grafana 监控数据同步到 OpenGauss 数据库的脚本
python /app/grafana/top.py &

# 启动后端
python uvicorn main:app --reload &

# 等待所有后台进程
wait