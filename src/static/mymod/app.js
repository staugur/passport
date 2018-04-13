/*
    SSO应用管理页面
*/

layui.define(["passport", "table", "element", "form", "layer", "util"], function(exports) {
    'use strict';
    var passport = layui.passport,
        table = layui.table,
        element = layui.element,
        form = layui.form,
        layer = layui.layer,
        $ = layui.jquery,
        util = layui.util;
    //显示当前tab
    if (location.hash) {
        element.tabChange('appList', location.hash.replace(/^#/, ''));
    }
    //监听tab切换
    element.on('tab(appList)', function() {
        var othis = $(this),
            layid = othis.attr('lay-id');
        if (layid) {
            location.hash = layid;
        }
    });
    //定义渲染应用列表函数
    var options = {
        elem: "#userapps",
        height: 315,
        url: "/api/user/app/", //数据接口
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
                    field: 'name',
                    title: '应用名',
                    width: 120
                }, {
                    field: 'description',
                    title: '应用描述',
                    width: 120
                }, {
                    field: 'app_redirect_url',
                    title: '回调域名'
                }, {
                    field: 'ctime',
                    title: '创建时间',
                    width: 160,
                    templet: function(d) {
                        return util.toDateString(d.ctime * 1000);
                    }
                }, {
                    fixed: 'right',
                    width: 160,
                    align: 'center',
                    toolbar: '#userAppBar'
                } //这里的toolbar值是模板元素的选择器
            ]
        ]
    };
    //初始化渲染表格
    table.render(options);
    //监听工具条
    table.on('tool(userAppTable)', function(obj) { //注：tool是工具条事件名，userAppTable是table原始容器的属性 lay-filter="对应的值"
        var data = obj.data; //获得当前行数据
        var layEvent = obj.event; //获得 lay-event 对应的值（也可以是表头的 event 参数对应的值）
        if (layEvent === 'detail') { //查看
            var mtime = data.mtime === null ? '暂无修改' : util.toDateString(data.mtime * 1000);
            layer.open({
                type: 1,
                skin: 'layui-layer-molv', //样式类名
                shade: 0,
                shadeClose: true,
                area: ['510px', '340px'],
                title: "查看 " + data.name + " 应用详情",
                content: '<table class="layui-table"><colgroup><col width="150"><col width="200"><col></colgroup><tbody><tr><td>应用名</td><td>' + data.name + '</td></tr><tr><td>描述</td><td>' + data.description + '</td></tr><tr><td>app_id</td><td>' + data.app_id + '</td></tr><tr><td>app_secret</td><td>' + data.app_secret + '</td></tr><tr><td>回调域名</td><td>' + data.app_redirect_url + '</td></tr><tr><td>创建时间</td><td>' + util.toDateString(data.ctime * 1000) + '</td></tr><tr><td>修改时间</td><td>' + mtime + '</td></tr></tbody></table>'
            });
        } else if (layEvent === 'del') { //删除
            layer.confirm('真的删除 ' + data.name + ' 应用么？', {
                icon: 3,
                title: '温馨提示'
            }, function(index) {
                layer.close(index);
                //向服务端发送删除指令
                passport.ajax("/api/user/app/", function(res) {
                    if (res.code == 0) {
                        popup("已删除应用");
                        obj.del(); //删除对应行（tr）的DOM结构，并更新缓存
                    }
                }, {
                    data: {
                        "name": data.name
                    },
                    method: "delete"
                });
            });
        } else if (layEvent === 'edit') { //编辑
            layer.open({
                type: 2,
                skin: 'layui-layer-molv', //样式类名
                shadeClose: true, //开启遮罩关闭
                shade: 0,
                area: ['400px', '280px'],
                title: "编辑 " + data.name + " 应用",
                content: "/user/app/?Action=editView",
                success: function(layero, index) {
                    // 设置子页面表单的值
                    var body = layer.getChildFrame('body', index);
                    body.find('#name').val(data.name);
                    body.find('#description').val(data.description);
                    body.find('#app_redirect_url').val(data.app_redirect_url);
                },
                end: function(layero, index) {
                    // 获取隐藏域的值，是个json串
                    var upvalue = document.getElementById("editView").value;
                    if (upvalue) {
                        try {
                            // 此处若不是正常json串则发生异常并终止执行；正常结果时表示已经成功修改应用。
                            upvalue = JSON.parse(upvalue);
                            // 检测
                            if (upvalue.name && upvalue.description && upvalue.app_redirect_url) {
                                // 确保有过修改才更新表格相应字段
                                if (upvalue.name != data.name || upvalue.description != data.description || upvalue.app_redirect_url != data.app_redirect_url) {
                                    // 同步更新缓存对应的值
                                    obj.update({
                                        name: upvalue.name,
                                        description: upvalue.description,
                                        app_redirect_url: upvalue.app_redirect_url,
                                        mtime: Math.round(new Date().getTime() / 1000).toString()
                                    });
                                }
                                // 清空隐藏域的值
                                document.getElementById("editView").value = '';
                            }
                        } catch (err) {
                            console.warn(err);
                        }
                    }
                }
            });
        }
    });
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
    //输出接口
    exports("app", null);
});