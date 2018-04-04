/*
    基本设置页面
*/

layui.define(["passport", "element", "form", "layer", "laydate", "util", "upload"], function(exports) {
    var passport = layui.passport,
        element = layui.element,
        form = layui.form,
        layer = layui.layer,
        $ = layui.jquery,
        laydate = layui.laydate,
        util = layui.util,
        upload = layui.upload;
    //显示当前tab
    if (location.hash) {
        element.tabChange('user', location.hash.replace(/^#/, ''));
    }
    //监听tab切换
    element.on('tab(user)', function() {
        var othis = $(this),
            layid = othis.attr('lay-id');
        if (layid) {
            location.hash = layid;
        }
    });
    //初始化生日输入框时间选择器
    laydate.render({
        elem: '#birthday',
        theme: "molv",
        done: function(value, date, endDate) {
            $('#birthday').val(value);
        }
    });
    //实时显示个性域名
    $('#domain_name').on("input propertychange", function() {
        var value = $(this).val();
        $('#domain_name_suffix').html(value);
    });
    //表单自定义校验
    form.verify({
        nick_name: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (value) {
                if (safeCheck(value) === false) {
                    return '昵称存在违规特殊字符';
                }
                if (value.length < 2 || value.length > 49) {
                    return '昵称长度不能小于2或大于49';
                }
            }
        },
        domain_name: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (value) {
                if (!new RegExp("^[a-z][a-z0-9_\\s·]+$").test(value)) {
                    return '个性域名不合法：以英文开头全部小写且无特殊字符';
                }
                if (/(^\_)|(\__)|(\_+$)/.test(value)) {
                    return '个性域名首尾不能出现下划线\'_\'';
                }
                if (/^\d+\d+\d$/.test(value)) {
                    return '个性域名不能全为数字';
                }
                if (value.length < 5 || value.length > 32) {
                    return '个性域名长度不能小于5或大于32';
                }
            }
        },
        nowpass: function(value, item) {
            if (value.length < 6 || value.length > 30 || value.indexOf(" ") != -1) {
                return '密码必须6到30位，且不能出现空格';
            }
        },
        newpass: function(value, item) {
            var nowpass = $('#nowpass').val();
            if (nowpass == value) {
                return '新密码要求与当前密码不能一致';
            }
            if (value.length < 6 || value.length > 30 || value.indexOf(" ") != -1) {
                return '新密码必须6到30位，且不能出现空格';
            }
        },
        repass: function(value, item) {
            var newpass = $('#newpass').val();
            if (newpass != value) {
                return '两次新密码输入不一致';
            }
        }
    });
    //监听修改资料提交
    form.on('submit(profile)', function(data) {
        var field = data.field; //当前容器的全部表单字段，键值对形式：{name: value}
        var profileMap = {
            nick_name: "个性昵称",
            domain_name: "个性域名",
            birthday: "生日",
            location: "城市",
            gender: "性别",
            signature: "签名"
        };
        passport.ajax("/api/user/profile/?Action=profile", function(res) {
            console.log(res);
            if (res.code == 0) {
                popup("已修改基本资料");
                //更新缓存
                for (var key in field) {
                    layui.cache.user[key] = field[key];
                }
                //若修改了相关项则设置禁用
                if (res.lock.nick_name) {
                    $("#nick_name").attr({
                        disabled: "disabled"
                    });
                    $('#nick_name').addClass("layui-disabled");
                }
                if (res.lock.domain_name) {
                    $("#domain_name").attr({
                        disabled: "disabled"
                    });
                    $('#domain_name').addClass("layui-disabled");
                }
                //更新导航中昵称
                $('#nav_nickname').text(field.nick_name || '');
            } else {
                var tip = res.msg;
                var err = '';
                for (var index in res.invalid) {
                    err += profileMap[res.invalid[index]] + " ";
                }
                popup(tip + "：" + err);
            }
        }, {
            data: field,
            method: "put",
            msgprefix: false,
            beforeSend: function() {
                //禁用按钮防止重复提交
                $("#profileSubmit").attr({
                    disabled: "disabled"
                });
                $('#profileSubmit').addClass("layui-disabled");
            },
            complete: function() {
                $('#profileSubmit').removeAttr("disabled");
                $('#profileSubmit').removeClass("layui-disabled");
            },
            fail: function(res) {
                if (res.code != 0) {
                    var tip = res.msg;
                    var err = '';
                    for (var index in res.invalid) {
                        err += profileMap[res.invalid[index]] + " ";
                    }
                    popup(tip + "：" + err);
                }
            }
        });
        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });
    //监听修改密码提交
    form.on('submit(password)', function(data) {
        var field = data.field; //当前容器的全部表单字段，键值对形式：{name: value}
        passport.ajax("/api/user/profile/?Action=password", function(res) {
            console.log(res);
            if (res.code == 0) {
                popup("已修改密码");
            }
        }, {
            data: field,
            method: 'put',
            msgprefix: '修改密码失败：',
            beforeSend: function() {
                //禁用按钮防止重复提交
                $("#passwordSubmit").attr({
                    disabled: "disabled"
                });
                $('#passwordSubmit').addClass("layui-disabled");
            },
            complete: function() {
                $('#passwordSubmit').removeAttr("disabled");
                $('#passwordSubmit').removeClass("layui-disabled");
            }
        })
        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });
    //监听偏好设置提交
    form.on('submit(like)', function(data) {
        function setCookie(name, value) {
            document.cookie = name + "=" + escape(value) + "; path=/";
        }
        var language = data.field.language;
        if (language) {
            setCookie("locale", language);
        }
        popup("已更新偏好设置");
        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });
    /* 头像上传部分 */
    //弹出框水平垂直居中
    (window.onresize = function() {
        var win_height = $(window).height();
        var win_width = $(window).width();
        if (win_width <= 768) {
            $(".tailoring-content").css({
                "top": (win_height - $(".tailoring-content").outerHeight()) / 2,
                "left": 0
            });
        } else {
            $(".tailoring-content").css({
                "top": (win_height - $(".tailoring-content").outerHeight()) / 2,
                "left": (win_width - $(".tailoring-content").outerWidth()) / 2
            });
        }
    })();
    //弹出图片裁剪框
    $("#uploadAvatar").on("click", function() {
        $(".tailoring-container").toggle();
    });
    //选择图片
    $('#chooseImg').change(function() {
        var file = this;
        if (!file.files || !file.files[0]) {
            return;
        }
        var reader = new FileReader();
        reader.onload = function(evt) {
            var replaceSrc = evt.target.result;
            //更换cropper的图片
            $('#tailoringImg').cropper('replace', replaceSrc, false); //默认false，适应高度，不失真
        }
        reader.readAsDataURL(file.files[0]);
    });
    //关闭裁剪框
    $('.close-tailoring').click(function() {
        $(".tailoring-container").toggle();
    });
    //cropper图片裁剪
    $('#tailoringImg').cropper({
        aspectRatio: 1 / 1, //默认比例
        preview: '.previewImg', //预览视图
        guides: false, //裁剪框的虚线(九宫格)
        autoCropArea: 0.5, //0-1之间的数值，定义自动剪裁区域的大小，默认0.8
        movable: false, //是否允许移动图片
        dragCrop: true, //是否允许移除当前的剪裁框，并通过拖动来新建一个剪裁框区域
        movable: true, //是否允许移动剪裁框
        resizable: true, //是否允许改变裁剪框的大小
        zoomable: true, //是否允许缩放图片大小
        mouseWheelZoom: true, //是否允许通过鼠标滚轮来缩放图片
        touchDragZoom: true, //是否允许通过触摸移动来缩放图片
        rotatable: true, //是否允许旋转图片
        crop: function(e) {
            // 输出结果数据裁剪图像。
        }
    });
    //旋转
    $(".cropper-rotate-btn").on("click", function() {
        $('#tailoringImg').cropper("rotate", 45);
    });
    //复位
    $(".cropper-reset-btn").on("click", function() {
        $('#tailoringImg').cropper("reset");
    });
    //换向
    var flagX = true;
    $(".cropper-scaleX-btn").on("click", function() {
        if (flagX) {
            $('#tailoringImg').cropper("scaleX", -1);
            flagX = false;
        } else {
            $('#tailoringImg').cropper("scaleX", 1);
            flagX = true;
        }
        flagX != flagX;
    });
    //裁剪后的处理
    $("#sureCut").on("click", function() {
        if ($("#tailoringImg").attr("src") == null) {
            return false;
        } else {
            var cas = $('#tailoringImg').cropper('getCroppedCanvas', {
                width: 336,
                imageSmoothingQuality: "high"
            }); //获取被裁剪后的canvas
            var base64url = cas.toDataURL('image/png'); //转换为base64地址形式
            var base64size = showSize(base64url);
            console.log("裁剪后图片大小：" + base64size + "KB");
            if (base64size > 2 * 1024) {
                popup("图片超出限定大小，请重新裁剪！");
                return false;
            }
            //执行上传
            passport.ajax("/api/user/upload/?callableAction=UpdateAvatar", function(res) {
                console.log(res);
                if (res.code == 0) {
                    popup("已更新头像");
                    layui.cache.user.avatar = res.imgUrl;
                    $("#avatar").prop("src", base64url);
                    $('#nav_avatar').prop('src', base64url);
                    //关闭裁剪框
                    $(".tailoring-container").toggle();
                }
            }, {
                data: {
                    picStr: base64url.replace('data:image/png;base64,', '')
                },
                beforeSend: function() {
                    //禁用按钮防止重复提交
                    $("#sureCut").attr({
                        disabled: "disabled"
                    });
                    $('#sureCut').addClass("l-btn-disable");
                },
                complete: function() {
                    //启用按钮
                    $('#sureCut').removeAttr("disabled");
                    $('#sureCut').removeClass("l-btn-disable");
                }
            });
        }
    });
    function showSize(base64url) {
        //获取base64图片大小，返回KB数字
        var str = base64url.replace('data:image/png;base64,', '');
        var equalIndex = str.indexOf('=');
        if (str.indexOf('=') > 0) {
            str = str.substring(0, equalIndex);
        }
        var strLength = str.length;
        var fileLength = parseInt(strLength - (strLength / 8) * 2);
        // 由字节转换为KB
        var size = "";
        size = (fileLength / 1024).toFixed(2);
        var sizeStr = size + ""; //转成字符串
        var index = sizeStr.indexOf("."); //获取小数点处的索引
        var dou = sizeStr.substr(index + 1, 2) //获取小数点后两位的值
        if (dou == "00") { //判断后两位是否为00，如果是则删除00                
            return sizeStr.substring(0, index) + sizeStr.substr(index + 3, 2)
        }
        return parseInt(size);
    }
    //输出接口
    exports('setting', null);
});