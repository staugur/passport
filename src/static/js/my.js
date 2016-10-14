            function postForm(authurl, nextUrl) {
                $.ajax({
                    url: authurl,
                    method: 'POST',
                    datatype: 'json',
                    data: $('#UserLoginFormId').serialize(),
                    success: function(res) {
                        console.log(res);
                        if (res.loggedIn == true){
                            window.location.href=nextUrl;
                        } else {
                            document.getElementById("login_error").innerHTML=res.error;
                        }
                    },
                });
            };
