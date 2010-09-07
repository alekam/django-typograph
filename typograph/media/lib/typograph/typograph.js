/**
 * Typograph for text fields
 */
function typo_btn(id, options){
    this.typo_url = '/tools/typograph/';
    this.img = '/images/typograph.png';
    if (options) {
        if ('url' in options)
            this.typo_url =  options.url;
        if ('img' in options)
            this.img =  options.img;
    }
    
    var $typo = $('<img id="typo'+id+'" src="'+this.img+'" />');
    $typo.css('vertical-align','bottom')
         .css('padding-bottom','2px')
         .css('cursor', 'pointer');
    $typo.attr('typo_url', this.typo_url);
    $typo.click(function(){
        $.post($(this).attr('typo_url'), {'text': $('#'+id).val()}, function(data){
            $('#'+id).val(data);
        });
        return false;
    });
    return $typo;
}
