<!DOCTYPE html>
<html class="devise-layout-html" lang="en">
<head prefix="og: http://ogp.me/ns#">
<meta charset="utf-8">
<meta content="IE=edge" http-equiv="X-UA-Compatible">
<meta content="object" property="og:type">
<meta content="GitLab" property="og:site_name">
<meta content="Sign in" property="og:title">
<meta content="BioHPC Git" property="og:description">
<meta content="https://git.biohpc.swmed.edu/assets/gitlab_logo-7ae504fe4f68fdebb3c2034e36621930cd36ea87924c11ff65dbcb8ed50dca58.png" property="og:image">
<meta content="https://git.biohpc.swmed.edu/users/sign_in" property="og:url">
<meta content="summary" property="twitter:card">
<meta content="Sign in" property="twitter:title">
<meta content="BioHPC Git" property="twitter:description">
<meta content="https://git.biohpc.swmed.edu/assets/gitlab_logo-7ae504fe4f68fdebb3c2034e36621930cd36ea87924c11ff65dbcb8ed50dca58.png" property="twitter:image">

<title>Sign in · GitLab</title>
<meta content="BioHPC Git" name="description">
<link rel="shortcut icon" type="image/x-icon" href="/assets/favicon-883fbd2a06c43a07e6995592e33b89a3a11570cc15e98dd861ad077cf580016d.ico" />
<link rel="stylesheet" media="all" href="/assets/application-066f0c78d428285c9b03f03b20ad5714c40123046b4e770b98973b79e7184e99.css" />
<link rel="stylesheet" media="print" href="/assets/print-9c3a1eb4a2f45c9f3d7dd4de03f14c2e6b921e757168b595d7f161bbc320fc05.css" />
<script src="/assets/application-27b34e705b8993925b2e4e847090c682182a1477b3f5e54a4cf2ae4bd43887ad.js"></script>
<meta name="csrf-param" content="authenticity_token" />
<meta name="csrf-token" content="BsxG5YxWwk4qb2weRCsVpSwpdjIjaXP53jym2WvNQyRgsdOkRNuSohuSRo17PSEaAplJUqkB7ktLl5Y/klu1iQ==" />
<meta content="origin-when-cross-origin" name="referrer">
<meta content="width=device-width, initial-scale=1, maximum-scale=1" name="viewport">
<meta content="#474D57" name="theme-color">
<link rel="apple-touch-icon" type="image/x-icon" href="/assets/touch-icon-iphone-5a9cee0e8a51212e70b90c87c12f382c428870c0ff67d1eb034d884b78d2dae7.png" />
<link rel="apple-touch-icon" type="image/x-icon" href="/assets/touch-icon-ipad-a6eec6aeb9da138e507593b464fdac213047e49d3093fc30e90d9a995df83ba3.png" sizes="76x76" />
<link rel="apple-touch-icon" type="image/x-icon" href="/assets/touch-icon-iphone-retina-72e2aadf86513a56e050e7f0f2355deaa19cc17ed97bbe5147847f2748e5a3e3.png" sizes="120x120" />
<link rel="apple-touch-icon" type="image/x-icon" href="/assets/touch-icon-ipad-retina-8ebe416f5313483d9c1bc772b5bbe03ecad52a54eba443e5215a22caed2a16a2.png" sizes="152x152" />
<link color="rgb(226, 67, 41)" href="/assets/logo-d36b5212042cebc89b96df4bf6ac24e43db316143e89926c0db839ff694d2de4.svg" rel="mask-icon">
<meta content="/assets/msapplication-tile-1196ec67452f618d39cdd85e2e3a542f76574c071051ae7effbfde01710eb17d.png" name="msapplication-TileImage">
<meta content="#30353E" name="msapplication-TileColor">




</head>

<body class="ui_charcoal login-page application navless" data-page="sessions:new">
<div class="page-wrap">
<script>
//<![CDATA[
window.gon={};gon.api_version="v3";gon.default_avatar_url="https:\/\/git.biohpc.swmed.edu\/assets\/no_avatar-849f9c04a3a0d0cea2424ae97b27447dc64a7dbfae83c036c45b403392f0e8ba.png";gon.max_file_size=10;gon.relative_url_root="";gon.shortcuts_path="\/help\/shortcuts";gon.user_color_scheme="white";gon.award_menu_url="\/emojis";gon.katex_css_url="\/assets\/katex-e46cafe9c3fa73920a7c2c063ee8bb0613e0cf85fd96a3aea25f8419c4bfcfba.css";gon.katex_js_url="\/assets\/katex-04bcf56379fcda0ee7c7a63f71d0fc15ffd2e014d017cd9d51fd6554dfccf40a.js";
//]]>
</script>
<header class="navbar navbar-fixed-top navbar-empty">
<div class="container">
<div class="center-logo">
<img src="/uploads/appearance/header_logo/1/logo-white.png" alt="Logo white" />
</div>
</div>
</header>



<div class="container navless-container">
<div class="content">
<div class="flash-container flash-container-page">
<div class="flash-alert">
<div class="container-fluid container-limited">
<span>You need to sign in or sign up before continuing.</span>
</div>
</div>
</div>

<div class="row">
<div class="col-sm-5 pull-right new-session-forms-container">
<div>
<ul class="custom-provider-tabs nav-links nav-tabs new-session-tabs">
<li class="active">
<a data-toggle="tab" href="#ldapmain">BioHPC Sign in</a>
</li>
<li>
<a data-toggle="tab" href="#ldap-standard">Standard</a>
</li>
</ul>

<div class="tab-content">
<div class="active login-box tab-pane" id="ldapmain" role="tabpanel">
<div class="login-body">
<form id="new_ldap_user" class="gl-show-field-errors" action="/users/auth/ldapmain/callback" accept-charset="UTF-8" method="post"><input name="utf8" type="hidden" value="&#x2713;" /><input type="hidden" name="authenticity_token" value="SskEWi+Z0/RK5Xku/VQQzbCV+5/MZ/mVv8EayIs0W2kstJEb5xSDGHsYU73CQiRyniXE/0YPZCcqaioucqKtxA==" /><div class="form-group">
<label for="username">BioHPC Username</label>
<input type="text" name="username" id="username" class="form-control top" title="This field is required." autofocus="autofocus" required="required" />
</div>
<div class="form-group">
<label for="password">Password</label>
<input type="password" name="password" id="password" class="form-control bottom" title="This field is required." required="required" />
</div>
<div class="remember-me checkbox">
<label for="remember_me">
<input type="checkbox" name="remember_me" id="remember_me" value="1" />
<span>Remember me</span>
</label>
</div>
<input type="submit" name="commit" value="Sign in" class="btn-save btn" />
</form>
</div>
</div>
<div class="login-box tab-pane" id="ldap-standard" role="tabpanel">
<div class="login-body">
<form class="new_user gl-show-field-errors" aria-live="assertive" id="new_user" action="/users/sign_in" accept-charset="UTF-8" method="post"><input name="utf8" type="hidden" value="&#x2713;" /><input type="hidden" name="authenticity_token" value="zgeCNios84ZbzlMlW+IndVH/fqbtyLvuLiowSqVNZ0Coehd34qGjamozebZk9BPKf09BxmegJly7gQCsXNuR7Q==" /><div class="form-group">
<label for="login">Username or email</label>
<input class="form-control top" autofocus="autofocus" autocapitalize="off" autocorrect="off" required="required" title="This field is required." type="text" name="user[login]" id="user_login" />
</div>
<div class="form-group">
<label for="user_password">Password</label>
<input class="form-control bottom" required="required" title="This field is required." type="password" name="user[password]" id="user_password" />
</div>
<div class="remember-me checkbox">
<label for="user_remember_me">
<input name="user[remember_me]" type="hidden" value="0" /><input type="checkbox" value="1" name="user[remember_me]" id="user_remember_me" />
<span>Remember me</span>
</label>
<div class="pull-right forgot-password">
<a href="/users/password/new">Forgot your password?</a>
</div>
</div>
<div class="submit-container move-submit-down">
<input type="submit" name="commit" value="Sign in" class="btn btn-save" />
</div>
</form>
</div>
</div>

</div>
</div>

</div>
<div class="col-sm-7 brand-holder pull-left">
<h1>
<img src="/uploads/appearance/logo/1/biohpc_logo_200pxh.png" alt="Biohpc logo 200pxh" />
</h1>
<h3>BioHPC Git</h3>
<p dir="auto">**  Files stored must not contain PHI or other privacy sensitive information without prior approval **</p>
</div>
</div>
</div>
</div>
<hr class="footer-fixed">
<div class="container footer-container">
<div class="footer-links">
<a href="/explore">Explore</a>
<a href="/help">Help</a>
<a href="https://about.gitlab.com/">About GitLab</a>
<a href="https://portal.biohpc.swmed.edu/">About BioHPC</a>
</div>
</div>
</div>
</body>
</html>
