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
    --hostname blurayposter \
    -v /blurayposter/config:/config \
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
            - /blurayposter/config:/config
        environment:
            - 'PUID=0'
            - 'PGID=0'
            - 'UMASK=000'
            - 'TZ=Asia/Shanghai'
        restart: always
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

- [ ] 配置参数参见配置文件

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
