# BlurayPoster
**给你的蓝光机加上海报墙**

## 一、 说明
解决蓝光发烧友播放器选片没有海报墙的不方便，一键在电视/手机/电脑上的海报墙选片后自动调取蓝光机播放 [效果视频](https://www.bilibili.com/video/BV12S8MeiEyF)
- [ ] 理论上可以支持所有能网络控制的智能电视、功放和播放器，以及其他媒体库的海报墙
- [ ] 媒体库目前仅支持emby
- [ ] 播放器目前仅支持oppo系, 其他的播放器我不太清楚能不能控制，我也没有, 无法测试
- [ ] 目前TV仅支持索尼bravia系和Lg webos电视，因为我没有其他电视，无法测试
- [ ] 目前没写功放控制, 不能联动功放，有功放又有能力的可以自己添加功放控制解锁更多玩法
- [ ] 如果有问题, 可以提issue。把config.json文件中的"loglevel"改为"debug"然后运行程序,并且把发生问题时的日志(程序目录/logs下)发上来


## 二、 开始

### 1. 打开电视的网络控制
- [sony bravia生成预共享密钥](https://pro-bravia.sony.net/zhs/develop/integrate/ip-control/index.html#ip-control-authentication)看页面上的"BRAVIA商用显示器设置"，在电视上自己设定预共享密钥，并且打开远程设备控制。
- lg webos, 需要打开设置-支持-IP控制设置-网络IP控制 -> 打开；设置-支持-IP控制设置-LAN网络唤醒 -> 打开; 设置-常规-外部设备-用手机打开电视-通过wifi打开 -> 打开。程序第一次运行电视上会弹出确认，点击确认后以后就不会弹了。当然，如果你下一次重启程序，还会弹一次，解决方法是关闭程序后，在logs/下找到最新的日志，然后里面搜索client_key,把最新的key复制一下并填到config里tv的key中，以后都默认使用这个key，以后重启也不会弹了。


- [ ] 如果你的电视暂时不在上面的列表中，首先确定你的电视是否能网络控制，如果能网络控制, 那么只是时间问题，等后续其他有你这款电视的人开发就行。如果你会python，你甚至只要花几分钟就可以创建你自己的tv,参见开发者说明
- [ ] 如果你的电视不能网络控制, 那么你播放器播放后你得手动切换hdmi输出口，放完后还得自己手动切回来。这样建议就换电视别费劲了。
- [ ] 如果你碰到上面的问题但是还不想换电视, 你可以买一个能网络控制的AV功放/HDMI切换器，然后蓝光机和随便一个装有emby的安卓盒子接在av功放/切换器上，这样蓝光机播放的时候通过切换功放/切换器的输出也能达到相同效果。

### 2. 安装emby server并配置好影片海报墙
- [emby官网下载页面](https://emby.media/download.html)
- [ ] 媒体库里新增文件夹时，记下你选择的文件夹路径，后面的路径配置里要用(例如文件夹路径是\\NAS466C/Video/电影)。**注意**： 配置文件夹时，下面还有一个 《`（可选）共享的网络文件夹 `》选项，可以留空。如果留空，那就记住前面那个文件夹路径；如果你没有留空，那么就记这个填写的可选路径。


### 3. 安装程序
安装方式有2种，docker方式和直接安装, 建议使用docker方式

#### 3.1 docker安装

##### docker-cli
```docker-cli
docker run -itd \
    --name blurayposter \
    --hostname blurayposter \
    -v /config_dir:/config \
    -e 'PUID=0' \
    -e 'PGID=0' \
    -e 'UMASK=000' \
    -e 'TZ=Asia/Shanghai' \
    --restart always \
    whitebrise/blurayposter:latest
```

##### docker-compose
```docker-compose
version: '3.8'

services:
    blurayposter:
        image: whitebrise/blurayposter:latest
        container_name: blurayposter
        volumes:
            - /config_dir:/config
        environment:
            - 'PUID=0'
            - 'PGID=0'
            - 'UMASK=000'
            - 'TZ=Asia/Shanghai'
        restart: always
        tty: true
        stdin_open: true
```
- 其中, /config_dir为配置文件文件夹，强烈建议修改成宿主机上的位置，这样以后你重装docker和升级时，原有配置不会丢失
- 容器安装好后，先停止运行, 配置完你的config.json后，再点击运行即可，配置方法见下方《配置文件参数说明》


#### 3.2 直接安装
##### 3.2.1 安装python(建议安装3.11)
- [python下载页面](https://www.python.org/downloads/)
- 安装python(网络上搜索安装教程)

然后安装python依赖(linux控制台, 或者windows cmd)
```安装python依赖库
pip install -r requirements.txt
```

##### 3.2.2 下载代码并解压
下载zip压缩包到本地并解压


##### 3.2.3. 配置config.json

- [ ] 配置参数参见后面配置文件参数说明

##### 3.2.4 启动服务
服务可以24h启动，只要你的用户名密码文件路径等这种配置不变的，就不需要重启程序。期间开关播放器、电视、功放、海报墙都没有影响，建议装在nas上。

###### Linux
```linux
cd /home/{your user}/BlurayPoster
nohup python bluray_poster.py > /dev/null 2>&1 &
```

###### Windows
```windows
双击 bluray_poster.py 启动
保持服务运行可以加入到开机自启列表或者就不关机
```

### 4. enjoy
- 先打开播放器, 电视, 功放等
- 打开任意一个emby的app(手机/电视/网页/其他设备),登录和你配置文件中相同的用户
- 选择影片并享受海报墙的便捷+蓝光播放器的画质
- [ ] 如果想只允许蓝光机播放，记得把海报墙选片的app设备名添加到阻止列表
- [ ] 独立使用的设备只需要登录不同的emby用户就可以了


## 三、 配置文件参数说明
- 配置文件采用json格式和规范(目录下的文件)

config.json
```config.json
{
  "Version": "0.5.0",                    // 版本号
  "LogLevel": "info",                    // 日志类型
  "Media": {            
    "Executor": "media.emby.Emby",       // 引用的媒体库执行器(目前就一个, 需要自己开发其他的见开发者说明)
    "Client": "Emby Bluray Poster",      // 设备客户端
    "Device": "Bluray Poster",           // emby服务端显示的设备名称
    "DeviceId": "BlueWhite",             // 设备唯一id
    "Host": "http://192.168.1.10:8096",  // emby服务器地址:端口, 改成你自己的
    "Username": "aabbccddee",            // emby的用户名, 改成你自己的
    "Password": "abcd123456789",         // emby的用户密码, 改成你自己的
    "BlockDevices": ["SONY XR-77A95L"],  // 阻止播放的设备列表, 改成你自己的
                                            (在app上选片后，本身设备也会进行串流播放，
                                            通过添加设备名称列表，比如你想选片的电视/手机，可以阻止它们串流播放，
                                            避免播放器和app两个同时播放
                                            该设备名称可在emby-设备里看到，图片下面第一排就是设备名)
    "ExcludeVideoExt": "mp4,mkv",        // 排除的文件扩展名
                                            (用,隔开，格式命中的文件会直接走服务器串流，不会调用蓝光机，
                                            避免蓝光机对一些格式的流媒体文件支持不佳)
    "RepeatFilterTimeout": 120           // 重复检测，同一个视频在xx秒内不允许重复播放，防止快速点击播放/停止造成的反复启动蓝光机
  },
  "Player": {
    "Executor": "player.oppo.Oppo",      // 引用的播放机执行器(目前就一个, 需要自己开发其他的见开发者说明)
    "IP": "192.168.1.11",                // 播放机ip, 改成你自己的
    "Auth": [                            // 由于oppo蓝光机的smb挂载有bug,同一个用户进入挂载的文件夹后只要退出来就会报用户名密码错误
      {                                  // 解决的方法是要么使用nfs，要么就需要配置至少2个用户，通过交替登录这个2个用户来避免bug
        "Username": "username1",         // smb用户名
        "Password": "password1"          // smb密码
      },
      {
        "Username": "username2",
        "Password": "password2"
      }
    ],
    "UdpTimeout": 10,                      // udp超时时间
    "NFSPrefer": true,                     // 是否优先启用nfs(建议优先nfs,由于oppo蓝光机smb只能挂载一个smb根目录
                                            
                                                
    
    "MappingPath": [                       // 文件夹映射路径, 需要配置你自己的文件夹路径映射,详见下面的路径映射说明
      {
        "Media": "/NAS466C",               // emby媒体库地址          
        "SMB": "/NAS466C",                 // SMB路径映射
        "NFS": "/192.168.88.50",           // NFS地址映射
      }
    ]
  },
  "TV": {
    "Executor": "tv.sony_bravia.SonyBravia",    // 引用的TV执行器(目前有2个，一个sony bravia，一个lg的,
                                                                根据你的电视类型选择
                                                                索尼就用tv.sony_bravia.SonyBravia, LG就用tv.lg_webos.LGWebos
                                                                如果有其他人开发的文件, 改为tv.<filename>.<classname>就行
                                                                需要自己开发其他的见开发者说明)
    "IP": "192.168.1.12",                       // 电视IP, 改成你自己的
    "Key": "1234",                              // 电视控制识别码, 改成你自己的
    "HDMI": 1,                                  // 蓝光机对应的HDMI口, 改成你自己的
    "PlayStopUri": null                         // 播放结束后电视默认切换策略 
                                                   配置为null执行默认策略, sony为跳转到emby app, Lg为返回原来页面)
                                                   可以通过"<param>=<data>来手动指定
                                                   例如"app=netflix"代表返回netflix的app，"hdmi=3"代表返回hdmi 3输入源
  }
}

```

路径映射说明:

*注意:*

`路径配置的分割符全部都要改为"/", 无论你是windows还是linux还是其他的，无论原来的分割符是"/","//","\","\\"甚至"\\\\"，都统一改为"/"`

`路径以/开头, 结尾不要/`

`不是smb和nfs都必须配置, 你可以用哪个就配置哪个，另一个配置可以直接留"", 当然你也可以全配置`
```angular2html
有2种配置方式

比如我的文件夹分类是这样

NAS466C/Video/
├── 电影/
│   ├── 电影1
│   └── 电影2
├── 电视剧/
│   ├── 电视剧1
│   ├── 电视剧2/
│   │   ├── 电视剧2-s01
│   │   └── 电视剧2-s02
├── 动漫/
    ├── 动漫1
    └── 动漫2

1. 傻瓜配置
a. 首先获取emby媒体库里的地址(直接在媒体库里复制出来, 比如是/mnt/Video/电影),修改分隔符, 填写到 Media中(例如"/mnt/Video/电影")
b. 打开oppo, 点击网络, 显示出来的smb设备和nfs设备就是路径开头,例如能看到一个smb设备"NAS466C", 一个nfs设备"192.168.1.10"
c. 继续点击，直到找到你媒体库挂载的相同路径文件夹, 比如我点击的顺序是NAS466C -> Video -> 电影(注意中间还有一个图片/音乐/视频, 那个是oppo自己虚拟的，跟你的实际目录没关系，忽略掉)
d. 那么我的SMB路径就是 "/NAS466C/Video/电影", nfs同理
e. 自己的媒体库有几个路径就配几个，确保每个媒体库路径都有正确的配置, 比如/NAS466C/Video/电视剧，/NAS466C/Video/动漫

2. 进阶配置(如果你上面配置的路径中包含中文, 强烈建议往下看)
傻瓜配置后,你有以下3个目录
media："/mnt/Video/电影"
"SMB": "/NAS466C/Video/电影"
"NFS": "/192.168.1.10/Video/电影"

media："/mnt/Video/电视剧"
"SMB": "/NAS466C/Video/电视剧"
"NFS": "/192.168.1.10/Video/电视剧"

media："/mnt/Video/动漫"
"SMB": "/NAS466C/Video/动漫"
"NFS": "/192.168.1.10/Video/动漫"

看第一个目录, 可以发现后面路径都是/Video/电影, 相同的路径可以约掉，例如我可以修改成
media："/mnt/Video"
"SMB": "/NAS466C/Video"
"NFS": "/192.168.1.10/Video"
甚至也可以修改成
media："/mnt"
"SMB": "/NAS466C"
"NFS": "/192.168.1.10"

所以，其实只需要配置一个路径
media："/mnt"
"SMB": "/NAS466C"
"NFS": "/192.168.1.10"
就可以了
```

## 四、 开发者说明

见 `DEVELOPMENT.md`


## 五、感谢
灵感来源于[xnoppo](https://github.com/siberian-git/Xnoppo)
