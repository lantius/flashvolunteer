function get_search_params(){
    if ($('#search_past_events:checked').val()) var past = 'on';
    else var past='';

    var nval = $('#event_search select.neighborhood_select option:selected').val();
    if (nval && nval!='none') 
       var nid = $('#event_search select.neighborhood_select option:selected').val();
    else 
       var nid='';
    
    //var cval = $('#event_search select.interest_category_select option:selected').text()
    //if (cval && cval!='none') var cid = cval;
    //else var cid='';
	
	return 'past_events='+past+'&neighborhood='+nid;//+'&interestcategory='+cid;
}

function event_search_submit(bookmark){
	search_params = get_search_params();
    build_dialog(100,'?' + search_params);
}

function get_people_search_params(){
    var nval = $('#person_search select.neighborhood_select option:selected').val();
    if (nval && nval!='none') 
       var nid = $('#person_search select.neighborhood_select option:selected').val();
    else 
       var nid='';
    
    return 'neighborhood='+nid;
}


function people_search_submit(){
    build_dialog(101,'?' + get_people_search_params());
}

function close_dialog(){
	$('#generic_dialog').fadeOut('slow',function(){
        $('#generic_dialog').remove();		
	});
}
function build_dialog(d_type, id){

	switch(d_type){
        case 0:
            var url = '/events/ongoing';
            break;
		case 1:
            var url = '/events/upcoming';
		    break;
		case 2:
            var url = '/events/recommended';
            break;
		case 3: 
		    var url = '/events/hosted/volunteer/'+id;
            break;
        case 4: 
		    var url = '/events/past/volunteer/'+id;
            break;
			
        case 5: 
            var url = '/events/upcoming/volunteer/'+id;
            break;
        case 6:
            var url = '/events/past/category/'+id;
            break;
        case 7:
            var url = '/events/upcoming/neighborhood/'+id;
            break;
        case 8:
            var url = '/events/past/neighborhood/'+id;
            break;
        case 9: 
            var url = '/events/past/coordinated/'+id;
            break;
        case 10:
            var url = '/events/upcoming/category/'+id;
            break;			
        case 11:
            var url = '/events/ongoing/neighborhood/'+id;
            break;
												
		case 20:
		    var url = '/events/'+id+'/attendees';
		    break;
		case 21:
		    var url = '/team/list';
			break;
		case 22:
		    var url = '/category/'+id + '/volunteers';
			break;
        case 23:
            var url = '/neighborhoods/'+id + '/volunteers_live';
            break;
        case 24:
            var url = '/neighborhoods/'+id + '/volunteers_work';
            break;

        case 25:
		    var url = '/volunteers/'+id+'/team';
			break;
			
			
		case 100:
		    var url = '/events/search' + id;
			break;
        case 101:
            var url = '/volunteers/search' + id;
            break;		
			
			
		case 200: 
		    var url = '/events/'+id + '/volunteer';
			break; 	
	}

    $.get(url, function(data){
       $('#dialogs').append(data);
       $('.closedialog').click(close_dialog);
     });

}