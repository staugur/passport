/*
    signup注册页面
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
        },
        repasswd: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (value.length < 6 || value.length > 30) {
                return '密码长度应在6到30个字符之间！';
            }
            var passwd = $('input[name="password"]').val();
            if (passwd != value) {
                return '密码和重复密码不同，请重新输入！';
            }
        },
        terms: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (!document.getElementById("terms").checked) {
                return "请阅读并同意服务条款后继续！";
            }
        }
    });
    //登录按钮事件
    form.on("submit(signUp)", function(data) {
        base.ajax("/signUp", function(res) {
            layer.msg("注册成功", {
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
        return false;
    });
    //输出接口
    exports("signup", null);
});