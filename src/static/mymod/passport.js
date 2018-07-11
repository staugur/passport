/*
    Passport主入口-登录后
*/

layui.define(["base", "element", "util", "layer", "form"], function(exports) {
    'use strict';
    var base = layui.base,
        element = layui.element,
        util = layui.util,
        layer = layui.layer,
        form = layui.form,
        device = layui.device(),
        $ = layui.jquery;
    //手机设备的简单适配
    var treeMobile = $('.site-tree-mobile'),
        shadeMobile = $('.site-mobile-shade');
    treeMobile.on('click', function() {
        $('body').addClass('site-mobile');
    });
    shadeMobile.on('click', function() {
        $('body').removeClass('site-mobile');
    });
    //对外接口
    var passport = $.extend({}, base, {
        socialAccountVisiblenameMapping: function(account) {
            /* 社会化账号可见名映射 */
            var mapping = {
                mobile: "手机",
                email: "邮箱",
                github: "GitHub",
                qq: "QQ",
                wechat: "微信",
                baidu: "百度",
                weibo: "微博",
                coding: "Coding",
                gitee: "码云"
            };
            return mapping[account];
        },
        loginTypeNameMapping: function(type) {
            /* 登录账号数字类型到标识名称映射 */
            var mapping = {
                1: "mobile",
                2: "email",
                3: "github",
                4: "qq",
                5: "wechat",
                6: "baidu",
                7: "weibo",
                8: "coding",
                9: "gitee"
            };
            return mapping[type];
        }
    });
    //获取用户信息
    var getBind = passport.getUrlPath() === "/user/setting/" ? true : false;
    passport.ajax("/api/user/profile/?getBind=" + getBind, function(res) {
        if (res.code == 0) {
            var userdata = res.data;
            //更新顶部导航昵称
            $('#nav_nickname').text(userdata.nick_name || '');
            if (userdata.is_realname === 1) {
                $('#nav_nickname').addClass("nickname-realname");
                $('#nav_nickname').after('<i class="saintic-icon saintic-icon-realname-logo layui-hide-xs nickname-realname" title="已实名认证"></i>');
            }
            //更新顶部导航头像
            $('#nav_avatar').attr('src', userdata.avatar || '/static/images/avatar/default.png');
            //前端缓存
            layui.cache.user = userdata;
            //设置页填充资料
            if (passport.getUrlPath() === "/user/setting/") {
                $('#nick_name').val(userdata.nick_name);
                $('#domain_name').val(userdata.domain_name);
                if (userdata.domain_name) {
                    $('#domain_name_suffix').html(userdata.domain_name);
                }
                if (userdata.lock.nick_name === false) {
                    $('#nick_name').removeAttr("disabled");
                    $('#nick_name').removeClass("layui-disabled");
                }
                if (userdata.lock.domain_name === false) {
                    $('#domain_name').removeAttr("disabled");
                    $('#domain_name').removeClass("layui-disabled");
                }
                if (userdata.birthday) {
                    $('#birthday').val(util.toDateString(userdata.birthday * 1000, "yyyy-MM-dd"));
                }
                if (userdata.location) {
                    $('#location').val(userdata.location);
                }
                if (userdata.gender === 1) {
                    $("#gender1").attr("checked", "checked");
                } else if (userdata.gender === 0) {
                    $("#gender0").attr("checked", "checked");
                } else if (userdata.gender === 2) {
                    $("#gender2").attr("checked", "checked");
                }
                $('#signature').val(userdata.signature);
                //更新头像
                $('#avatar').attr('src', userdata.avatar);
                //重新渲染表单
                form.render();
                //账号绑定
                for (var index = 0; index < userdata.bind.length; index++) {
                    var auth_type = userdata.bind[index].auth_type;
                    var identity_type = userdata.bind[index].identity_type;
                    var unbind_msg = auth_type === "oauth" ? '<a href="/unbind?identity_name=' + identity_type + '" class="acc-unbind" type="' + identity_type + '">解除绑定</a>' : '<a href="/user/setting/?Action=bindLauth" class="acc-unbind lauth-bind" type="' + identity_type + '">修改绑定</a>';
                    $("#auth-" + identity_type).addClass("app-havebind");
                    $("#auth-" + identity_type + "-tip").html('已成功绑定，您可以使用' + passport.socialAccountVisiblenameMapping(identity_type) + '帐号直接登录，当然，您也可以' + unbind_msg);
                    //绑定本地化账号页面
                    if (identity_type === "email") {
                        $("#LAY_BindInfoEmail").html('<label for="activate">您的邮箱：</label><span class="layui-form-text">' + userdata.bind[index].identifier + '<em style="color:#009688;">（已成功绑定）</em></span>');
                    }
                    if (identity_type === "mobile") {
                        $("#RealnameShow").html('<blockquote class="layui-elem-quote"><i class="saintic-icon saintic-icon-realname-logo layui-hide-xs nickname-realname" title="已实名认证"></i>&nbsp;<span style="color: #5FB878">您已完成手机号绑定，成为实名认证用户，修改请移步账号绑定！</span></blockquote>');
                        $("#LAY_BindInfoPhone").html('<label for="activate">您的手机：</label><span class="layui-form-text">' + userdata.bind[index].identifier + '<em style="color:#009688;">（已成功绑定）</em></span>');
                    }
                }
            }
        }
    }, {
        "async": true,
        "method": "get",
        "msgprefix": '拉取用户信息失败：'
    });
    if (passport.getUrlPath() != "/user/message/") {
        //获取用户消息统计
        passport.ajax("/api/user/message/?Action=getCount&msgStatus=1", function(res) {
            if (res.code == 0) {
                if (res.count == 0) {
                    return;
                }
                //更新消息
                var elemUser = $('.fly-nav-user');
                var msg = $('<a class="fly-nav-msg" href="javascript:;" title="你有 ' + res.count + ' 条未读消息">' + res.count + '</a>');
                elemUser.append(msg);
                msg.on('click', function() {
                    location.href = "/user/message/";
                });
                layer.tips('你有 ' + res.count + ' 条未读消息', msg, {
                    tips: 3,
                    tipsMore: true,
                    fixed: true
                });
            }
        }, {
            "method": "get",
            "msgprefix": '拉取用户消息失败：'
        });
    }
    //输出接口
    exports('passport', passport);
});