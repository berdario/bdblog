$(function(){ // supply the whole file as an handler to jQuery when it's ready

// Jcrop

$(function(){
	$('.jcrop_target').Jcrop({
		onSelect: setCoords,
		aspectRatio: 1
	});
});

function setCoords(coords)
{
	$('#id_x').val(coords.x);
	$('#id_y').val(coords.y);
	$('#id_size').val(coords.w);
}

// WebRTC webcam access (from Ryan Paul and stackoverflow)

if (navigator.webkitGetUserMedia){
	$("#live").show()
	$("#shutter").show()
	navigator.webkitGetUserMedia("video",
		  function(stream) {
			  $("#live").src = window.webkitURL.createObjectURL(stream)
		  },
		  function(err) {
			  console.log("Unable to get video stream!")
		  }
	)
}

function snap() {
	live = $("#live")
	snapshot = $("#snapshot")

	// Make the canvas the same size as the live video
	snapshot[0].width = live[0].clientWidth
	snapshot[0].height = live[0].clientHeight

	// Draw a frame of the live video onto the canvas
	c = snapshot[0].getContext("2d")
	c.drawImage(live, 0, 0, snapshot.width, snapshot.height)
	live.hide()
	snapshot.show()

	// Copy the data to the first hidden field
	$("#id_canvasData")[0].value = snapshot[0].toDataURL()

}

$('#shutter').click(snap)

})