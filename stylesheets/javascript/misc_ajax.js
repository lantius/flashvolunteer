function set_page_loader(content_selector){	
	$(content_selector + ' a.fv').each(function(){
		$(this).click(function(){
			$.address.value($(this).attr('href').replace(/^#/, ''));
		});
		
		$(this).address(function(){
			return $(this).attr('href').replace(/^#/, '');
		});
	});
}