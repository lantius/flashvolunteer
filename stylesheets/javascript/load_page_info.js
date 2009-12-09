function load_title(title){
	$('title').html('FV - ' + title);
}

function load_header(header){
	if (header != '')
    	$('#pagespectitle').html('<h1>'+header+'</h1>');
    else
	   $('#pagespectitle').remove();
}

function set_active(active){
	$("#navtabs li").each( 
	   function(){
	   	  if ($(this).attr('id') == active+'link'){
		  	$(this).addClass('current');
		  }
          else
		      $(this).removeClass('current');
	   }
	)
}

