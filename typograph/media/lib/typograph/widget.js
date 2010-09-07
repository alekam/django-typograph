$(document).ready(function(){
    $('.typograph').each(function(index){
        $(this).parent().append(new typo_btn($(this).attr('id')));
    });
});
