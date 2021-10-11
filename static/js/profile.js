$(document).ready(function (e) {
    $("#insertresume").on('submit', (function (e) {
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
                $('#formFile').val('');
                $("#yourresume").html('<iframe src="static/resumes/'+data.resume+'" allowfullscreen></iframe>');
            },
            failure: function (){
                $("#yourresume").html('error');
            }
        });
    }));
    
    $("#searchingjobposition").on('submit', (function (e) {
        e.preventDefault();
        $.ajax({
            url: "/updatejobpositionuser",
            type: "POST",
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                data = jQuery.parseJSON(data);
                $("#message").html('<div class="alert alert-success alert-dismissible fade show" role="alert"> Successfully updated <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
                $("#jobposition").html('Job position currently looking for : ' + data.job);
                $("#job").val('');
            }
        });
    }));
});