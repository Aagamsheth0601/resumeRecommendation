$(document).ready(function (e) {
    $("form").on('submit', (function (e) {
        e.preventDefault();
        $.ajax({
            url: "/companysignupcheck",
            type: "POST",
            data: new FormData(this),
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                data = jQuery.parseJSON(data);
                if(data.status=='fail'){
                    $('#error').html('<div class="alert alert-danger alert-dismissible fade show" role="alert">'+data.message+'<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>')
                }else{
                    $('#error').html('<div class="alert alert-success alert-dismissible fade show" role="alert">'+data.message+'<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>')
                }
            }
        });
    }));
});
