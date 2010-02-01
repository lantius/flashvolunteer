function handle_notification_message(notification_message){
    $('#container').append('<div id="dialog" title="Notifications"><p>'+notification_message+'</p></div>');
    $.ui.dialog.defaults.bgiframe = true;
    $(function() {
        $("#dialog").dialog({
            buttons: { "Ok": function() { $(this).dialog("close"); } },
            modal: true,
            draggable: false,
            resizable: false,
        });
    });
}

function handle_header_message(header_message){
	if (header_message){ 
	    $('#message_banner').html('<p>'+header_message+'</p>');
	    $('#message_banner').show();
	}
	else {
	   $('#message_banner').hide();
	};
}