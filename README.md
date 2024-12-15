# BlurayPoster
**给你的蓝光机加上海报墙**

## 一、 说明
解决蓝光发烧友播放器选片没有海报墙的不方便，一键在电视/手机/平板/安卓盒子/ATV/电脑上的海报墙选片后自动调取蓝光机播放 [效果视频](https://www.bilibili.com/video/BV1k384eLELP)
- [ ] 智能分流：原盘电影调用蓝光机看双层杜比，流媒体默认使用电视/盒子等播放，兼容所有格式并且效果最佳。
- [ ] 理论上可以支持所有能网络控制的智能电视、功放和播放器。
- [ ] 宽容度高, 电视，投影仪，功放，回音壁都行；有nas最好，没有nas电脑挂硬盘的这种也行，云盘cd2挂载也支持。可以说只要你的emby能刮削海报，你的播放器能播放，就能使用这套系统。
- [ ] 媒体库目前使用emby, 海报墙流畅精美。
- [ ] 播放器目前支持oppo系包括203，205这种，各种山寨魔改的oppo蓝光机也没问题，以及高清固件的9708。
- [ ] 可以联动的TV目前仅支持索尼bravia系和Lg webos电视，以及hdfury和带hdmi输入的oppo系。
- [ ] 可以联动的功放目前仅支持安桥功放
- [ ] 如果你的电视或者功放暂时不在支持列表中，无法实现hdmi自由切换。不过可以手机/电脑/平板选片，就是少了在大屏幕上看海报墙选片的快乐。
- [ ] 如果有问题, 可以提issue。把config.yaml文件中的"loglevel"的值由"info"改为"debug"然后运行程序,并且把发生问题时的日志(程序目录/logs下)发上来


## 二、 开始

### 1. 打开电视的网络控制(如果你不需要控制电视，跳过这一步)
- [sony bravia生成预共享密钥](https://pro-bravia.sony.net/zhs/develop/integrate/ip-control/index.html#ip-control-authentication)看页面上的"BRAVIA商用显示器设置"，在电视上自己设定预共享密钥，并且打开远程设备控制。
- lg webos, 需要打开设置-支持-IP控制设置-网络IP控制 -> 打开；设置-支持-IP控制设置-LAN网络唤醒 -> 打开; 设置-常规-外部设备-用手机打开电视-通过wifi打开 -> 打开。程序第一次运行电视上会弹出确认，点击确认后以后就不会弹了。当然，如果你下一次重启程序，还会弹一次，解决方法是关闭程序后，在logs/下找到最新的日志，然后里面搜索client_key,把最新的key复制一下并填到config里tv的key中，以后都默认使用这个key，以后重启也不会弹了。


- [ ] 如果你的电视暂时不在上面的列表中，首先确定你的电视是否能网络控制，如果能网络控制, 那么只是时间问题，等后续其他有你这款电视的人开发就行。如果你会python，你甚至只要花几分钟就可以创建你自己的tv,参见开发者说明
- [ ] 如果你不想使用电视控制，还可以使用功放切换hdmi输出口，或者使用hdmi切换器(如hdfury)。或者自带有hdmi输入的oppo系(再给它配个盒子就行)，这样蓝光机播放的时候通过切换功放/切换器/oppo的输出也能达到相同效果。
- [ ] 如果以上均不行, 那么如果你在大屏上选片后，播放器开始播放时你得手动切换hdmi输出口，放完后还得自己手动切回来，这样建议就不要在大屏幕上选片了。可以在手机/平板上点海报墙选片，那么把电视/功放的参数不填就可以满足你的要求了，相当于不控制电视/功放联动。

### 2. 安装emby server并配置好影片海报墙
- [emby官网下载页面](https://emby.media/download.html)
- [ ] 媒体库里新增文件夹时，记下你选择的文件夹路径，后面的路径配置里要用(例如文件夹路径是\\NAS466C/Video/电影)。**注意**： 配置文件夹时，下面还有一个 《`（可选）共享的网络文件夹 `》选项，一般可以留空。但如果你的emby媒体库文件夹路径不是以"/"开头(比如你是windows硬盘，配的文件夹路径是d:/movie)，那么就需要填写这个网络路径不能留空。
- [ ] `（可选）共享的网络文件夹 `如果留空，那就记住前面那个文件夹路径；如果没有留空，那么就记这个填写的可选路径。


### 3. 安装程序
安装方式有2种，docker方式和直接安装, 建议使用docker方式

#### 3.1 docker安装

##### docker-cli
```docker-cli
docker run -itd \
    --name blurayposter \
    --log-driver=json-file \
    --log-opt max-size=2m \
    --log-opt max-file=7 \
    --hostname blurayposter \
    -v /blurayposter/config:/config \
    -e 'PUID=0' \
    -e 'PGID=0' \
    -e 'UMASK=000' \
    -e 'TZ=Asia/Shanghai' \
    --restart unless-stopped \
    whitebrise/blurayposter:latest
```

##### docker-compose
```docker-compose
version: '3.8'

services:
    blurayposter:
        image: whitebrise/blurayposter:latest
        container_name: blurayposter
        logging:
            driver: "json-file"
            options:
                max-size: "2m"
                max-file: "7"
        volumes:
            - /blurayposter/config:/config
        environment:
            - 'PUID=0'
            - 'PGID=0'
            - 'UMASK=000'
            - 'TZ=Asia/Shanghai'
        restart: unless-stopped
        tty: true
        stdin_open: true
```
- 其中, /blurayposter/config为配置文件使用的文件目录，该目录含有配置文件config.yaml
- 容器安装好后，先停止运行, 配置完你的config.yaml后，再点击运行即可
- 每次修改完配置文件，必须重启后才能生效


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


##### 3.2.3. 配置config.yaml

- 默认docker配置文件路径为/blurayposter/config/config.yaml
- 默认配置文件一般如下

```yaml
# YAML配置
# 每次修改完配置后，必须重启程序才能生效
# 使用 # 来注释掉某行

# 版本号
Version: "1.0.0"

# 日志级别(如果发生问题搞不定的，把info改成debug然后重启，再把出问题时候的日志发上来, 问题修复后再改回info)
LogLevel: info


# 媒体库配置
Media:
  # 引用的媒体库执行器, 不要改
  Executor: media.emby.Emby
  # 设备客户端, 不要改
  Client: Emby Bluray Poster
  # 媒体库服务端显示的设备名称， 不要改
  Device: Bluray Poster
  # 设备唯一id， 不要改
  DeviceId: whitebrise
  # 媒体库服务器地址:端口, 改成你自己的
  Host: http://192.168.1.10:8096
  # 媒体库服务器的用户名, 改成你自己的
  Username: aabbccddee
  # 媒体库服务器的密码, 改成你自己的
  Password: abcd123456789
  # 阻止播放的设备列表, 改成你自己的, 一行一个，也可以留空
  # 在app上选片后，本身设备也会进行串流播放，通过添加设备名称列表，比如你想选片的电视/手机，可以阻止它们串流播放，避免播放器和app两个同时播放
  # 该设备名称可在 emby服务器-设备 里看到，每个设备图片下面第一排就是设备名
  # 也可以emby里不点击播放按钮而是点击收藏/已播放按钮也可以启动影片。这样就可以不填BlockDevices，加载速度会比点击播放按钮然后阻止选片设备播放快一点
  BlockDevices:
    #- SONY XR-77A95L
  # 排除的文件扩展名, 一行一个
  # 格式命中的文件会直接用点击海报的那个设备播放，不会调用蓝光机
  ExcludeVideoExt:
    - mp4
    - mkv
  # 重复检测时间, 不要改
  RepeatFilterTimeout: 120


# 播放器配置
Player:
  # 引用的播放机执行器(默认oppo)
  # 可供选择的执行器请看程序所在目录的player文件夹下，使用player.<filename>.<classname>来命名
  # 目前有以下几种:
    # player.oppo.Oppo
    # player.pioneer.Pioneer
  Executor: player.oppo.Oppo
  # 播放机ip, 改成你自己的
  IP: 192.168.1.11
  # SMB认证信息(按照下方格式，配置至少2个不同的用户, 不用smb可以不改), pioneer 不需要(由于固件限制只能在播放机上先手动进入共享目录, nfs同理)
  Auth:
    - Username: username1
      Password: password1
    - Username: username2
      Password: password2
  # udp超时时间，不要改
  UdpTimeout: 10
  # 是否优先启用nfs, true为使用nfs, false为使用smb
  NFSPrefer: true

  # 检测到开机后发送的控制按键，只支持pionner,  支持的按键有：ok, left, right, up, down, return, home
  # 默认的按键是在要进入的共享盘和子目录都在第一个的情况，其他情况请自行修改,按键之间会自动插入1秒的延迟。
  # 如果插入多1 秒的延迟可以像下面一样发送一个空的 key.(这里在 ok键后面插入空key增加 1 秒延迟是因为电影界面进入稍慢)
  StartupKeySequence:
    - right
    - ok
    -
    - ok
    - down
    - ok
  # 开机发送按键的延迟时间， 开机后发现smb,nfs需要一定时间，等待一会儿防止进目录后smb/nfs还没有出现。
  # 根据自己网络发现速度调整。
  StartupWait: 5

  # 文件夹映射路径(不用的协议路径值可以留空)
  # 文件最后有路径配置说明, pioneer请参照 pioneer部分
  MappingPath:
    - Media: /path1
      SMB: /smb_host1
      NFS: /192.168.1.10/path1
    - Media: /path2
      SMB: /smb_host2
      NFS: /192.168.1.10/path2


# 电视配置
TV:
  # 引用的TV执行器(默认null不启用)
  # 可供选择的执行器请看程序所在目录的tv文件夹下，使用tv.<filename>.<classname>来命名
  # 目前有以下几种:
    # tv.sony_bravia.SonyBravia
    # tv.lg_webos.LGWebos
    # tv.oppo_hdmi.OppoHdmi
    # tv.hdfury.Hdfury
  Executor: null
  # 电视或其它设备的IP, 改成你自己的
  IP: 192.168.1.12
  # 电视控制识别码, 改成你自己的
  Key: "1234"
  # 播放机对应的HDMI口, 改成你自己的
  HDMI: 0
  # 播放结束后电视默认切换策略, 改成你自己的
  # null 执行默认策略, sony为跳转到emby app, Lg为返回原来页面
  # app=xxxx 例如"app=netflix" 代表返回netflix app
  # hdmi=x 例如"hdmi=3"代表返回 hdmi 3输入源
  # oppo系列，如果希望结束后停留在HDMI输入 则填写hdmi=1；如果选择HDMI输入直通 则填写pass=1。
  PlayStopUri: null


# AV功放配置
AV:
  # 引用的AV执行器(默认null不启用)
  # 可供选择的执行器请看程序所在目录的av文件夹下，使用av.<filename>.<classname>来命名
  # 目前有以下几种:
    # av.onkyo.Onkyo
  Executor: null
  # AV功放ip, 改成你自己的
  IP: 192.168.1.13
  # 播放开始时功放切换策略，改成你自己的,默认代表切换副输出以及切到bd
  PlayStartUri: hdmi-output-selector=out-sub&source=bd
  # 播放结束后功放切换策略，改成你自己的(默认代表切回主输出且切到tv-earc)
  PlayStopUri: hdmi-output-selector=out&source=tv


#### 路径配置说明 -> 开始
#
#
#
#  路径配置的分割符全部都要改为"/", 无论你是windows还是linux还是其他的，无论原来的分割符是"/","//","\","\\"甚至"\\\\"，都统一改为"/"
#  路径以/开头, 结尾不要/
#  如果你的媒体路径是windows的路径，比如是"d:/video/"这种不以"/"开头的，需要填写emby媒体库设置中 `（可选）共享的网络文件夹 `，详情看readme.md。
#  不是smb和nfs都必须配置, 你用的哪个就配置哪个，另一个配置可以直接留空, 当然你全配置也没问题
#
#
#   1. 保姆配置【推荐】(保姆配置需要有nas，然后所有影片需要放在指定目录)
  
#   a. 首先你需要有一个nas，然后新建一个根共享目录，比如/Video
#   b. 所有的影片必须全丢在/Video下，可以在/Video下建立多级目录分类存放(比如/Video/电修改分隔符, 影/..., /Video/电视剧/...)
#   c. emby媒体库里的地址, 直接在媒体库里复制出来(比如是/mnt/Video/电影),只写到根共享目录，去掉后面所有。填写到 Media中(例如"/mnt/Video")   
#   d. 打开oppo, 点击网络, 显示出来的smb设备和nfs设备就是路径开头,例如能看到一个smb设备"NAS466C", 一个nfs设备"192.168.1.10"
#   e. 继续点击，直到找到你nfs的根目录文件夹, 比如我点击的顺序是NAS466C -> Video
#     (注意中间还有一个图片/音乐/视频, 那个是oppo自己虚拟的，跟你的实际目录没关系，忽略掉)
#   f. 那么我的SMB路径就是 "/NAS466C/Video", nfs就是/192.168.1.10/Video
#   g. 以上配置就完成了，此时不管你的根目录下二级三级n级目录怎么配置怎么折腾，这个配置都不用变。此时你的配置为
#    - Media: /mnt/Video
#      SMB: /NAS466C/Video
#      NFS: /192.168.1.10/Video
#
#  比如我的文件夹分类是这样，建议你也按照类似的目录存放影片，省的路径配不明白
#
#  NAS466C/Video/
#  ├── 电影/
#  │   ├── 电影1
#  │   └── 电影2
#  ├── 电视剧/
#  │   ├── 电视剧1
#  │   ├── 电视剧2/
#  │   │   ├── 电视剧2-s01
#  │   │   └── 电视剧2-s02
#  ├── 动漫/
#      ├── 动漫1
#      └── 动漫2
#
#  2. 进阶配置(适合自己有自定义多根目录，且不愿意按照保姆配置调整的)
#
#  a. 首先获取emby媒体库里的地址(直接在媒体库里复制出来, 比如是/mnt/Video/电影),修改分隔符, 填写到 Media中(例如"/mnt/Video/电影")
#  b. 打开oppo, 点击网络, 显示出来的smb设备和nfs设备就是路径开头,例如能看到一个smb设备"NAS466C", 一个nfs设备"192.168.1.10"
#  c. 继续点击，直到找到你媒体库挂载的相同路径文件夹, 比如我点击的顺序是NAS466C -> Video -> 电影
#    (注意中间还有一个图片/音乐/视频, 那个是oppo自己虚拟的，跟你的实际目录没关系，忽略掉)
#  d. 那么我的SMB路径就是 "/NAS466C/Video/电影", nfs同理
#  e. 自己的媒体库有几个路径就配几个，确保每个媒体库路径都有正确的配置, 比如/NAS466C/Video/电视剧，/NAS466C/Video/动漫
#
#  3. 最优配置(适合会折腾的)
#
#  进阶配置后,你有以下3个目录
#  media："/mnt/Video/电影"
#  "SMB": "/NAS466C/Video/电影"
#  "NFS": "/192.168.1.10/Video/电影"
#
#  media："/mnt/Video/电视剧"
#  "SMB": "/NAS466C/Video/电视剧"
#  "NFS": "/192.168.1.10/Video/电视剧"
#
#  media："/mnt/Video/动漫"
#  "SMB": "/NAS466C/Video/动漫"
#  "NFS": "/192.168.1.10/Video/动漫"
#
#  看第一个目录, 可以发现后面路径都是/Video/电影, 相同的路径是可以约掉的
#  例如我可以约掉 "电视剧" 修改成
#  media："/mnt/Video"
#  "SMB": "/NAS466C/Video"
#  "NFS": "/192.168.1.10/Video"
#  甚至也可以继续约掉 "Video" 修改成
#  media："/mnt"
#  "SMB": "/NAS466C"
#  "NFS": "/192.168.1.10"
#
#  所以，配置的最优路径为
#  media："/mnt"
#  "SMB": "/NAS466C"
#  "NFS": "/192.168.1.10"
#
#  如果第一步进阶配置中配了很多个，而且很多前面都有重复的路径，适合简化一样
#
#### 路径配置说明 -> pioneer
# 不管 smb,或者 nfs, 只支持单一共享文件夹, 如果有多个共享文件夹, 建议合并成一个上层目录再通过 nfs 或者 smb 进行共享.
# 否则播放不同目录的电影都需要手动在播放机上切换到对应目录, 比较麻烦, 还可能切换的目录对不上就播放失败,导致黑屏, 只能重启播放机.
# 以 nfs 举例: media部分和上面 oppo一致,
# nfs部分去掉 ip后面以"-"开头那一节, 比如
# Media: /volume1/Media/Movie
# NFS: /10.0.1.4/Movie
# 在播放机看到的路径是 10.0.1.4/-volume1-Media/Movie, 去掉"-volume1-Media"就是/10.0.1.4/Movie
#
# 多个硬盘或多个分区如何用一个共享目录(可以有子目录, 但是最层用于共享的目录只能一个):
# 1. 比较笨的办法就是把蓝光片全部落到一个硬盘然后共享.
# 2. 多个硬盘组 raid, 把蓝光放到一个目录,然后共享.
# 3. 不用动数据,但是需要折腾(需要执行 linux命令)的方法, 以群辉nfs举例:
#   1) 新建一个共享文件夹什么都不放, 我的是在/volume4/BluRay.
#   2) 将之前的共享文件夹的 nfs关掉(目的是不让蓝光机看到, 防止挂载错目录).
#   3) 将每个其他盘的电影目录挂载到 /volume4/BluRay 目录下.
#      打开 DSM -> 控制面板 -> 计划任务 -> 新增 -> 触发的任务 -> 用户自定义脚本,
#      任务名称自定, 用户账号选 root, 事件选开机, 已开启勾选上,
#      点击任务设置标签,用户自定义脚本填写:
#      #!/bin/bash
#      mount --bind /volume1/Media/Movie/ /volume4/BluRay/Media
#      mount --bind /volume2/Share/Movie/ /volume4/BluRay/Share
#      保存, 保存后点击运行看是否成功, 正常应该在/volume4/BluRay/Media 目录看到 /volume1/Media/Movie/ 目录下的内容
#   mount 的目标目录可以随便指定(最好不要有特殊字符), 只要在 NFS填对应的就行
  # 配置好后，先启动播放机，点击电影，点击共享的目录比如我是 10.0.1.4,
  # 然后点击共享的目录， 我这里是 -volume4-BluRay (一定要先点到这里,不然点播放会黑屏只能重启)， 然后就可以正常使用 emby播放
#
#### 路径配置说明 -> 结束

```

##### 3.2.4 启动服务
服务可以24h启动，只要你不改配置文件，就不需要重启程序。期间开关播放器、电视、功放、海报墙都没有影响，建议装在能24h运行的设备上, 比如nas等。

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
- [ ] 如果想只允许蓝光机播放，记得把海报墙选片的app设备名添加到阻止列表，否则你会双端同时播放。
- [ ] 如果没有点播放按钮播片的强迫症，也不需要程序在播放出错时的提示信息->可以把阻止列表留空，然后使用点击emby的【喜欢】/【已观看】按钮来实现播放，在某些特定状况下可以加快载入时间以及配合atv上的infuse选片。
- [ ] 独立使用的设备只需要登录不同的emby用户就可以了


## 三、 开发者说明

见 `DEVELOPMENT.md`


## 四、感谢
灵感来源于[xnoppo](https://github.com/siberian-git/Xnoppo)
