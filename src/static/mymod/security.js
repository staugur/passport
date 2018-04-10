/*
    安全设置页面
*/

layui.define(["passport", "table", "element", "form", "layer", "util", "laytpl"], function(exports) {
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
        {{# } }}\
    ';
    passport.ajax("/api/user/security/?Action=getSessions&getCurrentSession=true&getOtherSession=true", function(res) {
        if (res.code === 0) {
            var remote_ip_info = {
                area: ""
            }
            $.getScript(window.location.protocol + '//int.dpool.sina.com.cn/iplookup/iplookup.php?format=js&ip=' + res.data.CurrentSession.ip, function() {
                res.data.CurrentSession.area = remote_ip_info.area || '';
            });
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
                    width: 100
                }, {
                    field: 'login_area',
                    title: '地区与ISP'
                }, {
                    field: 'login_time',
                    title: '时间',
                    width: 160,
                    templet: function(d) {
                        return util.toDateString(d.login_time * 1000);
                    }
                }, {
                    field: 'login_type',
                    title: '方式',
                    width: 70,
                    templet: function(d) {
                        return passport.socialAccountVisiblenameMapping(passport.loginTypeNameMapping(d.login_type));
                    }
                }, {
                    field: 'browser_device',
                    title: '设备',
                    width: 80
                }, {
                    field: 'browser_family',
                    title: '浏览器',
                    width: 125,
                    templet: function(d) {
                        var str = d.browser_family;
                        str = str.split(' '); //先按照空格分割成数组
                        str.pop(); //删除数组最后一个元素
                        str = str.join(' '); //在拼接成字符串
                        return str;
                    }
                }, {
                    field: 'browser_os',
                    title: '操作系统',
                    width: 120
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