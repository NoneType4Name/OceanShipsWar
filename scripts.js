jQuery(document).ready(function($){
  
    $('.button#enter').on('click', function(e){
        if (document.location.search) location.href = 'osw:/' + document.location.search;
        else location.href = 'osw:/';
        setTimeout(function(){$("h1").text("Если приложение не запустилось, кажется у вас его нет...")}, 3000);});
  
    $('.button#download').on('click', function(e){
        e.preventDefault();
        location.href="https://github.com/NoneType4Name/OceanShipsWar/releases/latest/download/OceanShipsWar.exe";});

    $('.button#about').on('click', function(e){
        location.href= './about';});
})