
jQ(function() {
	if(jQ.support.cors && !(typeof(window.getSelection) === 'undefined')) {
		jQ(window).on("copy", function() { jQ.post("http://gu-text-catcher.appspot.com/capture", {selection: window.getSelection().toString(), path: window.location.pathname}); });
	}
});