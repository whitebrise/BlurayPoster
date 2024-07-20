# 开发者文档

## 目录

```plaintext
BlurayPoster/
├── av/                       # 功放执行器目录
│   ├── __init__.py
├── media/                    # 媒体库执行器目录
│   ├── __init__.py     
│   ├── emby.py               
├── player/                   # 播放器执行器目录
│   ├── __init__.py     
│   └── oppo.py               
├── tv/                       # tv执行器目录
│   ├── __init__.py     
│   └── sony_bravia.py     
│   └── lg_webos.py      
├── abstract_classes.py       # 基类
├── bluray_poster.py          # 主程序
├── config.json               # 配置文件
├── configuration.py          
├── DEVELOPMENT.md            # 开发者文档
├── README.md                 # 项目介绍文档
└── requirements.txt          # 依赖文件
```

##  开发指南
- [ ] 你的TV/AV设备不在支持的列表中？ 别怕，只要你会python, 那么可以轻松开发适合你自己的TV,AV功放个性化设备。Media一般就用emby，除非你有特殊需求；Player目前只有oppo系, 其他种类的播放器得你自己研究了。
- 如何开发其他TV(AV功放同理)


比如你要开发一个支持samsung的tv

project folder
```
BlurayPoster/
├── av/                       
│   ├── __init__.py
├── media/                    
│   ├── __init__.py     
│   ├── emby.py               
├── player/                   
│   ├── __init__.py     
│   └── oppo.py               
├── tv/                       
│   ├── __init__.py     
│   └── sony_bravia.py     
│   └── lg_webos.py
│   └── samsung.py            # create a tv new file here
...
```

samsung.py
```python
# create py file，for example, samsung.py，put into the tv folder, open and write

import logging
from abstract_classes import TV, TVException

logger = logging.getLogger(__name__)

class Samsung(TV):
    def __init__(self, config: dict):
        super().__init__(config)
        try:
            # your other code
        except Exception as e:
            raise TVException(e)

    ### your other code
    ### ...
    ### your other code

    def start_before(self, **kwargs):
        # this function will be running when program start        
        # your code here
        pass

    def play_begin(self, on_message, **kwargs):
        # this function will be running when the movie start
        ##
        ## on_message: callable[[header: str, message: str], None]
        ## if you use "on_message("Notice", "This is a notice")" then you will receive a notice in your emby app
        ##
        # your code here
        pass

    def play_end(self, on_message, **kwargs):
        # this function will be running when the movie stop        
        # your code here
        pass

```

config.json
```json
{
  "Version": "1.0.0",
  "LogLevel": "debug",
  // ...
  // ...
  "TV": {
    "Executor": "tv.samsung.Samsung",  // Executor write "foldername.filename.classname"
    "IP": "192.168.1.10",
    "Key": "1234",
    "HDMI": 1,
    "PlayStopUri": null
  }
}

```
至此, 一个新的TV设备开发完成
