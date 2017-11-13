$(document).ready(function() {
		// JQuery code to be added in here.

$("#about-btn").click( function(event) {
			alert("You clicked the button using JQuery!");
		});


	$("p").hover( function() {
		$(this).css('color', 'red');
	},
	function() {
		$(this).css('color', 'blue');
	});
	
	$("#about-btn").click( function(){
    $("#about-btn").addClass("btn btn-primary");
	});
	
	$("#about-btn").click( function(event) {
		msgstr = $("#msg").html()
		msgstr = msgstr + "ooo"
		$("#msg").html(msgstr)
	 });
});


$('#suggestion').keyup(function(){
		var query;
		query = $(this).val();
		$.get('/rango/suggest/', {suggestion: query}, function(data){
			$('#cats').html(data);
		});
	});

    $('.rango-add').click(function(){
	    var catid = $(this).attr("data-catid");
        var url = $(this).attr("data-url");
        var title = $(this).attr("data-title");
        var me = $(this)
	    $.get('/rango/add/', {category_id: catid, url: url, title: title}, function(data){
	                   $('#pages').html(data);
	                   me.hide();
	               });
	    });

	});