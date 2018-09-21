# crawler_practice
this practice is just a home work for NCTU, TW.

# 知道的bug #

乃木坂[email protected],https://www.ptt.cc/bbs/Beauty/M.1504367479.A.63D.html
in https://www.ptt.cc/bbs/Beauty/index2232.html today..

* 網頁版列表會保謢email，所以output出來的值會是保謢的值

程式片段
```html
<div class="r-ent">
	<div class="nrec"><span class="hl f3">18</span></div>
	<div class="title">

		<a href="/bbs/Beauty/M.1504367479.A.63D.html">[正妹] 乃木坂<span class="__cf_email__" data-cfemail="c2f6f482968581">[email&#160;protected]</span></a>

	</div>
	<div class="meta">
		<div class="author">aq200aq</div>
		<div class="article-menu">

			<div class="trigger">&#x22ef;</div>
			<div class="dropdown">
				<div class="item"><a href="/bbs/Beauty/search?q=thread%3A%5B%E6%AD%A3%E5%A6%B9%5D&#43;%E4%B9%83%E6%9C%A8%E5%9D%8246%40TGC">搜尋同標題文章</a></div>

				<div class="item"><a href="/bbs/Beauty/search?q=author%3Aaq200aq">搜尋看板內 aq200aq 的文章</a></div>

			</div>

		</div>
		<div class="date"> 9/02</div>
		<div class="mark"></div>
	</div>
</div>
```
