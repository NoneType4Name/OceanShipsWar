jQuery(document).ready(function($){
  
  $('.button#enter').on('click', function(e){
    if (document.location.search) location.href = 'osw://' + document.location.search;
    else location.href = 'osw:'
  });
  
  $('.button#download').on('click', function(e){
    e.preventDefault();
    location.href="https://github.com/NoneType4Name/OceanShipsWar/releases/latest/download/OceanShipsWar.exe"
  });
  
});
