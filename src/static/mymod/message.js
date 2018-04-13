/*
    我的消息页面
*/

layui.define(["passport", "util", "layer", "laytpl"], function(exports) {
    'use strict';
    var passport = layui.passport,
        util = layui.util,
        layer = layui.layer,
        laytpl = layui.laytpl,
        $ = layui.jquery;
    laytpl.config({
        open: '<%',
        close: '%>'
    });
    var delAll = $('#LAY_delallmsg'),
        minemsg = $('#LAY_minemsg'),
        msgtpl = '<%# var len = d.data.length;var msgtypemap = {system: "系统消息", product: "产品消息"};var msgstatusmap = {1: "未读", 0: "已读"};var msgmarkmap = {0: "未读", 1: "已读"};\
    if(len === 0){ %>\
      <div class="fly-none">您暂时没有消息</div>\
    <%# } else { %>\
      <ul class="mine-msg">\
      <%# for(var i = 0; i < len; i++){ %>\
        <li data-id="<% d.data[i].msgId %>" data-status="<% d.data[i].msgStatus %>">\
          <blockquote class="layui-elem-quote"><% d.data[i].msgContent %></blockquote>\
          <p><span><% msgstatusmap[d.data[i].msgStatus] %>的<% msgtypemap[d.data[i].msgType] %>：<% layui.util.timeAgo(d.data[i].msgTime*1000) %></span><a href="javascript:;" class="layui-btn layui-btn-xs layui-btn-primary fly-mark">标记为<% msgmarkmap[d.data[i].msgStatus] %></a><a href="javascript:;" class="layui-btn layui-btn-xs layui-btn-danger fly-remove">删除消息</a></p>\
        </li>\
      <%# } %>\
      </ul>\
    <%# } %>',
        delEnd = function(clear) {
            // 当clear为true时或者没有消息列表时清空并显示没有消息
            if (clear || minemsg.find('.mine-msg li').length === 0) {
                minemsg.html('<div class="fly-none">您暂时没有消息</div>');
            }
        };
    //获取用户消息列表
    passport.ajax("/api/user/message/?Action=getList&desc=true&msgStatus=" + passport.getUrlQuery("status", 1), function(res) {
        if (res.code == 0) {
            var html = laytpl(msgtpl).render(res);
            minemsg.html(html);
            if (res.data.length > 0) {
                delAll.removeClass('layui-hide');
            }
        }
    }, {
        method: "get",
        msgprefix: "拉取用户消息失败："
    });
    //标记消息状态
    minemsg.on('click', '.mine-msg li .fly-mark', function() {
        var othis = $(this).parents('li'),
            id = othis.attr('data-id'),
            status = parseInt(othis.attr('data-status'));
        var msgstatusmap = {
                1: "未读",
                0: "已读"
            },
            antimsgstatusmap = {
                0: "未读",
                1: "已读"
            };
        passport.ajax("/api/user/message/?Action=markMessage", function(res) {
            if (res.code == 0) {
                popup("标记消息成功");
                othis.remove();
                delEnd();
            }
        }, {
            data: {
                msgId: id
            },
            method: "post",
            msgprefix: "标记消息失败："
        });
    });
    //删除一条消息
    minemsg.on('click', '.mine-msg li .fly-remove', function() {
        var othis = $(this).parents('li'),
            id = othis.attr('data-id');
        passport.ajax("/api/user/message/?Action=delMessage", function(res) {
            if (res.code == 0) {
                popup("删除消息成功");
                othis.remove();
                delEnd();
            }
        }, {
            data: {
                msgId: id
            },
            method: "delete",
            msgprefix: "删除消息失败："
        });
    });
    //删除全部消息
    delAll.on('click', function() {
        var othis = $(this);
        layer.confirm('确定清空消息吗？<br>此操作将清空所有已读、未读消息！', {
            icon: 3,
            title: '温馨提示'
        }, function(index) {
            passport.ajax("/api/user/message/?Action=clearMessage", function(res) {
                if (res.code == 0) {
                    layer.close(index);
                    othis.addClass('layui-hide');
                    delEnd(true);
                    popup("清空消息成功");
                }
            }, {
                method: "delete",
                msgprefix: "清空消息失败："
            });
        });
    });
    //输出接口
    exports('message', null);
});