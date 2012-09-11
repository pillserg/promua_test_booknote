//fifo flash
function flash_put(msg){
    $('div.metanav').after($('<div class="flash">' + msg + '</div>'))
};


function flash_pop(){
    $('div.metanav').next('div.flash').remove()
};

$(document).ready(function(){

});
