/*
    Passport主入口
*/

layui.define(["element", "util", "layer", "form"], function(exports) {
    'use strict';
    var $ = layui.jquery,
        element = layui.element,
        util = layui.util,
        layer = layui.layer,
        form = layui.form,
        device = layui.device();
    //阻止IE7以下访问
    if (device.ie && device.ie < 8) {
        layer.alert('如果您非得使用 IE 浏览器访问，那么请使用 IE8+');
    }
    //手机设备的简单适配
    var treeMobile = $('.site-tree-mobile'),
        shadeMobile = $('.site-mobile-shade');
    treeMobile.on('click', function() {
        $('body').addClass('site-mobile');
    });
    shadeMobile.on('click', function() {
        $('body').removeClass('site-mobile');
    });
    //右下角工具
    util.fixbar({
        bgcolor: '#009688'
    });
    //对外接口
    var passport = {
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
                    //console.log(res);
                    if (res.code === 0) {
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
            str = str.substring(1, str.length);
            // 以&分隔字符串，获得类似name=xiaoli这样的元素数组
            var arr = str.split("&");
            var obj = new Object();
            // 将每一个数组元素以=分隔并赋给obj对象
            for (var i = 0; i < arr.length; i++) {
                var tmp_arr = arr[i].split("=");
                obj[decodeURIComponent(tmp_arr[0])] = decodeURIComponent(tmp_arr[1]);
            }
            return key ? obj[key] || acq : obj;
        },
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
        },
        isContains: function(str, substr) {
            /* 判断str中是否包含substr */
            return str.indexOf(substr) >= 0;
        }
    };
    //获取用户信息
    passport.ajax("/api/user/profile/?getBind=true", function(res) {
        if (res.code == 0) {
            var userdata = res.data;
            //更新顶部导航昵称
            $('#nav_nickname').text(userdata.nick_name || '');
            //更新顶部导航头像
            $('#nav_avatar').attr('src', userdata.avatar || '/static/images/avatar/default.png');
            //前端缓存
            layui.cache.user = userdata;
            //设置页填充资料
            if (passport.getUrlPath() == "/user/setting/") {
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
                for (var index = 0; index < userdata.bind.length; index++) {
                    var identity_type = userdata.bind[index].identity_type;
                    $("#oauth-" + identity_type).addClass("app-havebind");
                    $("#oauth-" + identity_type + "-tip").html('已成功绑定，您可以使用' + passport.socialAccountVisiblenameMapping(identity_type) + '帐号直接登录，当然，您也可以<a href="/unbind?identity_name=' + identity_type + '" class="acc-unbind" type="' + identity_type + '">解除绑定</a>');
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