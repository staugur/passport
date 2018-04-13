/*
    反馈页面
*/

layui.define(["form", "layedit", "layer"], function(exports) {
    'use strict';
    var form = layui.form,
        layedit = layui.layedit,
        layer = layui.layer,
        $ = layui.jquery;
    /*
    //初始化编辑器
    var editorIndex = layedit.build('editor', {
        tool: ['strong', 'italic', 'underline', 'del', '|', 'left', 'center', 'right'],
        height: 120,
        uploadImage: {
            url: '/api/user/upload2/',
            type: 'post',
        }
    });
    */
    //表单自定义校验
    form.verify({
        newemail: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (value) {
                if (!new RegExp("^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$").test(value)) {
                    return '邮箱格式不正确';
                }
            }
        }
    });
    //监听反馈提交
    form.on('submit(feedback)', function(data) {
        var field = data.field; //当前容器的全部表单字段，键值对形式：{name: value}
        console.log(field);
        var content = layedit.getContent(editorIndex);
        console.log(content);
        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });
    //输出接口
    exports('feedback', null);
});