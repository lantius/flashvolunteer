function set_page_loader(content_selector){	
	$(content_selector + ' a.fv').each(function(){
		$(this).click(function(){
			if ($(this).attr('href').search('http://') > -1){
				var href = $(this).attr('href').substring($(this).attr('href').indexOf('/', 7));
			}
			else{
				var href = $(this).attr('href');
			}
			$.address.value(href.replace(/^#/, ''));
		});
		
		$(this).address(function(){
			if ($(this).attr('href').search('http://') > -1){
				var href = $(this).attr('href').substring($(this).attr('href').indexOf('/', 7));
			}
			else{
				var href = $(this).attr('href');
			}
			return href.replace(/^#/, '');
		});
	});
}