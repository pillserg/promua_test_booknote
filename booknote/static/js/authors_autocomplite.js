// requires jQuery-Tokeninput
$(document).ready(function(){
    var config = {
        preventDuplicates: true,
    }
    $('input#authors').tokenInput('/authors_autocomplite', config)
    
});
