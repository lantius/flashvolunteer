function load_title(title){
	document.title = 'FV - ' + title;
}

function load_header(header){
	if (header != '')
    	$('#title_block').html('<h1>'+header+'</h1>');
    else
	   $('#title_block').remove();
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
    $("#navtabs li a").each( 
       function(){
          if ($(this).attr('id') == 'l_' + active){
            $(this).addClass('current');
          }
          else
              $(this).removeClass('current');
       }
    )
}

