# 西安交大健康每日报自动填写
## <font color="#c00">⚠ ⚠ ⚠ ! ! ! 注意 | Attention ! ! ! ⚠ ⚠ ⚠</font>
**健康每日报为了维护大家的健康。**  
**本项目仅为技术分析，绝不允许用于实际。**  
**为大家健康负责，健康信息应当如实填报。**  
**祝各位健健康康。**  

**Health report policy exists for EVERYONE's health**  
**This Project is only for analyzing the techniques, practical application is ABSOLUTELY FORBIDDEN**  
**Be responsible for the common health, health condition should be reported Faithfully**  
**Be Well**  

## 部署 | Deploy
### 环境要求 | Environment
* python >= 3.5
* python-pip
* python-virtualenv
* 进程监视(e.g. supervisor)
### 流程 | Process
* 配置虚拟环境，运行 `virtualenv ./venv`  
* 启动虚拟环境，运行 `source ./venv/bin/activate`  
* 安装依赖，运行 `pip3 install -r requirements.txt`  
* 退出虚拟环境，运行 `deactivate`
* 复制 .env 运行 `cp .env.example .env`
* 配置 .env 中的账号信息
* 配置进程监视
## 开发者 | Contributors
* 代码： [f(x, z)=xzx](https://github.com/XuZhixuan)
* 技术支持： [mhq1065](https://github.com/mhq1065)
## LICENSE
[MIT License](https://opensource.org/licenses/MIT)  

    Copyright (c) 2020 f(x,z)=xzx

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
