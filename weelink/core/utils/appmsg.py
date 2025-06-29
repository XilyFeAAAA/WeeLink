def generate_appmsg_xml(
    appid, 
    title, 
    des, 
    url, 
    lowurl, 
    dataurl, 
    lowdataurl,
    fromusername,
    appname
):
    """
    生成微信分享的XML格式
    
    参数:
        appid: 微信公众号appid
        title: 文章标题
        des: 文章描述
        url: 文章链接
        lowurl: 低分辨率文章链接
        dataurl: 数据URL
        lowdataurl: 低分辨率数据URL
        fromusername: 发送者用户名
        appname: 应用名称
    
    返回:
        生成的XML字符串
    """
    xml = f"""
<appmsg appid="{appid}" sdkver="0">
    <title>{title}</title>
    <des>{des}</des>
    <action>view</action>
    <type>3</type>
    <showtype>0</showtype>
    <soundtype>0</soundtype>
    <mediatagname />
    <messageext />
    <messageaction />
    <content />
    <contentattr>0</contentattr>
    <url>{url}</url>
    <lowurl>{lowurl}</lowurl>
    <dataurl>{dataurl}</dataurl>
    <lowdataurl>{lowdataurl}</lowdataurl>
    <songalbumurl />
    <songlyric />
    <template_id />
    <appattach>
        <totallen>0</totallen>
        <attachid />
        <emoticonmd5></emoticonmd5>
        <fileext />
        <aeskey></aeskey>
    </appattach>
    <extinfo />
    <sourceusername />
    <sourcedisplayname />
    <thumburl />
    <md5 />
    <statextstr>GhQKEnd4NDg1YTk3Yzg0NDA4NmRjOQ==</statextstr>
    <tingListenItem>
        <listenId />
        <type>1</type>
        <listenItem />
    </tingListenItem>
    <musicShareItem>
        <mid />
        <mvSingerName />
        <mvAlbumName />
        <musicDuration>0</musicDuration>
    </musicShareItem>
    <finderLiveProductShare>
        <marketPrice>0</marketPrice>
        <sellingPrice>0</sellingPrice>
        <flashSalePrice>0</flashSalePrice>
        <flashSaleEndTime>0</flashSaleEndTime>
        <firstProductTagAspectRatioString>0.0</firstProductTagAspectRatioString>
        <secondProductTagAspectRatioString>0.0</secondProductTagAspectRatioString>
        <isPriceBeginShow>false</isPriceBeginShow>
    </finderLiveProductShare>
    <finderShopWindowShare />
</appmsg>
<fromusername>{fromusername}</fromusername>
<scene>0</scene>
<appinfo>
    <version>29</version>
    <appname>{appname}</appname>
</appinfo>
<commenturl />
    """
    
    return xml


def generate_forward_xml():
    return """
<appmsg appid="" sdkver="0">
    <title>xujin2的聊天记录</title>
    <des>xujin2: 你好
    xujin2: 哈哈</des>
    <action />
    <type>19</type>
    <showtype>0</showtype>
    <soundtype>0</soundtype>
    <mediatagname />
    <messageext />
    <messageaction />
    <content />
    <contentattr>0</contentattr>
    <url />
    <lowurl />
    <dataurl />
    <lowdataurl />
    <songalbumurl />
    <songlyric />
    <template_id />
    <appattach>
        <totallen>0</totallen>
        <attachid />
        <emoticonmd5></emoticonmd5>
        <fileext />
        <aeskey></aeskey>
    </appattach>
    <extinfo />
    <sourceusername />
    <sourcedisplayname />
    <thumburl />
    <md5 />
    <statextstr />
    <recorditem><![CDATA[<recordinfo>
        <fromscene>0</fromscene>
        <favcreatetime>1751161562</favcreatetime>
        <isChatRoom>0</isChatRoom>
        <title>xujin2的聊天记录</title>
        <desc>xujin2: 你好
xuji哈哈</desc>
        <datalist count="2">
            <dataitem datatype="1" dataid="270f88184bffc2c570330080d49bd77d" htmlid="270f88184bffc2c570330080d49bd77d">
                <sourcename>xujin2</sourcename>
                <sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/zDGTmzJRZTLcRI5rtPNblIGX1f6lJE5xIvWMPiaFDTqh7gRH8UbyTliaxfZGF96UybuyspWQ59XTmCkvthNdiaGYw/0</sourceheadurl>
                <sourcetime>2025-06-29 09:45</sourcetime>
                <datadesc>你好</datadesc>
                <srcMsgLocalid>188</srcMsgLocalid>
                <srcMsgCreateTime>1751161549</srcMsgCreateTime>
                <fromnewmsgid>2623464290536301973</fromnewmsgid>
                <dataitemsource>
                    <hashusername>8522c0c83379cfd879def26ab7658ba99004d495b379d43b49074ed34b9dde5f</hashusername>
                </dataitemsource>
            </dataitem>
            <dataitem datatype="1" dataid="19bcab4dbcb008b85b49a4c131d0c057" htmlid="19bcab4dbcb008b85b49a4c131d0c057">
                <sourcename>xujin2</sourcename>
                <sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/zDGTmzJRZTLcRI5rtPNblIGX1f6lJE5xIvWMPiaFDTqh7gRH8UbyTliaxfZGF96UybuyspWQ59XTmCkvthNdiaGYw/0</sourceheadurl>
                <sourcetime>2025-06-29 09:45</sourcetime>
                <datadesc>哈哈</datadesc>
                <srcMsgLocalid>189</srcMsgLocalid>
                <srcMsgCreateTime>1751161550</srcMsgCreateTime>
                <fromnewmsgid>6635912577648233950</fromnewmsgid>
                <dataitemsource>
                    <hashusername>8522c0c83379cfd879def26ab7658ba99004d495b379d43b49074ed34b9dde5f</hashusername>
                </dataitemsource>
            </dataitem>
        </datalist>
    </recordinfo>]]></recorditem>
</appmsg>
<fromusername>wxid_80s2igjuvsn422</fromusername>
<scene>0</scene>
<appinfo>
    <version>1</version>
    <appname />
</appinfo>
<commenturl />
    """