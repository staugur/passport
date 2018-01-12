//聚焦
var input = document.querySelectorAll('.ui-input input');
input.forEach(function(val, i) { 
	val.onfocus = function() {
		this.parentNode.className += ' focus';
	}
	val.onblur = function() {
		this.parentNode.className = this.parentNode.className.replace(' focus', '');
	}
});