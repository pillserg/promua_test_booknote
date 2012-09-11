// requires jQuery-Tokeninput
$(document).ready(function(){
    var config = {
        preventDuplicates: true,
    };
    var json = $('span.json_autocomplite_init_data').text()
    if (json.length){
        config.prePopulate = eval(json);
    };
    
    $('input#authors').tokenInput('/authors_autocomplite', config)
    
});
