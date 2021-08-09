# ZJU-nCov-Hitcarder

浙大nCov肺炎健康打卡定时自动脚本，多账号 github Actions 版本

 - 可定时，默认为每天9点到12点每10分钟运行一次
 - 默认每次提交上次所提交的内容（只有时间部分更新）
 - 系统表单如有更新，在当天自行手机打卡，后面会自动按照你更新后的选项继续打卡

 项目用于学习交流，仅用于各项无异常时打卡，如有身体不适等情况还请自行如实打卡~

<img src="https://github.com/Tishacy/ZJU-nCov-Hitcarder/raw/master/demo.png" width="500px"/>

> 感谢[conv1d](https://github.com/conv1d)同学，已使用requests直接登录浙大统一认证平台，不再依赖phantomjs

## Usage

1. fork本项目

2. 在项目设置中添加名为 CONFIG 的 Secrets，将 config.example.json 模板文件的内容复制为值，并进行适当修改
  
    ```javascript
    [
      {
        "username": "你的浙大统一认证平台用户名",
        "password": "你的浙大统一认证平台密码"
      },
      {
        "username": "你的浙大统一认证平台用户名",
        "password": "你的浙大统一认证平台密码"
      }
    ]
    ```

4. 启动定时自动打卡脚本

   ```bash
   $ python3 main.py
   ```


## Tips

- 测试程序是否正常运行：可以先把定的时间放在最近的一个时间（比如下一分钟）看下到时间是否可以正常打卡
- 想指定自己打卡地理位置的童鞋可以参考[8#issue](https://github.com/Tishacy/ZJU-nCov-Hitcarder/issues/8#issue-565719250)


## Thanks

感谢贡献者

<a href="https://github.com/conv1d"><img src="https://avatars2.githubusercontent.com/u/24759956" width="100px" height="100px"></a>
<a href="https://github.com/Mythologyli"><img src="https://avatars.githubusercontent.com/u/15955880" width="100px" height="100px"></a>


## LICENSE

Copyright (c) 2020 tishacy.

Licensed under the [MIT License](https://github.com/Tishacy/ZJU-nCov-Hitcarder/blob/master/LICENSE)



