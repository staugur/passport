/*
function postForm(url, nextUrl) {
    $.ajax({
        url: url,
        method: 'POST',
        datatype: 'json',
        data: $('#loginform').serialize(),
        success: function(res) {
            console.log(res);
            if (res.loggedIn == true){
                window.location.href=nextUrl;
            }
        },
        error: function(error){
            console.log(error);
            document.getElementById("error").innerHTML(error);
        }
    });
};
*/