(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.scripts=mod.exports;}})(this,function(){"use strict";$(document).foundation();$(document).ready(function(){/*jshint validthis: true */// sidebar accordion menu
$('.toggle-me').attr("href","#");$('#accordion .toggle-me').click(function(event){// $('.toggle-me').event.preventDefault();
event.preventDefault();$(this).parent().find('#dropdown').slideToggle().addClass('opened');$(this).parent().find('.toggle-me').toggleClass('open');});// custom FILE inputs
// $(function(){
// 	$(".field-assetBundleAndroid .wrapper [type=file]").on("change", function(){
// 		var file = this.files[0];
// 		var formdata = new FormData();
// 		formdata.append("file", file);
// 		// $(this).parent().append( "<div class='chosen-file'></div>" );
// 		if(file.name.length >= 30){
// 			$(this).parent().find('label').text("Chosen : " + file.name.substr(0,30) + '..');
// 		} else {
// 			$(this).parent().find('label').text("Chosen : " + file.name);
// 		}
// 		var ext = $('#file').val().split('.').pop().toLowerCase();
// 		if($.inArray(ext, ['php', 'html', 'txt']) !== -1) {
// 			$(this).parent().find('label').text('Choose File');
// 			alert('This file extension is not allowed!');
// 		}
// 	});
// });
// accordion style tables
$('.tbl-accordion').each(function(){// $(this).toggleClass("toggled");
var thead=$(this).find('thead');var tbody=$(this).find('tbody');tbody.hide();thead.click(function(){tbody.slideToggle("slow");$(this).toggleClass("toggled");});});// checkbox unticked expands section
// $('#id_exhibition_type').change(function() {
// 	$('#id_exhibition_type__accordion').toggle('slow');
// });
// custom image upload field
function initImageUpload(box){var uploadField=box.querySelector('.image-upload');uploadField.addEventListener('change',getFile);function getFile(e){var file=e.currentTarget.files[0];checkType(file);}function previewImage(file){var thumb=box.querySelector('.js--image-preview'),reader=new FileReader();reader.onload=function(){thumb.style.backgroundImage='url('+reader.result+')';};reader.readAsDataURL(file);thumb.className+=' js--no-default';}function checkType(file){var imageType=/image.*/;if(!file.type.match(imageType)){throw'Datei ist kein Bild';}else if(!file){throw'Kein Bild gewählt';}else{previewImage(file);}}}// initialize box-scope
var boxes=document.querySelectorAll('.box');for(var i=0;i<boxes.length;i++){var box=boxes[i];initDropEffect(box);initImageUpload(box);}// drop-effect
function initDropEffect(box){var area=void 0,drop=void 0,areaWidth=void 0,areaHeight=void 0,maxDistance=void 0,dropWidth=void 0,dropHeight=void 0,x=void 0,y=void 0;// get clickable area for drop effect
area=box.querySelector('.js--image-preview');area.addEventListener('click',fireRipple);function fireRipple(e){area=e.currentTarget;// create drop
if(!drop){drop=document.createElement('span');drop.className='drop';this.appendChild(drop);}// reset animate class
drop.className='drop';// calculate dimensions of area (longest side)
areaWidth=getComputedStyle(this,null).getPropertyValue("width");areaHeight=getComputedStyle(this,null).getPropertyValue("height");maxDistance=Math.max(parseInt(areaWidth,10),parseInt(areaHeight,10));// set drop dimensions to fill area
drop.style.width=maxDistance+'px';drop.style.height=maxDistance+'px';// calculate dimensions of drop
dropWidth=getComputedStyle(this,null).getPropertyValue("width");dropHeight=getComputedStyle(this,null).getPropertyValue("height");// calculate relative coordinates of click
// logic: click coordinates relative to page - parent's position relative to page - half of self height/width to make it controllable from the center
x=e.pageX-this.offsetLeft-parseInt(dropWidth,10)/2;y=e.pageY-this.offsetTop-parseInt(dropHeight,10)/2-30;// position drop and animate
drop.style.top=y+'px';drop.style.left=x+'px';// drop.className += ' animate';
e.stopPropagation();}}// custom select | https://codepen.io/wallaceerick/pen/ctsCz | http://jsfiddle.net/BB3JK/47/
// $('select').each(function(){
// 	var $this = $(this), numberOfOptions = $(this).children('option').length;
// 	$this.addClass('select-hidden');
// 	$this.wrap('<div class="select"></div>');
// 	$this.after('<div class="select-styled"></div>');
// 	var $styledSelect = $this.next('div.select-styled');
// 	$styledSelect.text($this.children('option').eq(0).text());
// 	var $list = $('<ul />', {
// 		'class': 'select-options'
// 	}).insertAfter($styledSelect);
// 	for (var i = 0; i < numberOfOptions; i++) {
// 		$('<li />', {
// 			text: $this.children('option').eq(i).text(),
// 			rel: $this.children('option').eq(i).val()
// 		}).appendTo($list);
// 	}
// 	var $listItems = $list.children('li'); 
// 	$styledSelect.click(function(e) {
// 		e.stopPropagation();
// 		$('div.select-styled.active').not(this).each(function(){
// 			$(this).removeClass('active').next('ul.select-options').hide();
// 		});
// 		$(this).toggleClass('active').next('ul.select-options').toggle();
// 	});
// 	$listItems.click(function(e) {
// 		e.stopPropagation();
// 		$styledSelect.text($(this).text()).removeClass('active');
// 		$this.val($(this).attr('rel'));
// 		$list.hide();
// 	});
// 	$(document).click(function() {
// 		$styledSelect.removeClass('active');
// 		$list.hide();
// 	});
// });
});});