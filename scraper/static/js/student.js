var sidebar = 0
function toggleNav() {
    if (sidebar == 0) {
        document.getElementById("sidenav").style.width = "260px";
        document.getElementById("main").style.marginRight = "260px";
        document.getElementById("main").style.marginLeft = "-260px";
        document.getElementById("sidehead1").style.display = "block"
        document.getElementById("sidehead2").style.display = "block"
    } else {
        document.getElementById("sidenav").style.width = "0px";
        document.getElementById("main").style.marginLeft = "0";
        document.getElementById("main").style.marginRight = "0";
        document.getElementById("sidehead1").style.display = "none"
        document.getElementById("sidehead2").style.display = "none"
    }
    sidebar = parseInt(document.getElementById("sidenav").style.width)

}

$(".recBtn").click(function () {
    $(".payment").css("display", "none")
    $(".modal").css("display", "block")
    $(".clear").css("display", "block")
    $(".lds-dual-ring").css("display", "inline-block")
    var btn_id = $(this).attr("id")
    btn_id = btn_id.toString()
    let course_url = $("p#" + btn_id).attr("course-url")
    $.ajax({
        url: course_url,
        data: {},
        dataType: 'json',
        success: function (data) {
            if (data.error) {
                $(".lds-dual-ring").css("display", "none")
                $(".error-text").text(data.error)
            } else if (data.success) {
                $(".lds-dual-ring").css("display", "none")
                $(".error-text").text(data.success + "🙌")
            }
        },
        error: function (data) {
            $(".lds-dual-ring").css("display", "none")
            $(".error-text").text("Something went wrong, Reload your page")
        }
    })
})


$(".close").click(function () {
    $(".error-text").text("")
    $(".lds-dual-ring").css("display", "none")
    $(".modal").css("display", "none")
    $(".clear").css("display", "none")
    $(".payment").css("display", "none")

})

$(".pay").click(function () {
    $(".modal").css("display", "block")
    $(".payment").css("display", "block")


})

$(".dnwBtn").click(function () {
    $(".modal").css("display", "block")
    $(".clear").css("display", "block")
    $(".lds-dual-ring").css("display", "inline-block")
    var button_id = $(this).attr("id")
    button_id = button_id.toString()
    $(".error-text").text("It takes a while if your connection is low, Just chill out 😎🍷🥂")
    $.ajax({
        url: "student/dwnld-" + button_id,
        data: {},
        dataType: 'json',
        success: function (data) {
            if (data.error) {
                $(".lds-dual-ring").css("display", "none")
                $(".error-text").text(data.error)
            } else if (data.success) {
                $(".lds-dual-ring").css("display", "none")
                $(".error-text").text(data.success + "🙌")
            }
        }
    })
})


$("#post-form").on("submit", function() {
    event.preventDefault()
    $(".modal").css("display", "block")
    $(".clear").css("display", "block")
    $(".lds-dual-ring").css("display", "inline-block")
    
    $.ajax({
        url: "student/allcourse",
        type : "POST",
        data : { check : $("#check").is(":checked")},
        success : function(data) {
            if (data.courses_gone){
                $(".lds-dual-ring").css("display", "none")
                for(let i of data.courses_gone){
                    html = '<p>'+i+'</p>'
                    $(".error-text").append(html)
                }
            } else if (data.error) {
                $(".lds-dual-ring").css("display", "none")
                $(".error-text").text(data.error)
            }
        },
    })
})


$(function() {


// This function gets cookie with a given name
function getCookie(name) {
var cookieValue = null;
if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
}
return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
// these HTTP methods do not require CSRF protection
return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
// test that a given url is a same-origin URL
// url could be relative or scheme relative or absolute
var host = document.location.host; // host + port
var protocol = document.location.protocol;
var sr_origin = '//' + host;
var origin = protocol + sr_origin;
// Allow absolute or scheme relative URLs to same origin
return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
    (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
    // or any other URL that isn't scheme relative or absolute i.e relative.
    !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
        // Send the token to same-origin, relative URLs only.
        // Send the token only if the method warrants CSRF protection
        // Using the CSRFToken value acquired earlier
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
}
});

});