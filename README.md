# asmr.one downloader
## 简介
给出指定rj号，从![ASMR.ONE](https://asmr.one/)下载对应的音声。支持自动重连和断点下载。

## License
![GNU AGPL Version 3 Logo](https://www.gnu.org/graphics/agplv3-with-text-162x68.png)

asmr-one-downloader 是自由软件，遵循`Affero GNU 通用公共许可证第 3 版或任何后续版本`。你可以自由地使用、修改和分发该软件，但不提供任何明示或暗示的担保。有关详细信息，请参见 [Affero GNU 通用公共许可证](https://www.gnu.org/licenses/agpl-3.0.html)。

## 安装依赖
```bash
pip install -r requirements.txt

# 打开浏览器，下载 curl
firefox https://curl.se/download.html

# 解压到 /path/to/curl，然后加入 PATH 或者手动在参数指定
# 这里用 Windows 示范
wget https://curl.se/windows/dl-8.14.1_2/curl-8.14.1_2-win64-mingw.zip -O curl.zip
unzip curl.zip -d /path/to/curl/

# 如果一切正常的话，应该会出现以下目录结构
# /path/to/curl/curl-8.14.1_2-win64-mingw
#   - bin
#     - curl.exe
```

## 使用示例
```bash
# 获取音声的文件清单
python download_asmr.py 309477 --curl-path /path/to/curl/curl-8.14.1_2-win64-mingw/bin/curl.exe

# 输入后，等会你应该能看到一个文本编辑器窗口，要求你删除不想下载的项目（注：`#`开头的行为注释，不用管它）
# 删完后，保存并退出编辑器，然后程序就会开始下载
```

## 文档
文档是不可能写的，这辈子都不可能写的。经验表明，写了文档只会变成“代码一天一天改，文档一年不会动”的局面，反而误导人。

所以我真心推荐：有什么事直接看代码（代码的注释和函数的文档还是会更新的），或者复制代码问ai去吧（记得带上下文）。

## 贡献与开发
欢迎提出问题、改进或贡献代码。如果有任何问题或建议，您可以在 GitHub 上提 Issues，或者直接通过电子邮件联系开发者。

## 联系信息
如有任何问题或建议，请联系项目维护者 thiliapr。
- Email: thiliapr@tutanota.com

# 无关软件本身的广告
## Join the Blue Ribbon Online Free Speech Campaign!
![Blue Ribbon Campaign Logo](https://www.eff.org/files/brstrip.gif)

支持[Blue Ribbon Online 言论自由运动](https://www.eff.org/pages/blue-ribbon-campaign)！  
你可以通过向其[捐款](https://supporters.eff.org/donate)以表示支持。

## 支持自由软件运动
为什么要自由软件: [GNU 宣言](https://www.gnu.org/gnu/manifesto.html)

你可以通过以下方式支持自由软件运动:
- 向非自由程序或在线敌服务说不，哪怕只有一次，也会帮助自由软件。不和其他人使用它们会帮助更大。进一步，如果你告诉人们这是在捍卫自己的自由，那么帮助就更显著了。
- [帮助 GNU 工程和自由软件运动](https://www.gnu.org/help/help.html)
- [向 FSF 捐款](https://www.fsf.org/about/ways-to-donate/)