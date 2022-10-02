jQuery(document).ready(function($){
  
    $('.button#enter').on('click', function(e){
        var app_vame = 'osw:'
        $("h1").text("");
        if (document.location.search) window.location = app_vame + document.location.search.slice(1);
        else window.location = app_vame;
        });
  
    $('.button#download').on('click', function(e){
        e.preventDefault();
        location.href="https://github.com/NoneType4Name/OceanShipsWar/releases/latest/download/OceanShipsWar.exe";});

    $('.button#about').on('click', function(e){
        location.href= './about';});
})