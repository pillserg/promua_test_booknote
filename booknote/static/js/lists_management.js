// depends on core.js
var G = 0
$(document).ready(function(){
   console.log('lists management init') 
   
   $('a.delete_entry_link').click(function(){
       link = $(this)
       url = link.attr('href')
       $.post(url, function(data){
            if (data.success){
                console.log('callback called')
                link.parents('li.entry').remove()
                flash_put('Entry was successfylly deleted.')
               };
       });
       return false;
   });
   
});
