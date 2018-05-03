/*
    signin登录页面
*/
layui.define(['base', 'form', 'layer'], function(exports) {
    var base = layui.base,
        form = layui.form,
        layer = layui.layer,
        $ = layui.jquery;
    //表单自定义校验
    form.verify({
        passwd: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (value.length < 6 || value.length > 30) {
                return '密码长度应在6到30个字符之间！';
            }
        }
    });
    //登录按钮事件
    form.on("submit(signIn)", function(data) {
        var url = base.getUrlQuery("sso") ? "/signIn?sso=" + base.getUrlQuery("sso") : "/signIn";
        base.ajax(url, function(res) {
            location.href = res.nextUrl;
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
    //输出接口
    exports("signin", null);
});