$(document).ready(function (e) {
    $("form").on('submit', (function (e) {
        e.preventDefault();
        $.ajax({
            url: "/postresume",
            type: "POST",
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                data = jQuery.parseJSON(data);
                $("#yourresume").html('<iframe src="static/resumes/'+data.resume+'" allowfullscreen></iframe>');
            },
            failure: function (){
                $("#yourresume").html('error');
            }
        });
    }));
});
