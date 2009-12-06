// function to calculate local time
// in a different city
// given the city's UTC offset
function calcTime(city, offset) {
    // create Date object for current location
    d = new Date();
    // convert to msec
    // add local time zone offset
    // get UTC time in msec
    utc = d.getTime() + (d.getTimezoneOffset() * 60000);
    // create new Date object for different city
    // using supplied offset
    return utc + 3600000*offset;
	//nd = new Date(utc + (3600000*offset));
    // return time as a string
    //return nd;
}

function get_current_date(){
    return calcTime('seattle', -8);
    
    
//    var month = currentTime.getMonth() + 1;
//   var day = currentTime.getDate();
//    var year = currentTime.getFullYear();

//    if (day < 10){
//       day = "0" + day;
//    }
/*    var hours = currentTime.getHours();
    var minutes = currentTime.getMinutes();
    if (minutes < 10){
       minutes = "0" + minutes;
    }
    if (hours > 11) {
        var t = 'PM';
        if (hours > 12) {
            hours -= 11;
        }
    }
    else 
        var t = 'AM';
    
    return hours + ': + minutes + ' ' + t; */
	//	return month + "/" + day + "/" + year;  	
}

