// 
// mtaTwitterStatuses.js
// 
// A modification of the official Twitter JavaScript badge originally found
// here:
//
//    http://twitter.com/account/badge
//
// This modification provides insertion of the user's image (linking to their
// twitter page), displaying one or more of the user's recent tweets (including
// time posted, linking to that tweet's permalink), plus a bunch of CSS hooks
// for the list items.
//
// This package contains an html file and associated CSS & image files, but they 
// are merely an example of usage and only this JavaScript file is needed (it
// can be embeded directly in any HTML document, if you prefer).
// 
// v0.1   2007-05-02 - Morgan Aldridge <morgant@makkintosshu.com>
//                     Initial release.
// v0.2   2009-01-07 - Morgan Aldridge
//                     Integrated Jon Aquino's IE date parsing fix. Minor HTML
//                     tweaks & function name changes for better namespacing.
// v0.3   2009-01-09 - Morgan Aldridge
//                     Integrated regular expressions for making @replies and
//                     links clickable, thanks to René van Meurs
//                     <info@renevanmeurs.nl>.
// v0.4   2009-02-11 - Morgan Aldridge
//                     Updated regular expressions to find @replies butting up
//                     against punctuation. Some HTML restructuring.
// v0.5   2009-05-05 - Morgan Aldridge
//                     Added feature to filter out @replies, if requested.
// 

var mtaTwitterStatusesFilterReplies = false;

// Make date parseable in IE [Jon Aquino 2007-03-29]
// http://jonaquino.blogspot.com/2006/12/twitter-increasing-number-of-twitters.html
function fixDate(d) {
	var a = d.split(' ');
	var year = a.pop();
	return a.slice(0, 3).concat([year]).concat(a.slice(3)).join(' ');
}

function relativeTime(time_value) {
    var parsed_date = Date.parse(time_value);
    
    var relative_to = (arguments.length > 1) ? arguments[1] : new Date();
    var delta = parseInt((relative_to.getTime() - parsed_date) / 1000);
    
    if ( delta < 60 ) {
    	return 'less than a minute ago';
    } else if ( delta < 120 ) {
    	return 'about a minute ago';
    } else if ( delta < (45*60) ) {
    	return (parseInt(delta / 60)).toString() + ' minutes ago';
    } else if ( delta < (90*60) ) {
    	return 'about an hour ago';
    } else if ( delta < (24*60*60) ) {
    	return 'about ' + (parseInt(delta / 3600)).toString() + ' hours ago';
    } else if ( delta < (48*60*60) ) {
    	return '1 day ago';
    } else {
    	return (parseInt(delta / 86400)).toString() + ' days ago';
    }
}

function mtaTwitterCallback(obj) {
    var id = obj[0].user.id;
    var statuses_html = '';
    var isEven = false;
    
    statuses_html += "\n<ul>\n";
    
    for ( var i = 0; i < obj.length; i++ ) {
		var tweet_text = obj[i].text;
		
		//console.log("mtaTwitterStatusesFilterReplies = "+mtaTwitterStatusesFilterReplies+"\n");
		//console.log("tweet_text.match(/^@([A-Z0-9_]+)/gi) = "+tweet_text.match(/^@([A-Z0-9_]+)/gi)+"\n");
		if ( !mtaTwitterStatusesFilterReplies || (tweet_text.match(/^@[A-Z0-9_]+/gi) == null) )
		{
			tweet_text = tweet_text.replace(/((http|https|ftp):\/\/(([A-Z0-9][A-Z0-9_-]*)(\.[A-Z0-9][A-Z0-9_-]*)+)(\/*)(:(\d+))?([A-Z0-9_\/.?~-]*))/gi, '<a href="$1">$1</a>');
			tweet_text = tweet_text.replace(/(@([A-Z0-9_]+))/gi, '@<a class="reply" title="$2 on twitter" href="http://twitter.com/$2">$2</a>');
    		
    		statuses_html += '<li class="';
    		if ( i == 0 ) {
    			statuses_html += 'first';
    		} else if ( i == (obj.length - 1) ) {
    			statuses_html += 'last';
    		}
    		if ( isEven ) {
    			statuses_html += ' even';
    		}
    		else {
    			statuses_html += ' odd';
    		}
    		statuses_html += '">';
    		statuses_html += tweet_text;
    		statuses_html += ' <span class="when"><a href="http://twitter.com/' + obj[i].user.screen_name + '/statuses/' + obj[i].id + '">' + relativeTime(fixDate(obj[i].created_at)) + "</a></span></li>\n";
    		
    		isEven = !isEven;
    	}
    }
    statuses_html += "</ul>\n";
    
    document.getElementById('mtaTwitterbody').innerHTML = statuses_html;
}