function set_openid(openid, pr, submit){
            u = openid.search('<username>')
            if ( u!=-1 ){
                user = prompt('Enter your ' + pr + ' username:')
                openid = openid.substr(0, u) + user      
            };
            var form = $('#login_form')
            form.find('#openid').val(openid)
            if(submit){
                form.submit()  ; 
            };
        };

$(document).ready(function () {
    
});
