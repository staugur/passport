/*
    OAuthGuide第三方引导页面
*/
layui.define(['base', 'form', 'layer', 'element'], function(exports) {
    var base = layui.base,
        form = layui.form,
        layer = layui.layer,
        element = layui.element,
        $ = layui.jquery;
    //显示当前tab
    if (location.hash) {
        element.tabChange('guide', location.hash.replace(/^#/, ''));
    }
    //监听tab切换
    element.on('tab(guide)', function() {
        var othis = $(this),
            layid = othis.attr('lay-id');
        if (layid) {
            location.hash = layid;
        }
    });
    //表单自定义校验
    form.verify({
        passwd: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (value.length < 6 || value.length > 30) {
                return '密码长度应在6到30个字符之间！';
            }
        }
    });
    //绑定登录事件
    form.on("submit(bindLogin)", function(data) {
        var url = base.getUrlQuery("sso") ? "/OAuthGuide?Action=bindLogin&sso=" + base.getUrlQuery("sso") : "/OAuthGuide?Action=bindLogin";
        console.log(url);
        base.ajax(url, function(res) {
            layer.msg("绑定成功，跳转中", {
                icon: 1,
                time: 2000
            }, function() {
                location.href = res.nextUrl;
            });
        }, {
            data: data.field,
            method: "post",
            msgprefix: false,
            beforeSend: function() {
                $("#submitbutton").attr({
                    disabled: "disabled"
                });
                $('#submitbutton').addClass("layui-disabled");
            },
            complete: function() {
                $('#submitbutton').removeAttr("disabled");
                $('#submitbutton').removeClass("layui-disabled");
            },
            fail: function(res) {
                layer.msg(res.msg, {
                    icon: 7,
                    time: 3000
                });
            }
        });
    });
    //直接登录事件
    form.on("submit(directLogin)", function(data) {
        var url = base.getUrlQuery("sso") ? "/OAuthGuide?Action=directLogin&sso=" + base.getUrlQuery("sso") : "/OAuthGuide?Action=directLogin";
        console.log(url);
        base.ajax(url, function(res) {
            layer.msg("登录成功，跳转中", {
                icon: 1,
                time: 2000
            }, function() {
                location.href = res.nextUrl;
            });
        }, {
            data: data.field,
            method: "post",
            msgprefix: false,
            beforeSend: function() {
                $("#submitbutton2").attr({
                    disabled: "disabled"
                });
                $('#submitbutton2').addClass("layui-disabled");
            },
            complete: function() {
                $('#submitbutton2').removeAttr("disabled");
                $('#submitbutton2').removeClass("layui-disabled");
            },
            fail: function(res) {
                layer.msg(res.msg, {
                    icon: 7,
                    time: 3000
                });
            }
        });
    });
    //输出接口
    exports('oauthguide', null);
});