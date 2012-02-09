$(function(){
	$('#jcrop_target').Jcrop({
		onChange: setCoords,
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