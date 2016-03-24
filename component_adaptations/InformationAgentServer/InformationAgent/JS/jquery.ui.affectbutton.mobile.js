(function($, undefined) {

// basically just overwrite the _eventMap function in ui.affectbutton, i.e. use
// the originally declared handlers but bind to jQueryMobile's "virtual" events
var _replace = ['mousedown', 'mousemove', 'mouseup'];
var _super = $.ui.affectbutton.prototype._eventMap;
$.ui.affectbutton.prototype._eventMap = function() {
	var m = _super.call(this);
	$.each(m, function(k, v) {
		if ($.inArray(k, _replace) >= 0) {
			delete m[k];
			m['v' + k] = function(e) {
				// TODO if i read jqm docs correctly v.call(this,e) should work?
				return v.call(this, e.pageX ? e : e.originalEvent); 
			}
		}
	});
	return m;
};

// TODO autoenhance some elements?
// How about $(input[type="affect]) -- not really valid HTML5, of course...

})(jQuery);
