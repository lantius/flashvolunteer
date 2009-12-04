function get_current_datetime(){
    var currentTime = new Date()
    var month = currentTime.getMonth() + 1
    var day = currentTime.getDate()
    var year = currentTime.getFullYear()

    if (day < 10){
       day = "0" + day
    }
    
    var hours = currentTime.getHours()
    var minutes = currentTime.getMinutes()
    if (minutes < 10){
       minutes = "0" + minutes
    }
    if (hours > 11) {
        var t = 'PM';
        if (hours > 12) {
            hours -= 11;
        }
    }
    else 
        var t = 'AM';
    
    return month + "/" + day + "/" + year + t+ hours + ':' + minutes + ' ' + t;
    
    
}
