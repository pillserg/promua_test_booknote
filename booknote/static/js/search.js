//fifo flash
$(document).ready(function(){
    var search_box = $('form#searchform input#search_input');
    var search_query = $('span#search_query').text();
    
    if (search_query.length){
        search_box.val(search_query);
        $('ul.entries').highlight(search_query);
        $('ul.entries a').removeHighlight();
    } else {
        search_box.focus();
    };
    
    
});
