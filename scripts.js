function open_with_arg(args){
    var split_url = document.location.pathname.split('/');
    var page_name = split_url[split_url.length-2];
    var app_name = 'osw://'
    fetch('https://api.github.com/repos/NoneType4Name/OceanShipsWar/releases/latest').then(function(request){
                    console.log(request);
                    return request.json()}).then(function(data){
        if (data.message!="Not Found"){
            window.location = app_name + page_name + '/' + data.tag_name + args;
        }
        else {
            alert('project is closed');
        }})
}
$(window).on("load", function() {
    if (document.location.search) {
        open_with_arg(document.location.search);
    };
});
jQuery(document).ready(function($){
    $('.button#enter').on('click', function(e){
        open_with_arg(document.location.search);
    });
  
    $('.button#download').on('click', function(e){
        e.preventDefault();
        location.href = "https://github.com/NoneType4Name/OceanShipsWar/releases/latest/download/OceanShipsWar.exe";
    });

    $('.button#about').on('click', function(e){
        location.href= './about';});
})