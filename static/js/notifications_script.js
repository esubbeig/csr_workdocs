var box  = document.getElementById('box');
var down = false;


function toggleNotifi(){
	if (down) {
		box.style.height  = '0px';
		box.style.opacity = 0;
		down = false;
	}else {
		box.style.height  = '510px';
		box.style.opacity = 1;
		down = true;
	}
	$('#notification_cnt_span').text('0');
}

$(document).ready(function(){

	// defining a function
	$.fn.get_notifications_ajax = function(){

		$.ajax({
			url : '/get_notifications',
			type : 'get',
			dataType : 'json',
			success : function(data){
				$('.notifi-box').html(data.html_form);
			}
		});

	}

	function get_notifications_count() {

		$.ajax({
			url : '/get_notifications_count',
			type : 'get',
			dataType : 'json',
			success : function(data){
				
				$('#notification_cnt_span').text(data.total_notifications);
			}
		});
	}

	setInterval(get_notifications_count, 200000);

	$('.notification_icon').click(function(){

		$.fn.get_notifications_ajax();

	});

});