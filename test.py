import re
from lxml import etree

# 假设这是包含 HTML 内容的字符串
html_content = '''<div class="article">





        <div class="indent clearfix">
            <div class="subjectwrap clearfix">
                <div class="subject clearfix">





<div id="mainpic" class="">
    <a class="nbgnbg" href="https://movie.douban.com/subject/1292052/photos?type=R" title="点击看更多海报">
        <img src="https://img3.doubanio.com/view/photo/s_ratio_poster/public/p480747492.webp" title="点击看更多海报" alt="The Shawshank Redemption" rel="v:image">
   </a>
</div>




<div id="info">
        <span><span class="pl">导演</span>: <span class="attrs"><a href="https://www.douban.com/personage/27253735/" rel="v:directedBy">弗兰克·德拉邦特</a></span></span><br>
        <span><span class="pl">编剧</span>: <span class="attrs"><a href="https://www.douban.com/personage/27253735/">弗兰克·德拉邦特</a> / <a href="https://www.douban.com/personage/27255310/">斯蒂芬·金</a></span></span><br>
        <span><span class="pl">主演</span>: <span class="attrs"><span><a href="https://www.douban.com/personage/27260288/" rel="v:starring">蒂姆·罗宾斯</a> / </span><span><a href="https://www.douban.com/personage/27260301/" rel="v:starring">摩根·弗里曼</a> / </span><span><a href="https://www.douban.com/personage/27246934/" rel="v:starring">鲍勃·冈顿</a> / </span><span><a href="https://www.douban.com/personage/27205785/" rel="v:starring">威廉姆·赛德勒</a> / </span><span><a href="https://www.douban.com/personage/27219521/" rel="v:starring">克兰西·布朗</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27216303/" rel="v:starring">吉尔·贝罗斯</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27260625/" rel="v:starring">马克·罗斯顿</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27233634/" rel="v:starring">詹姆斯·惠特摩</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27293064/" rel="v:starring">杰弗里·德曼</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27279787/" rel="v:starring">拉里·布兰登伯格</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27304832/" rel="v:starring">尼尔·吉恩托利</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27546123/" rel="v:starring">布赖恩·利比</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27253983/" rel="v:starring">大卫·普罗瓦尔</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27546124/" rel="v:starring">约瑟夫·劳格诺</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27494501/" rel="v:starring">祖德·塞克利拉</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27219748/" rel="v:starring">保罗·麦克兰尼</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/30182674/" rel="v:starring">芮妮·布莱恩</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27289363/" rel="v:starring">阿方索·弗里曼</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27492451/" rel="v:starring">V·J·福斯特</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27206325/" rel="v:starring">弗兰克·梅德拉诺</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/30182677/" rel="v:starring">马克·迈尔斯</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27356038/" rel="v:starring">尼尔·萨默斯</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27253994/" rel="v:starring">耐德·巴拉米</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27206411/" rel="v:starring">布赖恩·戴拉特</a> / </span><span style="display: none;"><a href="https://www.douban.com/personage/27552265/" rel="v:starring">唐·麦克马纳斯</a></span><a href="javascript:;" class="more-attrs" title="显示更多">更多...</a></span></span><br>
        <span class="pl">类型:</span> <span property="v:genre">剧情</span> / <span property="v:genre">犯罪</span><br>

        <span class="pl">制片国家/地区:</span> 美国<br>
        <span class="pl">语言:</span> 英语<br>
        <span class="pl">上映日期:</span> <span property="v:initialReleaseDate" content="1994-09-10(多伦多电影节)">1994-09-10(多伦多电影节)</span> / <span property="v:initialReleaseDate" content="1994-10-14(美国)">1994-10-14(美国)</span><br>
        <span class="pl">片长:</span> <span property="v:runtime" content="142">142分钟</span><br>
        <span class="pl">又名:</span> 月黑高飞(港) / 刺激1995(台) / 地狱诺言 / 铁窗岁月 / 消香克的救赎<br>
        <span class="pl">IMDb:</span> tt0111161<br>

</div>
<script type="text/javascript">
$(function(){
    var limit = 5
    $('#info .attrs').each(function() {
        var $list = $(this).find('a')
        var $attrs = $(this)

        if($list.length > limit) {
            $attrs.empty()
            $list.each(function(idx) {
                if (idx+1 === $list.length) {
                    $('<span></span>').prepend($(this)).appendTo($attrs);
                } else {
                    $('<span> / </span>').prepend($(this)).appendTo($attrs);
                }
            })

            $attrs.append('<a href="javascript:;" class="more-attrs" title="显示更多">更多...</a>')
            $('.more-attrs').on('click', function() {
                $(this).parent().find('span').show()
                $(this).hide()
            })

            $attrs.find('span').slice(limit).hide()
        }
    })
})
</script>



                </div>



<link rel="stylesheet" href="https://img3.doubanio.com/cuphead/movie-static/download-output-image/index.7aaa3.css">
<div id="interest_sectl">
    <div class="rating_wrap clearbox" rel="v:rating">
        <div class="clearfix">
            <div class="rating_logo ll">
                豆瓣评分
            </div>
          <div class="output-btn-wrap rr" style="">
            <img src="https://img2.doubanio.com/cuphead/movie-static/pics/reference.png">
            <a class="download-output-image" href="#">引用</a>
          </div>
        </div>




<div class="rating_self clearfix" typeof="v:Rating">
    <strong class="ll rating_num" property="v:average">9.7</strong>
    <span property="v:best" content="10.0"></span>
    <div class="rating_right ">
        <div class="ll bigstar bigstar50"></div>
        <div class="rating_sum">
                <a href="comments" class="rating_people">
                    <span property="v:votes">3137118</span>人评价
                </a>
        </div>
    </div>
</div>
<div class="ratings-on-weight">

        <div class="item">

        <span class="stars5 starstop" title="力荐">
            5星
        </span>
        <div class="power" style="width:64px"></div>
        <span class="rating_per">85.7%</span>
        <br>
        </div>
        <div class="item">

        <span class="stars4 starstop" title="推荐">
            4星
        </span>
        <div class="power" style="width:9px"></div>
        <span class="rating_per">12.8%</span>
        <br>
        </div>
        <div class="item">

        <span class="stars3 starstop" title="还行">
            3星
        </span>
        <div class="power" style="width:0px"></div>
        <span class="rating_per">1.3%</span>
        <br>
        </div>
        <div class="item">

        <span class="stars2 starstop" title="较差">
            2星
        </span>
        <div class="power" style="width:0px"></div>
        <span class="rating_per">0.1%</span>
        <br>
        </div>
        <div class="item">

        <span class="stars1 starstop" title="很差">
            1星
        </span>
        <div class="power" style="width:0px"></div>
        <span class="rating_per">0.1%</span>
        <br>
        </div>
</div>

    </div>
        <div class="rating_betterthan">
            好于 <a href="/typerank?type_name=剧情&amp;type=11&amp;interval_id=100:90&amp;action=">99% 剧情片</a><br>
            好于 <a href="/typerank?type_name=犯罪&amp;type=3&amp;interval_id=100:90&amp;action=">99% 犯罪片</a><br>
        </div>
</div>
<script src="https://img1.doubanio.com/cuphead/movie-static/download-output-image/index.e9129.js"></script>



            </div>







<div id="interest_sect_level" class="clearfix">

            <a href="https://www.douban.com/reason=collectwish&amp;ck=" rel="nofollow" class="j a_show_login colbutt ll" name="pbtn-1292052-wish">
                <span>想看</span>
            </a>
            <a href="https://www.douban.com/reason=collectcollect&amp;ck=" rel="nofollow" class="j a_show_login colbutt ll" name="pbtn-1292052-collect">
                <span>看过</span>
            </a>
        <div class="ll j a_stars">


    评价:
    <span id="rating"> <span id="stars" data-solid="https://img1.doubanio.com/f/vendors/5a2327c04c0c231bced131ddf3f4467eb80c1c86/pics/rating_icons/star_onmouseover.png" data-hollow="https://img1.doubanio.com/f/vendors/2520c01967207a1735171056ec588c8c1257e5f8/pics/rating_icons/star_hollow_hover.png" data-solid-2x="https://img1.doubanio.com/f/vendors/7258904022439076d57303c3b06ad195bf1dc41a/pics/rating_icons/star_onmouseover@2x.png" data-hollow-2x="https://img1.doubanio.com/f/vendors/95cc2fa733221bb8edd28ad56a7145a5ad33383e/pics/rating_icons/star_hollow_hover@2x.png">

            <a href="https://www.douban.com/register?reason=rate" class="j a_show_login" name="pbtn-1292052-1">
            <img src="https://img1.doubanio.com/f/vendors/2520c01967207a1735171056ec588c8c1257e5f8/pics/rating_icons/star_hollow_hover.png" id="star1" width="16" height="16">
        </a>
            <a href="https://www.douban.com/register?reason=rate" class="j a_show_login" name="pbtn-1292052-2">
            <img src="https://img1.doubanio.com/f/vendors/2520c01967207a1735171056ec588c8c1257e5f8/pics/rating_icons/star_hollow_hover.png" id="star2" width="16" height="16">
        </a>
            <a href="https://www.douban.com/register?reason=rate" class="j a_show_login" name="pbtn-1292052-3">
            <img src="https://img1.doubanio.com/f/vendors/2520c01967207a1735171056ec588c8c1257e5f8/pics/rating_icons/star_hollow_hover.png" id="star3" width="16" height="16">
        </a>
            <a href="https://www.douban.com/register?reason=rate" class="j a_show_login" name="pbtn-1292052-4">
            <img src="https://img1.doubanio.com/f/vendors/2520c01967207a1735171056ec588c8c1257e5f8/pics/rating_icons/star_hollow_hover.png" id="star4" width="16" height="16">
        </a>
            <a href="https://www.douban.com/register?reason=rate" class="j a_show_login" name="pbtn-1292052-5">
            <img src="https://img1.doubanio.com/f/vendors/2520c01967207a1735171056ec588c8c1257e5f8/pics/rating_icons/star_hollow_hover.png" id="star5" width="16" height="16">
        </a>
    </span><span id="rateword" class="pl"></span>
    <input id="n_rating" type="hidden" value="">
    </span>

        </div>
</div>




















<div class="gtleft">
    <ul class="ul_subject_menu bicelink color_gray pt6 clearfix">




                  <li>
    <img src="https://img9.doubanio.com/cuphead/movie-static/pics/short-comment.gif">&nbsp;
        <a onclick="moreurl(this, {from:'mv_sbj_wr_cmnt_login'})" class="j a_show_login" href="https://www.douban.com/register?reason=review" rel="nofollow">写短评</a>
 </li>
                  <li>

    <img src="https://img1.doubanio.com/cuphead/movie-static/pics/add-review.gif">&nbsp;
        <a onclick="moreurl(this, {from:'mv_sbj_wr_rv_login'})" class="j a_show_login" href="https://www.douban.com/register?reason=review" rel="nofollow">写影评</a>
 </li>
                    <li>




    <span class="rec" id="电影-1292052">
    <a href="#" data-type="电影" data-url="https://movie.douban.com/subject/1292052/" data-desc="电影《肖申克的救赎 The Shawshank Redemption》 (来自豆瓣) " data-title="电影《肖申克的救赎 The Shawshank Redemption》 (来自豆瓣) " data-pic="https://img3.doubanio.com/view/photo/s_ratio_poster/public/p480747492.jpeg" class="bn-sharing ">
        分享到
    </a> &nbsp;&nbsp;
    </span>
    <link rel="stylesheet" href="https://img1.doubanio.com/f/vendors/e8a7261937da62636d22ca4c579efc4a4d759b1b/css/ui/dialog.css">
    <script src="https://img1.doubanio.com/f/vendors/f25ae221544f39046484a823776f3aa01769ee10/js/ui/dialog.js"></script>
    <script src="https://img1.doubanio.com/f/vendors/b6e0770163b1da14217b0f1ca39189d47b95f51f/js/lib/sharebutton.js"></script>
    <script src="https://img1.doubanio.com/cuphead/movie-static/libs/qrcode.min.js"></script>

  </li>


    </ul>

    <script type="text/javascript">
        $(function(){
            $(".ul_subject_menu li.rec .bn-sharing").bind("click", function(){
                $.get("/blank?sbj_page_click=bn_sharing");
            });
        });
    </script>
</div>










<link rel="stylesheet" href="https://img3.doubanio.com/cuphead/movie-static/mod/share.ee737.css" type="text/css">

<div class="rec-sec">
<span class="rec">
    <script id="movie-share" type="text/x-html-snippet">

    <form class="movie-share" action="/j/share" method="POST">
        <div class="clearfix form-bd">
            <div class="input-area">
                <textarea name="text" class="share-text" cols="72" data-mention-api="https://api.douban.com/shuo/in/complete?alt=xd&amp;callback=?"></textarea>
                <input type="hidden" name="target-id" value="1292052">
                <input type="hidden" name="target-type" value="0">
                <input type="hidden" name="title" value="肖申克的救赎 The Shawshank Redemption‎ (1994)">
                <input type="hidden" name="desc" value="导演 弗兰克·德拉邦特 主演 蒂姆·罗宾斯 / 摩根·弗里曼 / 美国 / 9.7分(3137118评价)">
                <input type="hidden" name="redir" value=""/>
                <div class="mentioned-highlighter"></div>
            </div>

            <div class="info-area">
                    <img class="media" src="https://img3.doubanio.com/view/photo/s_ratio_poster/public/p480747492.webp" />
                <strong>肖申克的救赎 The Shawshank Redemption‎ (1994)</strong>
                <p>导演 弗兰克·德拉邦特 主演 蒂姆·罗宾斯 / 摩根·弗里曼 / 美国 / 9.7分(3137118评价)</p>
                <p class="error server-error">&nbsp;</p>
            </div>
        </div>
        <div class="form-ft">
            <div class="form-ft-inner">




                <span class="avail-num-indicator">140</span>
                <span class="bn-flat">
                    <input type="submit" value="推荐" />
                </span>
            </div>
        </div>
    </form>

    <div id="suggest-mention-tmpl" style="display:none;">
        <ul>
            {{#users}}
            <li id="{{uid}}">
              <img src="{{avatar}}">{{{username}}}&nbsp;<span>({{{uid}}})</span>
            </li>
            {{/users}}
        </ul>
    </div>


    </script>


        <a href="/accounts/register?reason=recommend" class="j a_show_login lnk-sharing" share-id="1292052" data-mode="plain" data-name="肖申克的救赎 The Shawshank Redemption‎ (1994)" data-type="movie" data-desc="导演 弗兰克·德拉邦特 主演 蒂姆·罗宾斯 / 摩根·弗里曼 / 美国 / 9.7分(3137118评价)" data-href="https://movie.douban.com/subject/1292052/" data-image="https://img3.doubanio.com/view/photo/s_ratio_poster/public/p480747492.webp" data-properties="{}" data-redir="" data-text="" data-apikey="" data-curl="" data-count="10" data-object_kind="1002" data-object_id="1292052" data-target_type="rec" data-target_action="0" data-action_props="{&quot;subject_url&quot;:&quot;https:\/\/movie.douban.com\/subject\/1292052\/&quot;,&quot;subject_title&quot;:&quot;肖申克的救赎 The Shawshank Redemption‎ (1994)&quot;}">推荐</a>
</span>


</div>






            <script type="text/javascript">
                $(function() {
                    $('.collect_btn', '#interest_sect_level').each(function() {
                        Douban.init_collect_btn(this);
                    });
                    $('html').delegate(".indent .rec-sec .lnk-sharing", "click", function() {
                        moreurl(this, {
                            from : 'mv_sbj_db_share'
                        });
                    });
                });
            </script>
        </div>



    <div id="collect_form_1292052"></div>






<div class="related-info" style="margin-bottom:-10px;">
    <a name="intro"></a>




    <h2>
        <i class="">肖申克的救赎的剧情简介</i>
              · · · · · ·
    </h2>

            <div class="indent" id="link-report-intra">

                        <span class="short" style="display: none;">
                            <span property="v:summary">
                                    　　一场谋杀案使银行家安迪（蒂姆•罗宾斯 Tim Robbins 饰）蒙冤入狱，谋杀妻子及其情人的指控将囚禁他终生。在肖申克监狱的首次现身就让监狱“大哥”瑞德（摩根•弗里曼 Morgan Freeman 饰）对他另眼相看。瑞德帮助他搞到一把石锤和一幅女明星海报，两人渐成患难 之交。很快，安迪在监狱里大显其才，担当监狱图书管理员，并利用自己的金融知识帮助监狱官避税，引起了典狱长的注意，被招致麾下帮助典狱长洗黑钱。偶然一次，他得知一名新入狱的小偷能够作证帮他洗脱谋杀罪。燃起一丝希望的安迪找到了典狱长，希望他能帮自己翻案。阴险伪善的狱长假装答应安迪，背后却派人杀死小偷，让他唯一能合法出狱的希望泯灭。沮丧的安迪并没有绝望，在一个电闪雷鸣的风雨夜，一场暗藏几十年的越狱计划让他自我救赎，重获自由！老朋友瑞德在他的鼓舞和帮助下，也勇敢地奔向自由。
                                        <br>
                                    　　本片获得1995年奥...
                            </span>
                            <a href="javascript:void(0)" class="j a_show_full">(展开全部)</a>
                        </span>
                        <span class="all hidden" style="display: inline;">
                                　　一场谋杀案使银行家安迪（蒂姆•罗宾斯 Tim Robbins 饰）蒙冤入狱，谋杀妻子及其情人的指控将囚禁他终生。在肖申克监狱的首次现身就让监狱“大哥”瑞德（摩根•弗里曼 Morgan Freeman 饰）对他另眼相看。瑞德帮助他搞到一把石锤和一幅女明星海报，两人渐成患难 之交。很快，安迪在监狱里大显其才，担当监狱图书管理员，并利用自己的金融知识帮助监狱官避税，引起了典狱长的注意，被招致麾下帮助典狱长洗黑钱。偶然一次，他得知一名新入狱的小偷能够作证帮他洗脱谋杀罪。燃起一丝希望的安迪找到了典狱长，希望他能帮自己翻案。阴险伪善的狱长假装答应安迪，背后却派人杀死小偷，让他唯一能合法出狱的希望泯灭。沮丧的安迪并没有绝望，在一个电闪雷鸣的风雨夜，一场暗藏几十年的越狱计划让他自我救赎，重获自由！老朋友瑞德在他的鼓舞和帮助下，也勇敢地奔向自由。
                                    <br>
                                　　本片获得1995年奥斯卡10项提名，以及金球奖、土星奖等多项提名。
                        </span>
                        <span class="pl"><a href="https://movie.douban.com/help/movie#t0-qs">©豆瓣</a></span>
            </div>
</div>


    <div id="dale_movie_subject_banner_after_intro" ad-status="loaded"></div>







<link rel="stylesheet" href="https://img3.doubanio.com/cuphead/movie-static/celebrity/celebrities_section.610da.css">

<div id="celebrities" class="celebrities related-celebrities">


    <h2>
        <i class="">肖申克的救赎的演职员</i>
              · · · · · ·
            <span class="pl">
            (
                <a href="/subject/1292052/celebrities">全部 45</a>
            )
            </span>
    </h2>


  <ul class="celebrities-list from-subject __oneline">



  <li class="celebrity">


  <a href="https://www.douban.com/personage/27253735/" title="弗兰克·德拉邦特 Frank Darabont" class="">
      <div class="avatar" style="background-image: url(https://img1.doubanio.com/view/celebrity/m/public/p230.webp)">
    </div>
  </a>

    <div class="info">
      <span class="name"><a href="https://www.douban.com/personage/27253735/" title="弗兰克·德拉邦特 Frank Darabont" class="name">弗兰克·德拉邦特</a></span>

      <span class="role" title="导演">导演</span>

    </div>
  </li>





  <li class="celebrity">


  <a href="https://www.douban.com/personage/27260288/" title="蒂姆·罗宾斯 Tim Robbins" class="">
      <div class="avatar" style="background-image: url(https://img9.doubanio.com/view/celebrity/m/public/p17525.webp)">
    </div>
  </a>

    <div class="info">
      <span class="name"><a href="https://www.douban.com/personage/27260288/" title="蒂姆·罗宾斯 Tim Robbins" class="name">蒂姆·罗宾斯</a></span>

      <span class="role" title="饰 安迪·杜佛兰 Andy Dufresne">饰 安迪·杜佛兰 Andy Dufresne</span>

    </div>
  </li>





  <li class="celebrity">


  <a href="https://www.douban.com/personage/27260301/" title="摩根·弗里曼 Morgan Freeman" class="">
      <div class="avatar" style="background-image: url(https://img3.doubanio.com/view/celebrity/m/public/p34642.webp)">
    </div>
  </a>

    <div class="info">
      <span class="name"><a href="https://www.douban.com/personage/27260301/" title="摩根·弗里曼 Morgan Freeman" class="name">摩根·弗里曼</a></span>

      <span class="role" title="饰 艾利斯·波伊德·“瑞德”·瑞丁 Ellis Boyd 'Red' Redding">饰 艾利斯·波伊德·“瑞德”·瑞丁 Ellis Boyd 'Red' Redding</span>

    </div>
  </li>





  <li class="celebrity">


  <a href="https://www.douban.com/personage/27246934/" title="鲍勃·冈顿 Bob Gunton" class="">
      <div class="avatar" style="background-image: url(https://img3.doubanio.com/view/celebrity/m/public/p5837.webp)">
    </div>
  </a>

    <div class="info">
      <span class="name"><a href="https://www.douban.com/personage/27246934/" title="鲍勃·冈顿 Bob Gunton" class="name">鲍勃·冈顿</a></span>

      <span class="role" title="饰 监狱长山姆·诺顿 Warden Norton">饰 监狱长山姆·诺顿 Warden Norton</span>

    </div>
  </li>





  <li class="celebrity">


  <a href="https://www.douban.com/personage/27205785/" title="威廉姆·赛德勒 William Sadler" class="">
      <div class="avatar" style="background-image: url(https://img3.doubanio.com/view/celebrity/m/public/p7827.webp)">
    </div>
  </a>

    <div class="info">
      <span class="name"><a href="https://www.douban.com/personage/27205785/" title="威廉姆·赛德勒 William Sadler" class="name">威廉姆·赛德勒</a></span>

      <span class="role" title="饰 海伍德 Heywood">饰 海伍德 Heywood</span>

    </div>
  </li>





  <li class="celebrity">


  <a href="https://www.douban.com/personage/27219521/" title="克兰西·布朗 Clancy Brown" class="">
      <div class="avatar" style="background-image: url(https://img1.doubanio.com/view/personage/m/public/af679543a3cc6a54afe91023a73b7348.jpg)">
    </div>
  </a>

    <div class="info">
      <span class="name"><a href="https://www.douban.com/personage/27219521/" title="克兰西·布朗 Clancy Brown" class="name">克兰西·布朗</a></span>

      <span class="role" title="饰 上尉哈德利 Captain Hadley">饰 上尉哈德利 Captain Hadley</span>

    </div>
  </li>


  </ul>
</div>





<link rel="stylesheet" href="https://img1.doubanio.com/f/verify/a5bc0bc0aea4221d751bc4809fd4b0a1075ad25e/entry_creator/dist/author_subject/style.css">
<div id="author_subject" class="author-wrapper"><div class="author-subject"></div></div>
<script type="text/javascript">
    var answerObj = {
      ISALL: 'False',
      TYPE: 'movie',
      SUBJECT_ID: '1292052',
      USER_ID: 'None'
    }
</script>
<script type="text/javascript" src="https://img1.doubanio.com/f/vendors/bd6325a12f40c34cbf2668aafafb4ccd60deab7e/vendors.js"></script>
<script type="text/javascript" src="https://img1.doubanio.com/f/vendors/6242a400cfd25992da35ace060e58f160efc9c50/shared_rc.js"></script>
<script type="text/javascript" src="https://img1.doubanio.com/f/verify/67e13c04cd5519da7657f708714ba1e7eab8d342/entry_creator/dist/author_subject/index.js"></script>







<link rel="stylesheet" href="https://img1.doubanio.com/cuphead/movie-static/subject/photos_section.45abd.css">






    <div id="related-pic" class="related-pic">



    <h2>
        <i class="">肖申克的救赎的视频和图片</i>
              · · · · · ·
            <span class="pl">
            (
                <a href="https://movie.douban.com/subject/1292052/trailer#trailer">预告片2</a>&nbsp;|&nbsp;<a href="https://movie.douban.com/subject/1292052/trailer#short_video">视频评论3</a>&nbsp;|&nbsp;<a href="https://movie.douban.com/subject/1292052/all_photos">图片1087</a>&nbsp;·&nbsp;<a href="https://movie.douban.com/subject/1292052/mupload">添加</a>
            )
            </span>
    </h2>


        <ul class="related-pic-bd  wide_videos">
                <li class="label-trailer">
                    <a class="related-pic-video" href="https://movie.douban.com/trailer/259258/#content" title="预告片" style="background-image:url(https://img1.doubanio.com/img/trailer/medium/2587159379.jpg)">
                        <p class="type-title">预告片</p>
                    </a>
                </li>

                <li class="label-short-video">
                    <a class="related-pic-video" href="https://movie.douban.com/video/106436/" title="视频评论" style="background-image:url(https://img1.doubanio.com/view/photo/photo/public/p2616862940.webp?)">
                        <p class="type-title">视频评论</p>
                    </a>
                </li>
                <li>
                    <a href="https://movie.douban.com/photos/photo/2635663142/"><img src="https://img3.doubanio.com/view/photo/sqxs/public/p2635663142.webp" alt="图片"></a>
                </li>
                <li>
                    <a href="https://movie.douban.com/photos/photo/456482220/"><img src="https://img1.doubanio.com/view/photo/sqxs/public/p456482220.webp" alt="图片"></a>
                </li>
        </ul>
    </div>









<style type="text/css">
.award li { display: inline; margin-right: 5px }
.awards { margin-bottom: 20px }
.awards h2 { background: none; color: #000; font-size: 14px; padding-bottom: 5px; margin-bottom: 8px; border-bottom: 1px dashed #dddddd }
.awards .year { color: #666666; margin-left: -5px }
.mod { margin-bottom: 25px }
.mod .hd { margin-bottom: 10px }
.mod .hd h2 {margin:24px 0 3px 0}
</style>


<div class="mod">
    <div class="hd">

    <h2>
        <i class="">肖申克的救赎的获奖情况</i>
              · · · · · ·
            <span class="pl">
            (
                <a href="https://movie.douban.com/subject/1292052/awards/">全部</a>
            )
            </span>
    </h2>

    </div>

        <ul class="award">
            <li>
                <a href="https://movie.douban.com/awards/Oscar/67/">第67届奥斯卡金像奖</a>
            </li>
            <li>最佳影片(提名)</li>
            <li><a href="https://www.douban.com/personage/27519475/" target="_blank">妮基·马文</a></li>
        </ul>

        <ul class="award">
            <li>
                <a href="https://movie.douban.com/awards/golden-globes/52/">第52届金球奖</a>
            </li>
            <li>电影类 剧情片最佳男主角(提名)</li>
            <li><a href="https://www.douban.com/personage/27260301/" target="_blank">摩根·弗里曼</a></li>
        </ul>

        <ul class="award">
            <li>
                <a href="https://movie.douban.com/awards/jap/19/">第19届日本电影学院奖</a>
            </li>
            <li>最佳外语片</li>
            <li></li>
        </ul>
</div>







<link rel="stylesheet" href="https://img9.doubanio.com/cuphead/movie-static/subject/recommendations.00756.css">




    <div id="recommendations" class="">


    <h2>
        <i class="">喜欢这部电影的人也喜欢</i>
              · · · · · ·
    </h2>



    <div class="recommendations-bd">
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/1292720/?from=subject-page">
                    <img src="https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2372307693.webp" alt="阿甘正传" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/1292720/?from=subject-page" class="">阿甘正传</a>
                <span class="subject-rate">9.5</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/1292064/?from=subject-page">
                    <img src="https://img3.doubanio.com/view/photo/s_ratio_poster/public/p479682972.webp" alt="楚门的世界" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/1292064/?from=subject-page" class="">楚门的世界</a>
                <span class="subject-rate">9.4</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/1849031/?from=subject-page">
                    <img src="https://img1.doubanio.com/view/photo/s_ratio_poster/public/p1312700628.webp" alt="当幸福来敲门" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/1849031/?from=subject-page" class="">当幸福来敲门</a>
                <span class="subject-rate">9.2</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/1292365/?from=subject-page">
                    <img src="https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2597919477.webp" alt="活着" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/1292365/?from=subject-page" class="">活着</a>
                <span class="subject-rate">9.3</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/26387939/?from=subject-page">
                    <img src="https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2401676338.webp" alt="摔跤吧！爸爸" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/26387939/?from=subject-page" class="">摔跤吧！爸爸</a>
                <span class="subject-rate">9.0</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/26752088/?from=subject-page">
                    <img src="https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2561305376.webp" alt="我不是药神" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/26752088/?from=subject-page" class="">我不是药神</a>
                <span class="subject-rate">9.0</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/1292656/?from=subject-page">
                    <img src="https://img9.doubanio.com/view/photo/s_ratio_poster/public/p480965695.webp" alt="心灵捕手" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/1292656/?from=subject-page" class="">心灵捕手</a>
                <span class="subject-rate">9.0</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/3793023/?from=subject-page">
                    <img src="https://img2.doubanio.com/view/photo/s_ratio_poster/public/p579729551.webp" alt="三傻大闹宝莱坞" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/3793023/?from=subject-page" class="">三傻大闹宝莱坞</a>
                <span class="subject-rate">9.2</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/1298624/?from=subject-page">
                    <img src="https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2550757929.webp" alt="闻香识女人" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/1298624/?from=subject-page" class="">闻香识女人</a>
                <span class="subject-rate">9.1</span>
            </dd>
        </dl>
        <dl class="">
            <dt>
                <a href="https://movie.douban.com/subject/1295644/?from=subject-page">
                    <img src="https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2913554676.webp" alt="这个杀手不太冷" class="">
                </a>
            </dt>
            <dd>
                <a href="https://movie.douban.com/subject/1295644/?from=subject-page" class="">这个杀手不太冷</a>
                <span class="subject-rate">9.4</span>
            </dd>
        </dl>
    </div>

    </div>








<script type="text/x-handlebar-tmpl" id="comment-tmpl">
    <div class="dummy-fold">
        {{#each comments}}
        <div class="comment-item" data-cid="id">
            <div class="comment">
                <h3>
                    <span class="comment-vote">
                            <span class="votes">{{votes}}</span>
                        <input value="{{id}}" type="hidden"/>
                        <a href="javascript:;" class="j {{#if ../if_logined}}vote-comment{{else}}a_show_login{{/if}}">有用</a>
                    </span>
                    <span class="comment-info">
                        <a href="{{user.path}}" class="">{{user.name}}</a>
                        {{#if rating}}
                        <span class="allstar{{rating}}0 rating" title="{{rating_word}}"></span>
                        {{/if}}
                        <span>
                            {{time}}
                        </span>
                        <p> {{content_tmpl content}} </p>
                    </span>
            </div>
        </div>
        {{/each}}
    </div>
</script>













    <link rel="stylesheet" href="https://img1.doubanio.com/f/vendors/d63a579a99fd372b4398731a279a1382e6eac71e/subject-comments/comments-section.css">

    <div id="comments-section">
        <div class="mod-hd">


        <a class="comment_btn j a_show_login" href="https://www.douban.com/register?reason=review" rel="nofollow">
            <span>我要写短评</span>
        </a>


    <h2>
        <i class="">肖申克的救赎的短评</i>
              · · · · · ·
            <span class="pl">
            (
                <a href="https://movie.douban.com/subject/1292052/comments?status=P">全部 613286 条</a>
            )
            </span>
    </h2>

        </div>




        <div class="mod-bd">

        <div class="tab-hd">
                        <a id="hot-comments-tab" href="comments" data-id="hot" class="on">热门</a>&nbsp;/&nbsp;
                        <a id="new-comments-tab" href="comments?sort=time" data-id="new" class="j a_show_login">最新</a>&nbsp;/&nbsp;
                        <a id="following-comments-tab" href="comments?sort=follows" data-id="following" class="j a_show_login">好友</a>
        </div>

    <div class="tab-bd">
        <div id="hot-comments" class="tab">




        <div class="comment-item " data-cid="477351">


    <div class="comment">
        <h3>
            <span class="comment-vote">
                    <span class="votes vote-count">22460</span>

                    <input value="477351" type="hidden">
                    <a href="javascript:;" data-id="477351" class="j a_show_login" onclick="">有用</a>

                <!-- 删除短评 -->
            </span>
            <span class="comment-info">
                <a href="https://www.douban.com/people/whiterhinoceros/" class="">犀牛</a>
                    <span>看过</span>
                    <span class="allstar50 rating" title="力荐"></span>
                <span class="comment-time " title="2005-10-28 00:28:07">
                    2005-10-28 00:28:07
                </span>
                <span class="comment-location"></span>
            </span>
        </h3>
        <p class=" comment-content">

                <span class="short">当年的奥斯卡颁奖礼上，被如日中天的《阿甘正传》掩盖了它的光彩，而随着时间的推移，这部电影在越来越多的人们心中的地位已超越了《阿甘》。每当现实令我疲惫得产生无力感，翻出这张碟，就重获力量。毫无疑问，本片位列男人必看的电影前三名！回顾那一段经典台词：“有的人的羽翼是如此光辉，即使世界上最黑暗的牢狱，也无法长久地将他围困！”</span>
        </p>
        <div class="comment-report" data-url="https://movie.douban.com/subject/1292052/?comment_id=477351"></div>
    </div>
    <script>
        (function(){
            $("body").delegate(".comment-item", 'mouseenter mouseleave', function (e) {
                switch (e.type) {
                    case "mouseenter":
                    $(this).find(".comment-report").css('visibility', 'visible');
                    break;
                    case "mouseleave":
                    $(this).find(".comment-report").css('visibility', 'hidden');
                    break;
                }
            });
        })()
    </script>

        </div>

        <div class="comment-item " data-cid="32514679">


    <div class="comment">
        <h3>
            <span class="comment-vote">
                    <span class="votes vote-count">24781</span>

                    <input value="32514679" type="hidden">
                    <a href="javascript:;" data-id="32514679" class="j a_show_login" onclick="">有用</a>

                <!-- 删除短评 -->
            </span>
            <span class="comment-info">
                <a href="https://www.douban.com/people/ruxiaoguo/" class="">如小果</a>
                    <span>看过</span>
                    <span class="allstar50 rating" title="力荐"></span>
                <span class="comment-time " title="2008-02-27 21:43:23">
                    2008-02-27 21:43:23
                </span>
                <span class="comment-location"></span>
            </span>
        </h3>
        <p class=" comment-content">

                <span class="short">恐惧让你沦为囚犯，希望让你重获自由。——《肖申克的救赎》</span>
        </p>
        <div class="comment-report" data-url="https://movie.douban.com/subject/1292052/?comment_id=32514679"></div>
    </div>
    <script>
        (function(){
            $("body").delegate(".comment-item", 'mouseenter mouseleave', function (e) {
                switch (e.type) {
                    case "mouseenter":
                    $(this).find(".comment-report").css('visibility', 'visible');
                    break;
                    case "mouseleave":
                    $(this).find(".comment-report").css('visibility', 'hidden');
                    break;
                }
            });
        })()
    </script>

        </div>

        <div class="comment-item " data-cid="40114704">


    <div class="comment">
        <h3>
            <span class="comment-vote">
                    <span class="votes vote-count">12296</span>

                    <input value="40114704" type="hidden">
                    <a href="javascript:;" data-id="40114704" class="j a_show_login" onclick="">有用</a>

                <!-- 删除短评 -->
            </span>
            <span class="comment-info">
                <a href="https://www.douban.com/people/eve42/" class="">Eve|Classified</a>
                    <span>看过</span>
                    <span class="allstar50 rating" title="力荐"></span>
                <span class="comment-time " title="2008-05-09 23:15:34">
                    2008-05-09 23:15:34
                </span>
                <span class="comment-location"></span>
            </span>
        </h3>
        <p class=" comment-content">

                <span class="short">“这是一部男人必看的电影。”人人都这么说。但单纯从性别区分，就会让这电影变狭隘。《肖申克的救赎》突破了男人电影的局限，通篇几乎充满令人难以置信的温馨基调，而电影里最伟大的主题是“希望”。
当我们无奈地遇到了如同肖申克一般囚禁了心灵自由的那种囹圄，我们是无奈的老布鲁克，灰心的瑞德，还是智慧的安迪？运用智慧，信任希望，并且勇敢面对恐惧心理，去打败它？
经典的电影之所以经典，因为他们都在做同一件事—...</span>
                <span class="full">“这是一部男人必看的电影。”人人都这么说。但单纯从性别区分，就会让这电影变狭隘。《肖申克的救赎》突破了男人电影的局限，通篇几乎充满令人难以置信的温馨基调，而电影里最伟大的主题是“希望”。
当我们无奈地遇到了如同肖申克一般囚禁了心灵自由的那种囹圄，我们是无奈的老布鲁克，灰心的瑞德，还是智慧的安迪？运用智慧，信任希望，并且勇敢面对恐惧心理，去打败它？
经典的电影之所以经典，因为他们都在做同一件事——让你从不同的角度来欣赏希望的美好。</span>
                <span class="expand">(<a href="javascript:;">展开</a>)</span>
        </p>
        <div class="comment-report" data-url="https://movie.douban.com/subject/1292052/?comment_id=40114704"></div>
    </div>
    <script>
        (function(){
            $("body").delegate(".comment-item", 'mouseenter mouseleave', function (e) {
                switch (e.type) {
                    case "mouseenter":
                    $(this).find(".comment-report").css('visibility', 'visible');
                    break;
                    case "mouseleave":
                    $(this).find(".comment-report").css('visibility', 'hidden');
                    break;
                }
            });
        })()
    </script>

        </div>

        <div class="comment-item " data-cid="233959689">


    <div class="comment">
        <h3>
            <span class="comment-vote">
                    <span class="votes vote-count">18082</span>

                    <input value="233959689" type="hidden">
                    <a href="javascript:;" data-id="233959689" class="j a_show_login" onclick="">有用</a>

                <!-- 删除短评 -->
            </span>
            <span class="comment-info">
                <a href="https://www.douban.com/people/madeinds/" class="">711|湯不餓</a>
                    <span>看过</span>
                    <span class="allstar50 rating" title="力荐"></span>
                <span class="comment-time " title="2010-03-27 21:30:29">
                    2010-03-27 21:30:29
                </span>
                <span class="comment-location"></span>
            </span>
        </h3>
        <p class=" comment-content">

                <span class="short">策划了19年的私奔……</span>
        </p>
        <div class="comment-report" data-url="https://movie.douban.com/subject/1292052/?comment_id=233959689"></div>
    </div>
    <script>
        (function(){
            $("body").delegate(".comment-item", 'mouseenter mouseleave', function (e) {
                switch (e.type) {
                    case "mouseenter":
                    $(this).find(".comment-report").css('visibility', 'visible');
                    break;
                    case "mouseleave":
                    $(this).find(".comment-report").css('visibility', 'hidden');
                    break;
                }
            });
        })()
    </script>

        </div>

        <div class="comment-item " data-cid="3728484">


    <div class="comment">
        <h3>
            <span class="comment-vote">
                    <span class="votes vote-count">13556</span>

                    <input value="3728484" type="hidden">
                    <a href="javascript:;" data-id="3728484" class="j a_show_login" onclick="">有用</a>

                <!-- 删除短评 -->
            </span>
            <span class="comment-info">
                <a href="https://www.douban.com/people/aixiaoke/" class="">艾小柯</a>
                    <span>看过</span>
                    <span class="allstar50 rating" title="力荐"></span>
                <span class="comment-time " title="2006-06-20 03:18:55">
                    2006-06-20 03:18:55
                </span>
                <span class="comment-location"></span>
            </span>
        </h3>
        <p class=" comment-content">

                <span class="short">关于希望最强有力的注释。</span>
        </p>
        <div class="comment-report" data-url="https://movie.douban.com/subject/1292052/?comment_id=3728484"></div>
    </div>
    <script>
        (function(){
            $("body").delegate(".comment-item", 'mouseenter mouseleave', function (e) {
                switch (e.type) {
                    case "mouseenter":
                    $(this).find(".comment-report").css('visibility', 'visible');
                    break;
                    case "mouseleave":
                    $(this).find(".comment-report").css('visibility', 'hidden');
                    break;
                }
            });
        })()
    </script>

        </div>





                    &gt; <a href="comments?sort=new_score&amp;status=P">
                        更多短评
                            613286条
                    </a>
        </div>
        <div id="new-comments" class="tab">
            <div id="normal">
            </div>
            <div class="fold-hd hide">
                <a class="qa" href="/help/opinion#t2-q0" target="_blank">为什么被折叠？</a>
                <a class="btn-unfold" href="#">有一些短评被折叠了</a>
                <div class="qa-tip">
                    评论被折叠，是因为发布这条评论的账号行为异常。评论仍可以被展开阅读，对发布人的账号不造成其他影响。如果认为有问题，可以<a href="https://help.douban.com/help/ask?category=movie">联系</a>豆瓣电影。
                </div>
            </div>
            <div class="fold-bd">
            </div>
            <span id="total-num"></span>
        </div>
        <div id="following-comments" class="tab">






        <div class="comment-item">
            你关注的人还没写过短评
        </div>

        </div>
    </div>




            <script src="https://img1.doubanio.com/f/vendors/6eba6f43fb7592ab783e390f654c0d6a96b1598e/subject-comments/comments-section.js"></script>
            <script>
                $(function () {
                    if (window.SUBJECT_COMMENTS_SECTION) {
                        // tab handler
                        SUBJECT_COMMENTS_SECTION.createTabHandler();
                        // expand handler
                        SUBJECT_COMMENTS_SECTION.createExpandHandler({
                            root: document.getElementById('comments-section'),
                        });
                        // vote handler
                        SUBJECT_COMMENTS_SECTION.createVoteHandler({
                            api: '/j/comment/vote',
                            root: document.getElementById('comments-section'),
                            voteSelector: '.vote-comment',
                            textSelector: '.vote-count',
                            is_released: "true",
                            alert_text: "该电影还未上映，不能投票噢",
                            afterVote: function (elem) {
                                var parentNode = elem.parentNode;
                                var successElem = document.createElement('span');
                                successElem.innerHTML = '已投票';
                                parentNode.removeChild(elem);
                                parentNode.appendChild(successElem);
                            }
                        });
                    }
                });
            </script>
        </div>
    </div>



<!--        此处是挂载其他页面，不是注释！不是注释！不是注释！-->



<link rel="stylesheet" href="https://img1.doubanio.com/misc/mixed_static/321aad04ff83871e.css">

    <section id="reviews-wrapper" class="reviews mod movie-content">
        <header>

                <a href="new_review" rel="nofollow" class="create-review comment_btn " data-isverify="False" data-verify-url="https://www.douban.com/accounts/phone/verify?redir=http://movie.douban.com/subject/1292052/new_review">
                    <span>我要写影评</span>
                </a>
            <h2>
                    肖申克的救赎的影评 · · · · · ·

                    <span class="pl">( <a href="reviews">全部 13463 条</a> )</span>
            </h2>
        </header>


            <div class="review_filter">
                                <span class="link"><a href="javascript:;;" class="cur" data-sort="">热门</a></span>
            </div>
            <script>
                var cur_sort = '';
                $('#reviews-wrapper .review_filter a').on('click', function () {
                    var sort = $(this).data('sort');
                    if(sort === cur_sort) return;

                    if(sort === 'follow' && true){
                        window.location.href = '//www.douban.com/accounts/login?source=movie';
                        return;
                    }

                    if($('#reviews-wrapper .review_filter').data('doing')) return;
                    $('#reviews-wrapper .review_filter').data('doing', true);

                    cur_sort = sort;

                    $('#reviews-wrapper .review_filter a').removeClass('cur');
                    $(this).addClass('cur');

                    $.getJSON('reviews', { sort: sort }, function(res) {
                        $('#reviews-wrapper .review-list').remove();
                        $('#reviews-wrapper [href="reviews?sort=follow"]').parent().remove();
                        $('#reviews-wrapper .review_filter').after(res.html);
                        $('#reviews-wrapper .review_filter').data('doing', false);
                        $('#reviews-wrapper .review_filter').removeData('doing');

                        if (res.count === 0) {
                            $('#reviews-wrapper .review-list').html('<span class="no-review">你关注的人还没写过长评</span>');
                        }
                    });
                });
            </script>






<div class="review-list  ">





    <div data-cid="1000369">
        <div class="main review-item" id="1000369">



    <header class="main-hd">
        <a href="https://www.douban.com/people/bighead/" class="avator">
            <img width="24" height="24" src="https://img3.doubanio.com/icon/u1000152-23.jpg">
        </a>

        <a href="https://www.douban.com/people/bighead/" class="name">大头绿豆</a>

            <span class="allstar50 main-title-rating" title="力荐"></span>

        <span content="2005-05-12" class="main-meta">2005-05-12 20:44:13</span>


    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/1000369/">十年·肖申克的救赎</a></h2>

                <div id="review_1000369_short" class="review-short" data-rid="1000369">
                    <div class="short-content">

                        距离斯蒂芬·金（Stephen King）和德拉邦特（Frank Darabont）们缔造这部伟大的作品已经有十年了。我知道美好的东西想必大家都能感受，但是很抱歉，我的聒噪仍将一如既往。 在我眼里，肖申克的救赎与信念、自由和友谊有关。 ［1］信 念 瑞德（Red）说，希望是危险的东西，是精...

                        &nbsp;(<a href="javascript:;" id="toggle-1000369-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_1000369_full" class="hidden">
                    <div id="review_1000369_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="1000369" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-1000369">
                                18725
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="1000369" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-1000369">
                                733
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/1000369/#comments" class="reply ">1056回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>



    <div data-cid="1001258">
        <div class="main review-item" id="1001258">



    <header class="main-hd">
        <a href="https://www.douban.com/people/lazywormzhao/" class="avator">
            <img width="24" height="24" src="https://img3.doubanio.com/icon/u1000564-2.jpg">
        </a>

        <a href="https://www.douban.com/people/lazywormzhao/" class="name">隱居雲上</a>

            <span class="allstar50 main-title-rating" title="力荐"></span>

        <span content="2005-07-12" class="main-meta">2005-07-12 11:23:39</span>


    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/1001258/">终于找到了郁闷人生的原因――观《肖申克的救赎》有感</a></h2>

                <div id="review_1001258_short" class="review-short" data-rid="1001258">
                    <div class="short-content">

                         周末看了一部美国影片《肖申克的救赎》（《The Shawshank Redemption》） 讲的是一位因冤案入狱的年轻银行家在牢中如何追寻自由的故事。 不同的人看同样的影片可能都有不同的感受。对于目前无力改变现状的我，看完这部影片后最深的感受就是：才华、毅力两样，是任何人在任何境...

                        &nbsp;(<a href="javascript:;" id="toggle-1001258-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_1001258_full" class="hidden">
                    <div id="review_1001258_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="1001258" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-1001258">
                                12951
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="1001258" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-1001258">
                                799
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/1001258/#comments" class="reply ">1350回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>



    <div data-cid="10350620">
        <div class="main review-item" id="10350620">



    <header class="main-hd">
        <a href="https://www.douban.com/people/58718941/" class="avator">
            <img width="24" height="24" src="https://img3.doubanio.com/icon/u58718941-17.jpg">
        </a>

        <a href="https://www.douban.com/people/58718941/" class="name">泠十三</a>

            <span class="allstar50 main-title-rating" title="力荐"></span>

        <span content="2019-07-29" class="main-meta">2019-07-29 12:54:13</span>

            <a class="rel-topic" target="_blank" href="//www.douban.com/gallery/topic/《肖申克的救赎》到底“救赎”了什么？">#《肖申克的救赎》到底“救赎”了什么？</a>

    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/10350620/">《肖申克的救赎》到底“救赎”了什么？</a></h2>

                <div id="review_10350620_short" class="review-short" data-rid="10350620">
                    <div class="short-content">
                            <p class="spoiler-tip">这篇影评可能有剧透</p>

                        原文转自： 我们都是肖申克里等待救赎的灵魂 01 “你来对地方了，这里人人都无罪。” Red笑着对Andy说。 这个杀妻的银行家，因谋杀妻子和她的情夫，被判处终身监禁。 尽管被关进了这座叫肖申克的监狱，他依然极力否认。 犯人经过审判，被判处有罪，他们被关进监狱。 在这里，脱...

                        &nbsp;(<a href="javascript:;" id="toggle-10350620-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_10350620_full" class="hidden">
                    <div id="review_10350620_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="10350620" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-10350620">
                                6043
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="10350620" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-10350620">
                                17
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/10350620/#comments" class="reply ">173回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>



    <div data-cid="9259304">
        <div class="main review-item" id="9259304">



    <header class="main-hd">
        <a href="https://www.douban.com/people/yalindongdong/" class="avator">
            <img width="24" height="24" src="https://img9.doubanio.com/icon/u2586116-96.jpg">
        </a>

        <a href="https://www.douban.com/people/yalindongdong/" class="name">方枪枪</a>

            <span class="allstar50 main-title-rating" title="力荐"></span>

        <span content="2018-03-30" class="main-meta">2018-03-30 16:46:05</span>

            <a class="rel-topic" target="_blank" href="//www.douban.com/gallery/topic/为何《肖申克的救赎》在IMDb和豆瓣都能排第一？">#为何《肖申克的救赎》在IMDb和豆瓣都能排第一？</a>

    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/9259304/">为何《肖申克的救赎》在IMDb和豆瓣都能排第一？</a></h2>

                <div id="review_9259304_short" class="review-short" data-rid="9259304">
                    <div class="short-content">

                        时间会证明经典的价值，虽然在某些时刻会被误判和忽视。 用上面这句话来描述电影《肖申克的救赎》丝毫不会让人觉得会有任何夸张和吹捧的意味，因为这部电影在后来多年牢牢占据IMDB和豆瓣电影榜单第一名的位置足以说明一切。但就是这么一部经典的电影，却在其锋芒初露的时候被人...

                        &nbsp;(<a href="javascript:;" id="toggle-9259304-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_9259304_full" class="hidden">
                    <div id="review_9259304_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="9259304" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-9259304">
                                4666
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="9259304" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-9259304">
                                712
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/9259304/#comments" class="reply ">490回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>



    <div data-cid="1127585">
        <div class="main review-item" id="1127585">



    <header class="main-hd">
        <a href="https://www.douban.com/people/1317870/" class="avator">
            <img width="24" height="24" src="https://img3.doubanio.com/icon/u1317870-33.jpg">
        </a>

        <a href="https://www.douban.com/people/1317870/" class="name">aratana</a>

            <span class="allstar50 main-title-rating" title="力荐"></span>

        <span content="2007-02-26" class="main-meta">2007-02-26 10:38:45</span>


    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/1127585/">《肖申克的救赎》：1994—2007，希望就是现实</a></h2>

                <div id="review_1127585_short" class="review-short" data-rid="1127585">
                    <div class="short-content">

                        一、缘起  从来没想过给《肖申克的救赎》写一篇影评，也许是生怕暴露自己只是个不谙世事的初级影迷，也许是对这样一部无法复制的影片真的不愿去过多地提起。然而一场出其不意的重感冒让我只能卧床裹被，已没有了力气去消化我那些故作高深、一直收着却懒得去看的电影，不期然地...

                        &nbsp;(<a href="javascript:;" id="toggle-1127585-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_1127585_full" class="hidden">
                    <div id="review_1127585_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="1127585" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-1127585">
                                2092
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="1127585" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-1127585">
                                161
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/1127585/#comments" class="reply ">202回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>



    <div data-cid="1005528">
        <div class="main review-item" id="1005528">



    <header class="main-hd">
        <a href="https://www.douban.com/people/suoliweng/" class="avator">
            <img width="24" height="24" src="https://img3.doubanio.com/icon/u1026935-2.jpg">
        </a>

        <a href="https://www.douban.com/people/suoliweng/" class="name">蓑笠翁</a>

            <span class="allstar50 main-title-rating" title="力荐"></span>

        <span content="2005-09-25" class="main-meta">2005-09-25 16:27:41</span>


    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/1005528/">人生的过程就是一个摆脱institutionalization(体制化)的过程</a></h2>

                <div id="review_1005528_short" class="review-short" data-rid="1005528">
                    <div class="short-content">

                        现在好象比较时兴将人分为体制内和体制外的人,体制外的人通常有某种优越感,似乎自己的人格才是独立的.可实际上,真正愿意做体制外的人还是很少的,而且是很痛苦的.余杰北大硕士毕业后差一点进了他想进的国家图书馆作一个体制内的人,可由于他写了一些比较反体制的文章,最后还是被...

                        &nbsp;(<a href="javascript:;" id="toggle-1005528-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_1005528_full" class="hidden">
                    <div id="review_1005528_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="1005528" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-1005528">
                                1451
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="1005528" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-1005528">
                                78
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/1005528/#comments" class="reply ">162回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>



    <div data-cid="1062920">
        <div class="main review-item" id="1062920">



    <header class="main-hd">
        <a href="https://www.douban.com/people/erichuang/" class="avator">
            <img width="24" height="24" src="https://img2.doubanio.com/icon/u1187841-1.jpg">
        </a>

        <a href="https://www.douban.com/people/erichuang/" class="name">油爆虾</a>

            <span class="allstar50 main-title-rating" title="力荐"></span>

        <span content="2006-08-03" class="main-meta">2006-08-03 23:24:54</span>


    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/1062920/">《肖申克的救赎》的一些幕后花絮</a></h2>

                <div id="review_1062920_short" class="review-short" data-rid="1062920">
                    <div class="short-content">

                         * 是否记得片尾有一行字幕"In memory of Allen Greene"？翻译成中文就是"纪念Allen Greene "。Allen Greene是《肖申克的救赎》编导Frank Darabont的经纪人，在影片完成 的前夕死于AIDS的并发症。 　　 　　* 是否记得刚来到监狱的新囚犯们走下囚车时，嘲笑他们的人群中有一个...

                        &nbsp;(<a href="javascript:;" id="toggle-1062920-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_1062920_full" class="hidden">
                    <div id="review_1062920_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="1062920" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-1062920">
                                854
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="1062920" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-1062920">
                                41
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/1062920/#comments" class="reply ">66回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>



    <div data-cid="5449290">
        <div class="main review-item" id="5449290">



    <header class="main-hd">
        <a href="https://www.douban.com/people/58035060/" class="avator">
            <img width="24" height="24" src="https://img3.doubanio.com/icon/u58035060-33.jpg">
        </a>

        <a href="https://www.douban.com/people/58035060/" class="name">附离</a>

            <span class="allstar10 main-title-rating" title="很差"></span>

        <span content="2012-05-31" class="main-meta">2012-05-31 22:40:33</span>


    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/5449290/">没能力自由，谈什么自由 —— 其实你没那么渴望自由</a></h2>

                <div id="review_5449290_short" class="review-short" data-rid="5449290">
                    <div class="short-content">

                        打一颗星并不是因为这部片很差，只是不明白怎么会是豆瓣电影里的头牌。用极端的踩来平衡下极端的捧。  N年前看的片子，当时觉得真不错。具体不错在哪里？或许是因为结局不错，主人公最终成功越狱到达梦想之地，观影者借以给自己希望，以为自己也能达到自由的彼处。  第一次看完...

                        &nbsp;(<a href="javascript:;" id="toggle-5449290-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_5449290_full" class="hidden">
                    <div id="review_5449290_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="5449290" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-5449290">
                                2619
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="5449290" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-5449290">
                                1529
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/5449290/#comments" class="reply ">729回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>



    <div data-cid="8848890">
        <div class="main review-item" id="8848890">



    <header class="main-hd">
        <a href="https://www.douban.com/people/lzy1110/" class="avator">
            <img width="24" height="24" src="https://img3.doubanio.com/icon/u167539095-2.jpg">
        </a>

        <a href="https://www.douban.com/people/lzy1110/" class="name">刘泽宇</a>

            <span class="allstar50 main-title-rating" title="力荐"></span>

        <span content="2017-10-05" class="main-meta">2017-10-05 22:18:05</span>


    </header>


            <div class="main-bd">

                <h2><a href="https://movie.douban.com/review/8848890/">关于“救赎”</a></h2>

                <div id="review_8848890_short" class="review-short" data-rid="8848890">
                    <div class="short-content">
                            <p class="spoiler-tip">这篇影评可能有剧透</p>

                        个人感觉，《肖申克的救赎》（The Shawshank Redemption）中的Redemption的意思是“赎回;偿还;补救”，因此“救赎”非常完美地解释了这部电影的主题，围绕“救赎”主题的是： 1，安迪对自己的救赎：从一开始不让自己沦陷于监狱生活（对比于和他同时入狱的胖子第一晚就受不了）...

                        &nbsp;(<a href="javascript:;" id="toggle-8848890-copy" class="unfold" title="展开">展开</a>)
                    </div>
                </div>

                <div id="review_8848890_full" class="hidden">
                    <div id="review_8848890_full_content" class="full-content"></div>
                </div>

                <div class="action">
                    <a href="javascript:;" class="action-btn up" data-rid="8848890" title="有用">
                        <img src="https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png">
                        <span id="r-useful_count-8848890">
                                1193
                        </span>
                    </a>
                    <a href="javascript:;" class="action-btn down" data-rid="8848890" title="没用">
                        <img src="https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png">
                        <span id="r-useless_count-8848890">
                                85
                        </span>
                    </a>
                    <a href="https://movie.douban.com/review/8848890/#comments" class="reply ">22回应</a>

                    <a href="javascript:;;" class="fold hidden">收起</a>
                </div>
            </div>
        </div>
    </div>






    <!-- COLLECTED JS -->
    <!-- COLLECTED CSS -->
</div>

    <script type="text/javascript">
        (function() {
            if (window.__init_review_list) return;
            __init_review_list = true;
                window.is_released = true
                window.txt_released = '该电影还未上映，不能投票噢'
        })();
        window.useful_icon = "https://img1.doubanio.com/f/zerkalo/536fd337139250b5fb3cf9e79cb65c6193f8b20b/pics/up.png";
        window.usefuled_icon = "https://img1.doubanio.com/f/zerkalo/635290bb14771c97270037be21ad50514d57acc3/pics/up-full.png";
        window.useless_icon = "https://img1.doubanio.com/f/zerkalo/68849027911140623cf338c9845893c4566db851/pics/down.png";
        window.uselessed_icon = "https://img1.doubanio.com/f/zerkalo/23cee7343568ca814238f5ef18bf8aadbe959df2/pics/down-full.png";
    </script>

    <link rel="stylesheet" href="https://img1.doubanio.com/f/zerkalo/3aeb281ab0e4f2c7050458684acfeb6838441de9/css/review/editor/ng/setting_standalone.css">
    <script src="https://img1.doubanio.com/f/zerkalo/938cdbe2e223a3117cbbcb4929cae2001b402c20/js/review/editor/ng/manifest.js"></script>
    <script src="https://img1.doubanio.com/f/zerkalo/296cd5fec472a78add5fee958c58d72f47d91586/js/review/editor/ng/vendor.js"></script>
    <script src="https://img1.doubanio.com/f/zerkalo/c0095c35695e36603701c428b6679987211e3c9b/js/review/editor/ng/setting_standalone.js"></script>
    <script src="https://img1.doubanio.com/f/zerkalo/8941af7854ddad9561648b706cdb49f3d1534ff3/js/review/editor/ng/render_gif.js"></script>
    <script src="https://img1.doubanio.com/f/zerkalo/68b2d67ea75209236a6443ad45f370f1bca536ae/js/review/actions.js"></script>
    <script src="https://img1.doubanio.com/f/zerkalo/7196bdec780f03785f55b06fda34999595057f65/js/review/unfold.js"></script>
    <script src="https://img1.doubanio.com/f/vendors/f25ae221544f39046484a823776f3aa01769ee10/js/ui/dialog.js"></script>











                <p class="pl">
                    &gt;
                        <a href="reviews">
                            更多影评
                                13463篇
                        </a>
                </p>
    </section>
<!-- COLLECTED JS -->


    <br>


            <div class="section-discussion">

                    <div class="mod-hd">
                            <a class="comment_btn j a_show_login" href="https://www.douban.com/register?reason=review" rel="nofollow"><span>添加新讨论</span></a>

    <h2>
        讨论区
         &nbsp; ·&nbsp; ·&nbsp; ·&nbsp; ·&nbsp; ·&nbsp; ·
    </h2>

                    </div>

  <table class="olt"><tbody><tr><td></td><td></td><td></td><td></td></tr>

        <tr>
          <td class="pl"><a href="https://movie.douban.com/subject/1292052/discussion/637760819/" title="为什么在“审美是主观的”这一前提下我们仍然能评选出一个全平台第一的电影呢？">为什么在“审美是主观的”这一前提下我们仍然能评...</a></td>
          <td class="pl"><span>来自</span><a href="https://www.douban.com/people/285660731/">豆友didin</a></td>
          <td class="pl"><span>6 回应</span></td>
          <td class="pl"><span>2025-02-27 03:07:10</span></td>
        </tr>

        <tr>
          <td class="pl"><a href="https://movie.douban.com/subject/1292052/discussion/637767654/" title="又看一遍">又看一遍</a></td>
          <td class="pl"><span>来自</span><a href="https://www.douban.com/people/Zeno6993/">建築師鼓手</a></td>
          <td class="pl"><span>1 回应</span></td>
          <td class="pl"><span>2025-02-20 20:42:22</span></td>
        </tr>

        <tr>
          <td class="pl"><a href="https://movie.douban.com/subject/1292052/discussion/637772250/" title="优秀电影值得反复观赏">优秀电影值得反复观赏</a></td>
          <td class="pl"><span>来自</span><a href="https://www.douban.com/people/244351342/">一</a></td>
          <td class="pl"><span></span></td>
          <td class="pl"><span>2025-02-18 23:34:14</span></td>
        </tr>

        <tr>
          <td class="pl"><a href="https://movie.douban.com/subject/1292052/discussion/637768392/" title="《肖申克的救赎》">《肖申克的救赎》</a></td>
          <td class="pl"><span>来自</span><a href="https://www.douban.com/people/281625563/">讨厌吃苦瓜🪵</a></td>
          <td class="pl"><span></span></td>
          <td class="pl"><span>2025-02-09 20:14:50</span></td>
        </tr>

        <tr>
          <td class="pl"><a href="https://movie.douban.com/subject/1292052/discussion/637766494/" title="终于看完了">终于看完了</a></td>
          <td class="pl"><span>来自</span><a href="https://www.douban.com/people/189901830/">客观立场群众</a></td>
          <td class="pl"><span></span></td>
          <td class="pl"><span>2025-02-04 20:01:29</span></td>
        </tr>
  </tbody></table>

                    <p class="pl" align="right">
                        <a href="/subject/1292052/discussion/" rel="nofollow">
                            &gt; 去这部影片的讨论区（全部3595条）
                        </a>
                    </p>
            </div>











<div id="askmatrix">
    <div class="mod-hd">
        <h2>
                关于《肖申克的救赎》的问题
                · · · · · ·
            <span class="pl">
                (<a href="https://movie.douban.com/subject/1292052/questions/?from=subject">
                    全部88个
                </a>)
            </span>
        </h2>


        <!--

    <a class='j a_show_login comment_btn'
        href='https://movie.douban.com/subject/1292052/questions/ask/?from=subject'>我来提问</a>
 -->
    </div>

    <div class="mod-bd">
        <ul class="">
            <li class="">
                <span class="tit">
                    <a href="https://movie.douban.com/subject/1292052/questions/3982/?from=subject" class="">
                            Andy为什么不凿好隧道就逃走？
                    </a>
                </span>
                <span class="meta">
                    14人回答
                </span>
            </li>
            <li class="">
                <span class="tit">
                    <a href="https://movie.douban.com/subject/1292052/questions/3914/?from=subject" class="">
                            为什么安迪要偷走典狱长的鞋子？为什么逃狱之前里面穿了件衬衫，后面逃出来的时候却是里面T恤...
                    </a>
                </span>
                <span class="meta">
                    21人回答
                </span>
            </li>
        </ul>

        <p>&gt;
            <a href="https://movie.douban.com/subject/1292052/questions/?from=subject">
                全部88个问题
            </a>
        </p>

    </div>
</div>








            </div>
'''

# 使用 re.DOTALL 标志进行正则匹配
pattern = r'<span class="all hidden" style="display: inline;">(.*?)</span>'
match = re.search(pattern, html_content, re.DOTALL)

if match:
    # 提取匹配的内容
    content_with_tags = match.group(1).strip()
    # # 去除 HTML 标签
    # content_without_tags = re.sub(r'<[^>]*>', '', content_with_tags)
    # # 去除空行
    # content_without_empty_lines = '\n'.join([line for line in content_without_tags.split('\n') if line.strip()])
    # 打开一个文件以写入模式
    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write(content_with_tags)
    print("内容已成功写入 output.txt")
else:
    print("未找到匹配内容")