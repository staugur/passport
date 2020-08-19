/*
    基本的公共功能
*/

layui.define(["element", "util", "layer"], function(exports) {
    'use strict';
    var $ = layui.jquery,
        util = layui.util,
        layer = layui.layer,
        device = layui.device(),
        element = layui.element;
    //禁止嵌套
    if (window != top) {
        top.location.href = location.href;
    }
    //阻止IE7以下访问
    if (device.ie && device.ie < 8) {
        layer.alert('如果您非得使用 IE 浏览器访问，那么请使用 IE8+');
    }
    //右下角工具
    util.fixbar({
        bgcolor: '#009688'
    });
    //公共接口
    var base = {
        ajax: function(url, success, options) {
            /*
                Ajax提交
                @param url string: 请求路径
                @param success function: success为成功后回调函数
                @param options object:
                    async是否异步; 
                    post,put,delete等方法所需data;
                    error为发生异常时或success返回中code不为0时回调函数;
                    beforeSend为请求前回调函数;
                    complete为完成请求后回调;
                    msgprefix表示success返回code不为0时提示消息的前缀。
            */
            var that = this,
                urltype = typeof url === 'string',
                successtype = typeof success === "function",
                optionstype = typeof options === "object";
            if (!url || !urltype) {
                return false;
            }
            if (success) {
                if (!successtype) {
                    return false;
                }
            }
            if (options) {
                if (!optionstype) {
                    return false;
                }
            } else {
                options = {};
            }
            return $.ajax({
                url: url,
                async: options.async || true,
                method: options.method || 'post',
                dataType: options.dataType || 'json',
                data: options.data || {},
                beforeSend: options.beforeSend ? options.beforeSend : function() {},
                success: function(res) {
                    if (res.code === 0 || res.success === true) {
                        success && success(res);
                    } else {
                        if (options.msgprefix != false) {
                            popup(options.msgprefix || '' + res.msg || res.code);
                        }
                        options.fail && options.fail(res);
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    popup("系统异常，请稍后再试，状态码：" + XMLHttpRequest.status + "，" + textStatus);
                },
                complete: options.complete ? options.complete : function() {}
            });
        },
        getUrlPath: function(ishref) {
            /*
                获取url路径(不包含锚部分)；如果ishref为true，则返回全路径(包含锚部分)
                比如url为http://passport.saintic.com/user/setting/，默认返回/user/setting/ ，ishref为true返回上述url
            */
            return ishref === true ? location.href : location.pathname;
        },
        getUrlQuery: function(key, acq) {
            /*
                获取URL中?之后的查询参数，不包含锚部分，比如url为http://passport.saintic.com/user/message/?status=1&Action=getCount
                若无查询的key，则返回整个查询参数对象，即返回{status: "1", Action: "getCount"}；
                若有查询的key，则返回对象值，返回值可以指定默认值acq：如key=status, 返回1；key=test返回acq
            */
            var str = location.search;
            var obj = {};
            if (str) {
                str = str.substring(1, str.length);
                // 以&分隔字符串，获得类似name=xiaoli这样的元素数组
                var arr = str.split("&");
                //var obj = new Object();
                // 将每一个数组元素以=分隔并赋给obj对象
                for (var i = 0; i < arr.length; i++) {
                    var tmp_arr = arr[i].split("=");
                    obj[decodeURIComponent(tmp_arr[0])] = decodeURIComponent(tmp_arr[1]);
                }
            }
            return key ? obj[key] || acq : obj;
        },
        isContains: function(str, substr) {
            /* 判断str中是否包含substr */
            return str.indexOf(substr) >= 0;
        },
        safeCheck: function(s) {
            /* 简单字符串安全检查 */
            try {
                if (s.indexOf("'") != -1 || s.indexOf('"') != -1 || s.indexOf("?") != -1 || s.indexOf("%") != -1 || s.indexOf(";") != -1 || s.indexOf("*") != -1 || s.indexOf("=") != -1 || s.indexOf("\\") != -1) {
                    return false
                } else {
                    return true;
                }
            } catch (e) {
                return false;
            }
        }
    };
    //用户反馈
    $('#feedback').on('click', function() {
        var width = $(window).width(),
            height = 460;
        if (width > 400) {
            width = 400;
        } else {
            width = width / 4 * 3;
            height = 480;
        }
        layer.open({
            type: 2,
            title: '意见反馈',
            shadeClose: false,
            shade: 0.3,
            area: [width + 'px', height + 'px'],
            content: '/feedback.html'
        });
    });
    //注册账号、绑定本地账号时发送验证码
    $('#sms-tip-msg').on('click', function() {
        disable_sendCode();
        var wait = 300;
        var account = $('input[name="account"]').val();
        if (account) {
            base.ajax("/api/miscellaneous/_sendVcode", function(res) {
                check();
            }, {
                method: 'post',
                data: {
                    account: account,
                    scene: $('#scene').val() || "signUp"
                },
                msgprefix: false,
                fail: function(res) {
                    layer.msg(res.msg);
                    enable_sendCode();
                }
            });
        } else {
            layer.tips('请填写邮箱或手机号', '#account', {
                tips: 3
            });
            enable_sendCode();
        }

        function disable_sendCode() {
            $('#sms-tip-msg').attr("disabled", "disabled");
            $('#sms-tip-msg').addClass("layui-disabled");
        }

        function enable_sendCode() {
            $('#sms-tip-msg').removeAttr("disabled");
            $('#sms-tip-msg').removeClass("layui-disabled");
        }

        function check() {
            if (wait == 0) {
                enable_sendCode();
                $('#sms-tip-msg').text("重发验证码");
                wait = 300;
            } else {
                $('#sms-tip-msg').text(wait + "秒后重发");
                wait--;
                setTimeout(function() {
                    check();
                }, 1000)
            }
        }

        return false;
    });
    //输出接口
    exports('base', base);
});