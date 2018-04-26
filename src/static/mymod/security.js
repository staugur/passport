/*
    安全设置页面
*/

layui.define(["passport", "table", "element", "form", "layer", "util", "laytpl"], function(exports) {
    'use strict';
    var passport = layui.passport,
        table = layui.table,
        element = layui.element,
        form = layui.form,
        layer = layui.layer,
        $ = layui.jquery,
        util = layui.util,
        laytpl = layui.laytpl;
    //显示当前tab
    if (location.hash) {
        element.tabChange('securityTab', location.hash.replace(/^#/, ''));
    }
    //监听tab切换
    element.on('tab(securityTab)', function() {
        var othis = $(this),
            layid = othis.attr('lay-id');
        if (layid) {
            location.hash = layid;
        }
    });
    //会话模板
    var Sessiontpl = '\
        <fieldset class="layui-elem-field layui-field-title"><legend>当前会话</legend></fieldset>\
            <blockquote class="layui-elem-quote layui-quote-nm">\
                <b>{{ d.data.CurrentSession.area||"未知地区" }} {{ d.data.CurrentSession.ip }}</b><br/>\
                <b>{{ d.data.CurrentSession.browser.family }}</b> on {{ d.data.CurrentSession.browser.os }}<br/>\
                您于{{ layui.util.toDateString(d.data.CurrentSession.iat*1000) }}登录{{# if(d.data.CurrentSession.session){ }}，已登录{{ d.data.CurrentSession.session.clients.length }}个客户端{{# } }}\
            </blockquote>\
        {{# if (d.data.OtherSession.length>0) { }}\
            <fieldset class="layui-elem-field layui-field-title"><legend>其他会话</legend></fieldset>\
            {{#  layui.each(d.data.OtherSession, function(index, item){ }}\
                <blockquote class="layui-elem-quote layui-quote-nm">\
                    登录源于<b>{{ item.source }}</b><br/>\
                    共登录{{ item.clients.length }}个客户端\
                </blockquote>\
            {{#  }); }}\
        {{# } }}',
        ITChangeMapping = function(item, type) {
            //将操作系统、浏览器、设备转换为字体图标
            var im, browserMap = {
                    edge: '<i class="saintic-icon saintic-icon-edge-browser"></i>',
                    safari: '<i class="saintic-icon saintic-icon-safari-browser"></i>',
                    chrome: '<i class="saintic-icon saintic-icon-chrome-browser"></i>',
                    firefox: '<i class="saintic-icon saintic-icon-firefox"></i>',
                    ie: '<i class="saintic-icon saintic-icon-ie-browser"></i>',
                    opera: '<i class="saintic-icon saintic-icon-opera-browser"></i>',
                    qq: '<i class="saintic-icon saintic-icon-qq-browser"></i>',
                    sogou: '<i class="saintic-icon saintic-icon-sogou-browser"></i>',
                    uc: '<i class="saintic-icon saintic-icon-uc-browser"></i>',
                    baidu: '<i class="saintic-icon saintic-icon-baidu-browser"></i>'
                },
                systemMap = {
                    windows: '<i class="saintic-icon saintic-icon-windows"></i>',
                    linux: '<i class="saintic-icon saintic-icon-linux"></i>',
                    apple: '<i class="saintic-icon saintic-icon-apple"></i>',
                    android: '<i class="saintic-icon saintic-icon-andriod"></i>'
                },
                deviceMap = {
                    pc: '<i class="saintic-icon saintic-icon-pc"></i>',
                    mobile: '<i class="saintic-icon saintic-icon-mobilephone"></i>',
                    tablet: '<i class="saintic-icon saintic-icon-tablet"></i>'
                };
            if (type == "browser") {
                im = browserMap[item];
            } else if (type == "system") {
                im = systemMap[item];
            } else if (type == "device") {
                im = deviceMap[item]
            }
            return im || '<i class="saintic-icon saintic-icon-unknown"></i>'
        };
    passport.ajax("/api/user/security/?Action=getSessions&getCurrentSession=true&getOtherSession=true", function(res) {
        if (res.code === 0) {
            var html = laytpl(Sessiontpl).render(res);
            $('#SessionShow').html(html);
        }
    }, {
        method: "get"
    });
    //初始化渲染表格
    table.render({
        elem: "#loginHistory",
        height: 471,
        url: "/api/user/security/", //数据接口
        where: {
            Action: "getLoginHistory"
        },
        page: true, //开启分页
        cellMinWidth: 30,
        loading: true,
        cols: [
            [ //表头
                {
                    field: 'id',
                    title: 'ID',
                    sort: true,
                    width: 60
                }, {
                    field: 'login_ip',
                    title: 'IP',
                    width: 128
                }, {
                    field: 'login_area',
                    title: '地区与ISP',
                    minWidth: 80
                }, {
                    field: 'login_time',
                    title: '时间',
                    width: 170,
                    templet: function(d) {
                        return util.toDateString(d.login_time * 1000);
                    }
                }, {
                    field: 'login_type',
                    title: '方式',
                    width: 80,
                    templet: function(d) {
                        return passport.socialAccountVisiblenameMapping(passport.loginTypeNameMapping(d.login_type));
                    }
                }, {
                    field: 'browser_device',
                    title: '设备',
                    width: 60,
                    templet: function(d) {
                        var icon = ITChangeMapping(d.browser_type.toLowerCase(), "device")
                        return "<center title='" + d.browser_device + "'>" + icon + "</center>";
                    }
                }, {
                    field: 'browser_family',
                    title: '浏览器',
                    width: 75,
                    templet: function(d) {
                        var item, browser = d.browser_family.toLowerCase();
                        if (passport.isContains(browser, "chrome") === true) {
                            item = "chrome";
                        } else if (passport.isContains(browser, "firefox") === true) {
                            item = "firefox";
                        } else if (passport.isContains(browser, "safari") === true) {
                            item = "safari";
                        } else if (passport.isContains(browser, "edge") === true) {
                            item = "edge";
                        } else if (passport.isContains(browser, "ie") === true) {
                            item = "ie";
                        } else if (passport.isContains(browser, "opera") === true) {
                            item = "opera";
                        } else if (passport.isContains(browser, "qq") === true) {
                            item = "qq"
                        } else if (passport.isContains(browser, "sogou") === true) {
                            item = "sogou"
                        } else if (passport.isContains(browser, "uc") === true) {
                            item = "uc"
                        } else if (passport.isContains(browser, "bidu") === true) {
                            item = "baidu"
                        }
                        var icon = ITChangeMapping(item, "browser")
                        return "<center title='" + d.browser_family + '&#10;' + d.user_agent + "'>" + icon + "</center>";
                    }
                }, {
                    field: 'browser_os',
                    title: '系统',
                    width: 60,
                    templet: function(d) {
                        var item, system = d.browser_os.toLowerCase();
                        if (passport.isContains(system, "windows")) {
                            item = "windows";
                        } else if (passport.isContains(system, "linux") || passport.isContains(system, "centos") || passport.isContains(system, "ubuntu") || passport.isContains(system, "unix")) {
                            item = "linux";
                        } else if (passport.isContains(system, "ios") || passport.isContains(system, "mac")) {
                            item = "apple";
                        } else if (passport.isContains(system, "android")) {
                            item = "android";
                        }
                        var icon = ITChangeMapping(item, "system")
                        return "<center title='" + d.browser_os + "'>" + icon + "</center>";
                    }
                }
            ]
        ]
    });
    /*
    //表单自定义校验
    form.verify({
        name: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (!new RegExp("^[a-zA-Z0-9_\\s·]+$").test(value)) {
                return '应用名不能有特殊字符';
            }
            if (/(^\_)|(\__)|(\_+$)/.test(value)) {
                return '应用名首尾不能出现下划线\'_\'';
            }
            if (/^\d+\d+\d$/.test(value)) {
                return '应用名不能全为数字';
            }
        }
    });
    //监听新建应用提交
    form.on('submit(newApp)', function(data) {
        var field = data.field; //当前容器的全部表单字段，名值对形式：{name: value}
        passport.ajax("/api/user/app/", function(res) {
            if (res.code == 0) {
                popup("已新建应用");
                // 重载表格数据
                table.reload("userapps", options);
            }
        }, {
            data: field,
            method: "post",
            beforeSend: function() {
                //禁用按钮防止重复提交
                $("#newAppSubmit").attr({
                    disabled: "disabled"
                });
                $('#newAppSubmit').addClass("layui-disabled");
            },
            complete: function() {
                $('#newAppSubmit').removeAttr("disabled");
                $('#newAppSubmit').removeClass("layui-disabled");
            }
        });
        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });
    */
    //输出接口
    exports("security", null);
});