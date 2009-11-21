function event_search_submit(){
    if ($('#search_past_events:checked').val()) var past = 'on';
    else var past='';

    var nval = $('#event_search select.neighborhood_select option:selected').val();
    if (nval && nval!='none') 
       var nid = $('#event_search select.neighborhood_select option:selected').val();
    else 
	   var nid='';
    
    var cval = $('#event_search select.interest_category_select option:selected').text()
    if (cval && cval!='none') var cid = cval;
    else var cid='';
    
    build_dialog(100,'?past_events='+past+'&neighborhood='+nid+'&interestcategory='+cid);
}


function people_search_submit(){
    var nval = $('#person_search select.neighborhood_select option:selected').val();
    if (nval && nval!='none') 
	   var nid = $('#person_search select.neighborhood_select option:selected').val();
    else 
	   var nid='';
    
    build_dialog(101,'?neighborhood='+nid);
}

function close_dialog(){
    $('#generic_dialog').remove();
}
function build_dialog(d_type, id){

	switch(d_type){
		case 1:
            var url = '/events/upcoming/1';
		    break;
		case 2:
            var url = '/events/recommended/1';
            break;
		case 3: 
		    var url = '/events/hosted/volunteer/'+id+'/1';
            break;
        case 4: 
		    var url = '/events/past/volunteer/'+id+'/1';
            break;
        case 5: 
            var url = '/events/upcoming/volunteer/'+id+'/1';
            break;
        case 6:
            var url = '/events/past/category/'+id + '/1';
            break;
        case 7:
            var url = '/events/upcoming/neighborhood/'+id + '/1';
            break;
        case 8:
            var url = '/events/past/neighborhood/'+id + '/1';
            break;
											
		case 20:
		    var url = '/events/'+id+'/attendees/1';
		    break;
		case 21:
		    var url = '/team/1';
			break;
		case 22:
		    var url = '/category/'+id + '/volunteers/1';
			break;
        case 23:
            var url = '/neighborhoods/'+id + '/volunteers_live/1';
            break;
        case 24:
            var url = '/neighborhoods/'+id + '/volunteers_work/1';
            break;

        case 25:
		    var url = '/volunteers/'+id+'/team/1';
			break;
			
			
		case 100:
		    var url = '/events/search' + id;
			break;
        case 101:
            var url = '/volunteers/search' + id;
            break;			
	}

    $.get(url, function(data){
       $('#bottom').append(data);
       $('.closedialog').click(close_dialog);
     });

}