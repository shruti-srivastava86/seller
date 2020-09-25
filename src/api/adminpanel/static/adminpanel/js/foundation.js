(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationCore=mod.exports;}})(this,function(){'use strict';var _typeof=typeof Symbol==="function"&&typeof Symbol.iterator==="symbol"?function(obj){return typeof obj;}:function(obj){return obj&&typeof Symbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeof obj;};!function($){"use strict";var FOUNDATION_VERSION='6.3.1';// Global Foundation object
// This is attached to the window, or used as a module for AMD/Browserify
var Foundation={version:FOUNDATION_VERSION,/**
   * Stores initialized plugins.
   */_plugins:{},/**
   * Stores generated unique ids for plugin instances
   */_uuids:[],/**
   * Returns a boolean for RTL support
   */rtl:function rtl(){return $('html').attr('dir')==='rtl';},/**
   * Defines a Foundation plugin, adding it to the `Foundation` namespace and the list of plugins to initialize when reflowing.
   * @param {Object} plugin - The constructor of the plugin.
   */plugin:function plugin(_plugin,name){// Object key to use when adding to global Foundation object
// Examples: Foundation.Reveal, Foundation.OffCanvas
var className=name||functionName(_plugin);// Object key to use when storing the plugin, also used to create the identifying data attribute for the plugin
// Examples: data-reveal, data-off-canvas
var attrName=hyphenate(className);// Add to the Foundation object and the plugins list (for reflowing)
this._plugins[attrName]=this[className]=_plugin;},/**
   * @function
   * Populates the _uuids array with pointers to each individual plugin instance.
   * Adds the `zfPlugin` data-attribute to programmatically created plugins to allow use of $(selector).foundation(method) calls.
   * Also fires the initialization event for each plugin, consolidating repetitive code.
   * @param {Object} plugin - an instance of a plugin, usually `this` in context.
   * @param {String} name - the name of the plugin, passed as a camelCased string.
   * @fires Plugin#init
   */registerPlugin:function registerPlugin(plugin,name){var pluginName=name?hyphenate(name):functionName(plugin.constructor).toLowerCase();plugin.uuid=this.GetYoDigits(6,pluginName);if(!plugin.$element.attr('data-'+pluginName)){plugin.$element.attr('data-'+pluginName,plugin.uuid);}if(!plugin.$element.data('zfPlugin')){plugin.$element.data('zfPlugin',plugin);}/**
           * Fires when the plugin has initialized.
           * @event Plugin#init
           */plugin.$element.trigger('init.zf.'+pluginName);this._uuids.push(plugin.uuid);return;},/**
   * @function
   * Removes the plugins uuid from the _uuids array.
   * Removes the zfPlugin data attribute, as well as the data-plugin-name attribute.
   * Also fires the destroyed event for the plugin, consolidating repetitive code.
   * @param {Object} plugin - an instance of a plugin, usually `this` in context.
   * @fires Plugin#destroyed
   */unregisterPlugin:function unregisterPlugin(plugin){var pluginName=hyphenate(functionName(plugin.$element.data('zfPlugin').constructor));this._uuids.splice(this._uuids.indexOf(plugin.uuid),1);plugin.$element.removeAttr('data-'+pluginName).removeData('zfPlugin')/**
           * Fires when the plugin has been destroyed.
           * @event Plugin#destroyed
           */.trigger('destroyed.zf.'+pluginName);for(var prop in plugin){plugin[prop]=null;//clean up script to prep for garbage collection.
}return;},/**
   * @function
   * Causes one or more active plugins to re-initialize, resetting event listeners, recalculating positions, etc.
   * @param {String} plugins - optional string of an individual plugin key, attained by calling `$(element).data('pluginName')`, or string of a plugin class i.e. `'dropdown'`
   * @default If no argument is passed, reflow all currently active plugins.
   */reInit:function reInit(plugins){var isJQ=plugins instanceof $;try{if(isJQ){plugins.each(function(){$(this).data('zfPlugin')._init();});}else{var type=typeof plugins==='undefined'?'undefined':_typeof(plugins),_this=this,fns={'object':function object(plgs){plgs.forEach(function(p){p=hyphenate(p);$('[data-'+p+']').foundation('_init');});},'string':function string(){plugins=hyphenate(plugins);$('[data-'+plugins+']').foundation('_init');},'undefined':function undefined(){this['object'](Object.keys(_this._plugins));}};fns[type](plugins);}}catch(err){console.error(err);}finally{return plugins;}},/**
   * returns a random base-36 uid with namespacing
   * @function
   * @param {Number} length - number of random base-36 digits desired. Increase for more random strings.
   * @param {String} namespace - name of plugin to be incorporated in uid, optional.
   * @default {String} '' - if no plugin name is provided, nothing is appended to the uid.
   * @returns {String} - unique id
   */GetYoDigits:function GetYoDigits(length,namespace){length=length||6;return Math.round(Math.pow(36,length+1)-Math.random()*Math.pow(36,length)).toString(36).slice(1)+(namespace?'-'+namespace:'');},/**
   * Initialize plugins on any elements within `elem` (and `elem` itself) that aren't already initialized.
   * @param {Object} elem - jQuery object containing the element to check inside. Also checks the element itself, unless it's the `document` object.
   * @param {String|Array} plugins - A list of plugins to initialize. Leave this out to initialize everything.
   */reflow:function reflow(elem,plugins){// If plugins is undefined, just grab everything
if(typeof plugins==='undefined'){plugins=Object.keys(this._plugins);}// If plugins is a string, convert it to an array with one item
else if(typeof plugins==='string'){plugins=[plugins];}var _this=this;// Iterate through each plugin
$.each(plugins,function(i,name){// Get the current plugin
var plugin=_this._plugins[name];// Localize the search to all elements inside elem, as well as elem itself, unless elem === document
var $elem=$(elem).find('[data-'+name+']').addBack('[data-'+name+']');// For each plugin found, initialize it
$elem.each(function(){var $el=$(this),opts={};// Don't double-dip on plugins
if($el.data('zfPlugin')){console.warn("Tried to initialize "+name+" on an element that already has a Foundation plugin.");return;}if($el.attr('data-options')){var thing=$el.attr('data-options').split(';').forEach(function(e,i){var opt=e.split(':').map(function(el){return el.trim();});if(opt[0])opts[opt[0]]=parseValue(opt[1]);});}try{$el.data('zfPlugin',new plugin($(this),opts));}catch(er){console.error(er);}finally{return;}});});},getFnName:functionName,transitionend:function transitionend($elem){var transitions={'transition':'transitionend','WebkitTransition':'webkitTransitionEnd','MozTransition':'transitionend','OTransition':'otransitionend'};var elem=document.createElement('div'),end;for(var t in transitions){if(typeof elem.style[t]!=='undefined'){end=transitions[t];}}if(end){return end;}else{end=setTimeout(function(){$elem.triggerHandler('transitionend',[$elem]);},1);return'transitionend';}}};Foundation.util={/**
   * Function for applying a debounce effect to a function call.
   * @function
   * @param {Function} func - Function to be called at end of timeout.
   * @param {Number} delay - Time in ms to delay the call of `func`.
   * @returns function
   */throttle:function throttle(func,delay){var timer=null;return function(){var context=this,args=arguments;if(timer===null){timer=setTimeout(function(){func.apply(context,args);timer=null;},delay);}};}};// TODO: consider not making this a jQuery function
// TODO: need way to reflow vs. re-initialize
/**
 * The Foundation jQuery method.
 * @param {String|Array} method - An action to perform on the current jQuery object.
 */var foundation=function foundation(method){var type=typeof method==='undefined'?'undefined':_typeof(method),$meta=$('meta.foundation-mq'),$noJS=$('.no-js');if(!$meta.length){$('<meta class="foundation-mq">').appendTo(document.head);}if($noJS.length){$noJS.removeClass('no-js');}if(type==='undefined'){//needs to initialize the Foundation object, or an individual plugin.
Foundation.MediaQuery._init();Foundation.reflow(this);}else if(type==='string'){//an individual method to invoke on a plugin or group of plugins
var args=Array.prototype.slice.call(arguments,1);//collect all the arguments, if necessary
var plugClass=this.data('zfPlugin');//determine the class of plugin
if(plugClass!==undefined&&plugClass[method]!==undefined){//make sure both the class and method exist
if(this.length===1){//if there's only one, call it directly.
plugClass[method].apply(plugClass,args);}else{this.each(function(i,el){//otherwise loop through the jQuery collection and invoke the method on each
plugClass[method].apply($(el).data('zfPlugin'),args);});}}else{//error for no class or no method
throw new ReferenceError("We're sorry, '"+method+"' is not an available method for "+(plugClass?functionName(plugClass):'this element')+'.');}}else{//error for invalid argument type
throw new TypeError('We\'re sorry, '+type+' is not a valid parameter. You must use a string representing the method you wish to invoke.');}return this;};window.Foundation=Foundation;$.fn.foundation=foundation;// Polyfill for requestAnimationFrame
(function(){if(!Date.now||!window.Date.now)window.Date.now=Date.now=function(){return new Date().getTime();};var vendors=['webkit','moz'];for(var i=0;i<vendors.length&&!window.requestAnimationFrame;++i){var vp=vendors[i];window.requestAnimationFrame=window[vp+'RequestAnimationFrame'];window.cancelAnimationFrame=window[vp+'CancelAnimationFrame']||window[vp+'CancelRequestAnimationFrame'];}if(/iP(ad|hone|od).*OS 6/.test(window.navigator.userAgent)||!window.requestAnimationFrame||!window.cancelAnimationFrame){var lastTime=0;window.requestAnimationFrame=function(callback){var now=Date.now();var nextTime=Math.max(lastTime+16,now);return setTimeout(function(){callback(lastTime=nextTime);},nextTime-now);};window.cancelAnimationFrame=clearTimeout;}/**
   * Polyfill for performance.now, required by rAF
   */if(!window.performance||!window.performance.now){window.performance={start:Date.now(),now:function now(){return Date.now()-this.start;}};}})();if(!Function.prototype.bind){Function.prototype.bind=function(oThis){if(typeof this!=='function'){// closest thing possible to the ECMAScript 5
// internal IsCallable function
throw new TypeError('Function.prototype.bind - what is trying to be bound is not callable');}var aArgs=Array.prototype.slice.call(arguments,1),fToBind=this,fNOP=function fNOP(){},fBound=function fBound(){return fToBind.apply(this instanceof fNOP?this:oThis,aArgs.concat(Array.prototype.slice.call(arguments)));};if(this.prototype){// native functions don't have a prototype
fNOP.prototype=this.prototype;}fBound.prototype=new fNOP();return fBound;};}// Polyfill to get the name of a function in IE9
function functionName(fn){if(Function.prototype.name===undefined){var funcNameRegex=/function\s([^(]{1,})\(/;var results=funcNameRegex.exec(fn.toString());return results&&results.length>1?results[1].trim():"";}else if(fn.prototype===undefined){return fn.constructor.name;}else{return fn.prototype.constructor.name;}}function parseValue(str){if('true'===str)return true;else if('false'===str)return false;else if(!isNaN(str*1))return parseFloat(str);return str;}// Convert PascalCase to kebab-case
// Thank you: http://stackoverflow.com/a/8955580
function hyphenate(str){return str.replace(/([a-z])([A-Z])/g,'$1-$2').toLowerCase();}}(jQuery);});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationUtilBox=mod.exports;}})(this,function(){'use strict';!function($){Foundation.Box={ImNotTouchingYou:ImNotTouchingYou,GetDimensions:GetDimensions,GetOffsets:GetOffsets/**
 * Compares the dimensions of an element to a container and determines collision events with container.
 * @function
 * @param {jQuery} element - jQuery object to test for collisions.
 * @param {jQuery} parent - jQuery object to use as bounding container.
 * @param {Boolean} lrOnly - set to true to check left and right values only.
 * @param {Boolean} tbOnly - set to true to check top and bottom values only.
 * @default if no parent object passed, detects collisions with `window`.
 * @returns {Boolean} - true if collision free, false if a collision in any direction.
 */};function ImNotTouchingYou(element,parent,lrOnly,tbOnly){var eleDims=GetDimensions(element),top,bottom,left,right;if(parent){var parDims=GetDimensions(parent);bottom=eleDims.offset.top+eleDims.height<=parDims.height+parDims.offset.top;top=eleDims.offset.top>=parDims.offset.top;left=eleDims.offset.left>=parDims.offset.left;right=eleDims.offset.left+eleDims.width<=parDims.width+parDims.offset.left;}else{bottom=eleDims.offset.top+eleDims.height<=eleDims.windowDims.height+eleDims.windowDims.offset.top;top=eleDims.offset.top>=eleDims.windowDims.offset.top;left=eleDims.offset.left>=eleDims.windowDims.offset.left;right=eleDims.offset.left+eleDims.width<=eleDims.windowDims.width;}var allDirs=[bottom,top,left,right];if(lrOnly){return left===right===true;}if(tbOnly){return top===bottom===true;}return allDirs.indexOf(false)===-1;};/**
 * Uses native methods to return an object of dimension values.
 * @function
 * @param {jQuery || HTML} element - jQuery object or DOM element for which to get the dimensions. Can be any element other that document or window.
 * @returns {Object} - nested object of integer pixel values
 * TODO - if element is window, return only those values.
 */function GetDimensions(elem,test){elem=elem.length?elem[0]:elem;if(elem===window||elem===document){throw new Error("I'm sorry, Dave. I'm afraid I can't do that.");}var rect=elem.getBoundingClientRect(),parRect=elem.parentNode.getBoundingClientRect(),winRect=document.body.getBoundingClientRect(),winY=window.pageYOffset,winX=window.pageXOffset;return{width:rect.width,height:rect.height,offset:{top:rect.top+winY,left:rect.left+winX},parentDims:{width:parRect.width,height:parRect.height,offset:{top:parRect.top+winY,left:parRect.left+winX}},windowDims:{width:winRect.width,height:winRect.height,offset:{top:winY,left:winX}}};}/**
 * Returns an object of top and left integer pixel values for dynamically rendered elements,
 * such as: Tooltip, Reveal, and Dropdown
 * @function
 * @param {jQuery} element - jQuery object for the element being positioned.
 * @param {jQuery} anchor - jQuery object for the element's anchor point.
 * @param {String} position - a string relating to the desired position of the element, relative to it's anchor
 * @param {Number} vOffset - integer pixel value of desired vertical separation between anchor and element.
 * @param {Number} hOffset - integer pixel value of desired horizontal separation between anchor and element.
 * @param {Boolean} isOverflow - if a collision event is detected, sets to true to default the element to full width - any desired offset.
 * TODO alter/rewrite to work with `em` values as well/instead of pixels
 */function GetOffsets(element,anchor,position,vOffset,hOffset,isOverflow){var $eleDims=GetDimensions(element),$anchorDims=anchor?GetDimensions(anchor):null;switch(position){case'top':return{left:Foundation.rtl()?$anchorDims.offset.left-$eleDims.width+$anchorDims.width:$anchorDims.offset.left,top:$anchorDims.offset.top-($eleDims.height+vOffset)};break;case'left':return{left:$anchorDims.offset.left-($eleDims.width+hOffset),top:$anchorDims.offset.top};break;case'right':return{left:$anchorDims.offset.left+$anchorDims.width+hOffset,top:$anchorDims.offset.top};break;case'center top':return{left:$anchorDims.offset.left+$anchorDims.width/2-$eleDims.width/2,top:$anchorDims.offset.top-($eleDims.height+vOffset)};break;case'center bottom':return{left:isOverflow?hOffset:$anchorDims.offset.left+$anchorDims.width/2-$eleDims.width/2,top:$anchorDims.offset.top+$anchorDims.height+vOffset};break;case'center left':return{left:$anchorDims.offset.left-($eleDims.width+hOffset),top:$anchorDims.offset.top+$anchorDims.height/2-$eleDims.height/2};break;case'center right':return{left:$anchorDims.offset.left+$anchorDims.width+hOffset+1,top:$anchorDims.offset.top+$anchorDims.height/2-$eleDims.height/2};break;case'center':return{left:$eleDims.windowDims.offset.left+$eleDims.windowDims.width/2-$eleDims.width/2,top:$eleDims.windowDims.offset.top+$eleDims.windowDims.height/2-$eleDims.height/2};break;case'reveal':return{left:($eleDims.windowDims.width-$eleDims.width)/2,top:$eleDims.windowDims.offset.top+vOffset};case'reveal full':return{left:$eleDims.windowDims.offset.left,top:$eleDims.windowDims.offset.top};break;case'left bottom':return{left:$anchorDims.offset.left,top:$anchorDims.offset.top+$anchorDims.height+vOffset};break;case'right bottom':return{left:$anchorDims.offset.left+$anchorDims.width+hOffset-$eleDims.width,top:$anchorDims.offset.top+$anchorDims.height+vOffset};break;default:return{left:Foundation.rtl()?$anchorDims.offset.left-$eleDims.width+$anchorDims.width:$anchorDims.offset.left+hOffset,top:$anchorDims.offset.top+$anchorDims.height+vOffset};}}}(jQuery);});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationUtilKeyboard=mod.exports;}})(this,function(){/*******************************************
 *                                         *
 * This util was created by Marius Olbertz *
 * Please thank Marius on GitHub /owlbertz *
 * or the web http://www.mariusolbertz.de/ *
 *                                         *
 ******************************************/'use strict';!function($){var keyCodes={9:'TAB',13:'ENTER',27:'ESCAPE',32:'SPACE',37:'ARROW_LEFT',38:'ARROW_UP',39:'ARROW_RIGHT',40:'ARROW_DOWN'};var commands={};var Keyboard={keys:getKeyCodes(keyCodes),parseKey:function parseKey(event){var key=keyCodes[event.which||event.keyCode]||String.fromCharCode(event.which).toUpperCase();// Remove un-printable characters, e.g. for `fromCharCode` calls for CTRL only events
key=key.replace(/\W+/,'');if(event.shiftKey)key='SHIFT_'+key;if(event.ctrlKey)key='CTRL_'+key;if(event.altKey)key='ALT_'+key;// Remove trailing underscore, in case only modifiers were used (e.g. only `CTRL_ALT`)
key=key.replace(/_$/,'');return key;},handleKey:function handleKey(event,component,functions){var commandList=commands[component],keyCode=this.parseKey(event),cmds,command,fn;if(!commandList)return console.warn('Component not defined!');if(typeof commandList.ltr==='undefined'){// this component does not differentiate between ltr and rtl
cmds=commandList;// use plain list
}else{// merge ltr and rtl: if document is rtl, rtl overwrites ltr and vice versa
if(Foundation.rtl())cmds=$.extend({},commandList.ltr,commandList.rtl);else cmds=$.extend({},commandList.rtl,commandList.ltr);}command=cmds[keyCode];fn=functions[command];if(fn&&typeof fn==='function'){// execute function  if exists
var returnValue=fn.apply();if(functions.handled||typeof functions.handled==='function'){// execute function when event was handled
functions.handled(returnValue);}}else{if(functions.unhandled||typeof functions.unhandled==='function'){// execute function when event was not handled
functions.unhandled();}}},findFocusable:function findFocusable($element){if(!$element){return false;}return $element.find('a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, *[tabindex], *[contenteditable]').filter(function(){if(!$(this).is(':visible')||$(this).attr('tabindex')<0){return false;}//only have visible elements and those that have a tabindex greater or equal 0
return true;});},register:function register(componentName,cmds){commands[componentName]=cmds;},trapFocus:function trapFocus($element){var $focusable=Foundation.Keyboard.findFocusable($element),$firstFocusable=$focusable.eq(0),$lastFocusable=$focusable.eq(-1);$element.on('keydown.zf.trapfocus',function(event){if(event.target===$lastFocusable[0]&&Foundation.Keyboard.parseKey(event)==='TAB'){event.preventDefault();$firstFocusable.focus();}else if(event.target===$firstFocusable[0]&&Foundation.Keyboard.parseKey(event)==='SHIFT_TAB'){event.preventDefault();$lastFocusable.focus();}});},releaseFocus:function releaseFocus($element){$element.off('keydown.zf.trapfocus');}};/*
 * Constants for easier comparing.
 * Can be used like Foundation.parseKey(event) === Foundation.keys.SPACE
 */function getKeyCodes(kcs){var k={};for(var kc in kcs){k[kcs[kc]]=kcs[kc];}return k;}Foundation.Keyboard=Keyboard;}(jQuery);});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationUtilMediaQuery=mod.exports;}})(this,function(){'use strict';var _typeof=typeof Symbol==="function"&&typeof Symbol.iterator==="symbol"?function(obj){return typeof obj;}:function(obj){return obj&&typeof Symbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeof obj;};!function($){// Default set of media queries
var defaultQueries={'default':'only screen',landscape:'only screen and (orientation: landscape)',portrait:'only screen and (orientation: portrait)',retina:'only screen and (-webkit-min-device-pixel-ratio: 2),'+'only screen and (min--moz-device-pixel-ratio: 2),'+'only screen and (-o-min-device-pixel-ratio: 2/1),'+'only screen and (min-device-pixel-ratio: 2),'+'only screen and (min-resolution: 192dpi),'+'only screen and (min-resolution: 2dppx)'};var MediaQuery={queries:[],current:'',_init:function _init(){var self=this;var extractedStyles=$('.foundation-mq').css('font-family');var namedQueries;namedQueries=parseStyleToObject(extractedStyles);for(var key in namedQueries){if(namedQueries.hasOwnProperty(key)){self.queries.push({name:key,value:'only screen and (min-width: '+namedQueries[key]+')'});}}this.current=this._getCurrentSize();this._watcher();},atLeast:function atLeast(size){var query=this.get(size);if(query){return window.matchMedia(query).matches;}return false;},is:function is(size){size=size.trim().split(' ');if(size.length>1&&size[1]==='only'){if(size[0]===this._getCurrentSize())return true;}else{return this.atLeast(size[0]);}return false;},get:function get(size){for(var i in this.queries){if(this.queries.hasOwnProperty(i)){var query=this.queries[i];if(size===query.name)return query.value;}}return null;},_getCurrentSize:function _getCurrentSize(){var matched;for(var i=0;i<this.queries.length;i++){var query=this.queries[i];if(window.matchMedia(query.value).matches){matched=query;}}if((typeof matched==='undefined'?'undefined':_typeof(matched))==='object'){return matched.name;}else{return matched;}},_watcher:function _watcher(){var _this=this;$(window).on('resize.zf.mediaquery',function(){var newSize=_this._getCurrentSize(),currentSize=_this.current;if(newSize!==currentSize){// Change the current media query
_this.current=newSize;// Broadcast the media query change on the window
$(window).trigger('changed.zf.mediaquery',[newSize,currentSize]);}});}};Foundation.MediaQuery=MediaQuery;// matchMedia() polyfill - Test a CSS media type/query in JS.
// Authors & copyright (c) 2012: Dual MIT/BSD license
window.matchMedia||(window.matchMedia=function(){'use strict';// For browsers that support matchMedium api such as IE 9 and webkit
var styleMedia=window.styleMedia||window.media;// For those that don't support matchMedium
if(!styleMedia){var style=document.createElement('style'),script=document.getElementsByTagName('script')[0],info=null;style.type='text/css';style.id='matchmediajs-test';script&&script.parentNode&&script.parentNode.insertBefore(style,script);// 'style.currentStyle' is used by IE <= 8 and 'window.getComputedStyle' for all other browsers
info='getComputedStyle'in window&&window.getComputedStyle(style,null)||style.currentStyle;styleMedia={matchMedium:function matchMedium(media){var text='@media '+media+'{ #matchmediajs-test { width: 1px; } }';// 'style.styleSheet' is used by IE <= 8 and 'style.textContent' for all other browsers
if(style.styleSheet){style.styleSheet.cssText=text;}else{style.textContent=text;}// Test if media query is true or false
return info.width==='1px';}};}return function(media){return{matches:styleMedia.matchMedium(media||'all'),media:media||'all'};};}());// Thank you: https://github.com/sindresorhus/query-string
function parseStyleToObject(str){var styleObject={};if(typeof str!=='string'){return styleObject;}str=str.trim().slice(1,-1);// browsers re-quote string style values
if(!str){return styleObject;}styleObject=str.split('&').reduce(function(ret,param){var parts=param.replace(/\+/g,' ').split('=');var key=parts[0];var val=parts[1];key=decodeURIComponent(key);// missing `=` should be `null`:
// http://w3.org/TR/2012/WD-url-20120524/#collect-url-parameters
val=val===undefined?null:decodeURIComponent(val);if(!ret.hasOwnProperty(key)){ret[key]=val;}else if(Array.isArray(ret[key])){ret[key].push(val);}else{ret[key]=[ret[key],val];}return ret;},{});return styleObject;}Foundation.MediaQuery=MediaQuery;}(jQuery);});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationUtilMotion=mod.exports;}})(this,function(){'use strict';!function($){/**
 * Motion module.
 * @module foundation.motion
 */var initClasses=['mui-enter','mui-leave'];var activeClasses=['mui-enter-active','mui-leave-active'];var Motion={animateIn:function animateIn(element,animation,cb){animate(true,element,animation,cb);},animateOut:function animateOut(element,animation,cb){animate(false,element,animation,cb);}};function Move(duration,elem,fn){var anim,prog,start=null;// console.log('called');
if(duration===0){fn.apply(elem);elem.trigger('finished.zf.animate',[elem]).triggerHandler('finished.zf.animate',[elem]);return;}function move(ts){if(!start)start=ts;// console.log(start, ts);
prog=ts-start;fn.apply(elem);if(prog<duration){anim=window.requestAnimationFrame(move,elem);}else{window.cancelAnimationFrame(anim);elem.trigger('finished.zf.animate',[elem]).triggerHandler('finished.zf.animate',[elem]);}}anim=window.requestAnimationFrame(move);}/**
 * Animates an element in or out using a CSS transition class.
 * @function
 * @private
 * @param {Boolean} isIn - Defines if the animation is in or out.
 * @param {Object} element - jQuery or HTML object to animate.
 * @param {String} animation - CSS class to use.
 * @param {Function} cb - Callback to run when animation is finished.
 */function animate(isIn,element,animation,cb){element=$(element).eq(0);if(!element.length)return;var initClass=isIn?initClasses[0]:initClasses[1];var activeClass=isIn?activeClasses[0]:activeClasses[1];// Set up the animation
reset();element.addClass(animation).css('transition','none');requestAnimationFrame(function(){element.addClass(initClass);if(isIn)element.show();});// Start the animation
requestAnimationFrame(function(){element[0].offsetWidth;element.css('transition','').addClass(activeClass);});// Clean up the animation when it finishes
element.one(Foundation.transitionend(element),finish);// Hides the element (for out animations), resets the element, and runs a callback
function finish(){if(!isIn)element.hide();reset();if(cb)cb.apply(element);}// Resets transitions and removes motion-specific classes
function reset(){element[0].style.transitionDuration=0;element.removeClass(initClass+' '+activeClass+' '+animation);}}Foundation.Move=Move;Foundation.Motion=Motion;}(jQuery);});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationUtilNest=mod.exports;}})(this,function(){'use strict';!function($){var Nest={Feather:function Feather(menu){var type=arguments.length>1&&arguments[1]!==undefined?arguments[1]:'zf';menu.attr('role','menubar');var items=menu.find('li').attr({'role':'menuitem'}),subMenuClass='is-'+type+'-submenu',subItemClass=subMenuClass+'-item',hasSubClass='is-'+type+'-submenu-parent';items.each(function(){var $item=$(this),$sub=$item.children('ul');if($sub.length){$item.addClass(hasSubClass).attr({'aria-haspopup':true,'aria-label':$item.children('a:first').text()});// Note:  Drilldowns behave differently in how they hide, and so need
// additional attributes.  We should look if this possibly over-generalized
// utility (Nest) is appropriate when we rework menus in 6.4
if(type==='drilldown'){$item.attr({'aria-expanded':false});}$sub.addClass('submenu '+subMenuClass).attr({'data-submenu':'','role':'menu'});if(type==='drilldown'){$sub.attr({'aria-hidden':true});}}if($item.parent('[data-submenu]').length){$item.addClass('is-submenu-item '+subItemClass);}});return;},Burn:function Burn(menu,type){var//items = menu.find('li'),
subMenuClass='is-'+type+'-submenu',subItemClass=subMenuClass+'-item',hasSubClass='is-'+type+'-submenu-parent';menu.find('>li, .menu, .menu > li').removeClass(subMenuClass+' '+subItemClass+' '+hasSubClass+' is-submenu-item submenu is-active').removeAttr('data-submenu').css('display','');// console.log(      menu.find('.' + subMenuClass + ', .' + subItemClass + ', .has-submenu, .is-submenu-item, .submenu, [data-submenu]')
//           .removeClass(subMenuClass + ' ' + subItemClass + ' has-submenu is-submenu-item submenu')
//           .removeAttr('data-submenu'));
// items.each(function(){
//   var $item = $(this),
//       $sub = $item.children('ul');
//   if($item.parent('[data-submenu]').length){
//     $item.removeClass('is-submenu-item ' + subItemClass);
//   }
//   if($sub.length){
//     $item.removeClass('has-submenu');
//     $sub.removeClass('submenu ' + subMenuClass).removeAttr('data-submenu');
//   }
// });
}};Foundation.Nest=Nest;}(jQuery);});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationUtilTimerAndImageLoader=mod.exports;}})(this,function(){'use strict';!function($){function Timer(elem,options,cb){var _this=this,duration=options.duration,//options is an object for easily adding features later.
nameSpace=Object.keys(elem.data())[0]||'timer',remain=-1,start,timer;this.isPaused=false;this.restart=function(){remain=-1;clearTimeout(timer);this.start();};this.start=function(){this.isPaused=false;// if(!elem.data('paused')){ return false; }//maybe implement this sanity check if used for other things.
clearTimeout(timer);remain=remain<=0?duration:remain;elem.data('paused',false);start=Date.now();timer=setTimeout(function(){if(options.infinite){_this.restart();//rerun the timer.
}if(cb&&typeof cb==='function'){cb();}},remain);elem.trigger('timerstart.zf.'+nameSpace);};this.pause=function(){this.isPaused=true;//if(elem.data('paused')){ return false; }//maybe implement this sanity check if used for other things.
clearTimeout(timer);elem.data('paused',true);var end=Date.now();remain=remain-(end-start);elem.trigger('timerpaused.zf.'+nameSpace);};}/**
 * Runs a callback function when images are fully loaded.
 * @param {Object} images - Image(s) to check if loaded.
 * @param {Func} callback - Function to execute when image is fully loaded.
 */function onImagesLoaded(images,callback){var self=this,unloaded=images.length;if(unloaded===0){callback();}images.each(function(){// Check if image is loaded
if(this.complete||this.readyState===4||this.readyState==='complete'){singleImageLoaded();}// Force load the image
else{// fix for IE. See https://css-tricks.com/snippets/jquery/fixing-load-in-ie-for-cached-images/
var src=$(this).attr('src');$(this).attr('src',src+(src.indexOf('?')>=0?'&':'?')+new Date().getTime());$(this).one('load',function(){singleImageLoaded();});}});function singleImageLoaded(){unloaded--;if(unloaded===0){callback();}}}Foundation.Timer=Timer;Foundation.onImagesLoaded=onImagesLoaded;}(jQuery);});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationUtilTouch=mod.exports;}})(this,function(){'use strict';//**************************************************
//**Work inspired by multiple jquery swipe plugins**
//**Done by Yohai Ararat ***************************
//**************************************************
(function($){$.spotSwipe={version:'1.0.0',enabled:'ontouchstart'in document.documentElement,preventDefault:false,moveThreshold:75,timeThreshold:200};var startPosX,startPosY,startTime,elapsedTime,isMoving=false;function onTouchEnd(){//  alert(this);
this.removeEventListener('touchmove',onTouchMove);this.removeEventListener('touchend',onTouchEnd);isMoving=false;}function onTouchMove(e){if($.spotSwipe.preventDefault){e.preventDefault();}if(isMoving){var x=e.touches[0].pageX;var y=e.touches[0].pageY;var dx=startPosX-x;var dy=startPosY-y;var dir;elapsedTime=new Date().getTime()-startTime;if(Math.abs(dx)>=$.spotSwipe.moveThreshold&&elapsedTime<=$.spotSwipe.timeThreshold){dir=dx>0?'left':'right';}// else if(Math.abs(dy) >= $.spotSwipe.moveThreshold && elapsedTime <= $.spotSwipe.timeThreshold) {
//   dir = dy > 0 ? 'down' : 'up';
// }
if(dir){e.preventDefault();onTouchEnd.call(this);$(this).trigger('swipe',dir).trigger('swipe'+dir);}}}function onTouchStart(e){if(e.touches.length==1){startPosX=e.touches[0].pageX;startPosY=e.touches[0].pageY;isMoving=true;startTime=new Date().getTime();this.addEventListener('touchmove',onTouchMove,false);this.addEventListener('touchend',onTouchEnd,false);}}function init(){this.addEventListener&&this.addEventListener('touchstart',onTouchStart,false);}function teardown(){this.removeEventListener('touchstart',onTouchStart);}$.event.special.swipe={setup:init};$.each(['left','up','down','right'],function(){$.event.special['swipe'+this]={setup:function setup(){$(this).on('swipe',$.noop);}};});})(jQuery);/****************************************************
 * Method for adding psuedo drag events to elements *
 ***************************************************/!function($){$.fn.addTouch=function(){this.each(function(i,el){$(el).bind('touchstart touchmove touchend touchcancel',function(){//we pass the original event object because the jQuery event
//object is normalized to w3c specs and does not provide the TouchList
handleTouch(event);});});var handleTouch=function handleTouch(event){var touches=event.changedTouches,first=touches[0],eventTypes={touchstart:'mousedown',touchmove:'mousemove',touchend:'mouseup'},type=eventTypes[event.type],simulatedEvent;if('MouseEvent'in window&&typeof window.MouseEvent==='function'){simulatedEvent=new window.MouseEvent(type,{'bubbles':true,'cancelable':true,'screenX':first.screenX,'screenY':first.screenY,'clientX':first.clientX,'clientY':first.clientY});}else{simulatedEvent=document.createEvent('MouseEvent');simulatedEvent.initMouseEvent(type,true,true,window,1,first.screenX,first.screenY,first.clientX,first.clientY,false,false,false,false,0/*left*/,null);}first.target.dispatchEvent(simulatedEvent);};};}(jQuery);//**********************************
//**From the jQuery Mobile Library**
//**need to recreate functionality**
//**and try to improve if possible**
//**********************************
/* Removing the jQuery function ****
************************************

(function( $, window, undefined ) {

	var $document = $( document ),
		// supportTouch = $.mobile.support.touch,
		touchStartEvent = 'touchstart'//supportTouch ? "touchstart" : "mousedown",
		touchStopEvent = 'touchend'//supportTouch ? "touchend" : "mouseup",
		touchMoveEvent = 'touchmove'//supportTouch ? "touchmove" : "mousemove";

	// setup new event shortcuts
	$.each( ( "touchstart touchmove touchend " +
		"swipe swipeleft swiperight" ).split( " " ), function( i, name ) {

		$.fn[ name ] = function( fn ) {
			return fn ? this.bind( name, fn ) : this.trigger( name );
		};

		// jQuery < 1.8
		if ( $.attrFn ) {
			$.attrFn[ name ] = true;
		}
	});

	function triggerCustomEvent( obj, eventType, event, bubble ) {
		var originalType = event.type;
		event.type = eventType;
		if ( bubble ) {
			$.event.trigger( event, undefined, obj );
		} else {
			$.event.dispatch.call( obj, event );
		}
		event.type = originalType;
	}

	// also handles taphold

	// Also handles swipeleft, swiperight
	$.event.special.swipe = {

		// More than this horizontal displacement, and we will suppress scrolling.
		scrollSupressionThreshold: 30,

		// More time than this, and it isn't a swipe.
		durationThreshold: 1000,

		// Swipe horizontal displacement must be more than this.
		horizontalDistanceThreshold: window.devicePixelRatio >= 2 ? 15 : 30,

		// Swipe vertical displacement must be less than this.
		verticalDistanceThreshold: window.devicePixelRatio >= 2 ? 15 : 30,

		getLocation: function ( event ) {
			var winPageX = window.pageXOffset,
				winPageY = window.pageYOffset,
				x = event.clientX,
				y = event.clientY;

			if ( event.pageY === 0 && Math.floor( y ) > Math.floor( event.pageY ) ||
				event.pageX === 0 && Math.floor( x ) > Math.floor( event.pageX ) ) {

				// iOS4 clientX/clientY have the value that should have been
				// in pageX/pageY. While pageX/page/ have the value 0
				x = x - winPageX;
				y = y - winPageY;
			} else if ( y < ( event.pageY - winPageY) || x < ( event.pageX - winPageX ) ) {

				// Some Android browsers have totally bogus values for clientX/Y
				// when scrolling/zooming a page. Detectable since clientX/clientY
				// should never be smaller than pageX/pageY minus page scroll
				x = event.pageX - winPageX;
				y = event.pageY - winPageY;
			}

			return {
				x: x,
				y: y
			};
		},

		start: function( event ) {
			var data = event.originalEvent.touches ?
					event.originalEvent.touches[ 0 ] : event,
				location = $.event.special.swipe.getLocation( data );
			return {
						time: ( new Date() ).getTime(),
						coords: [ location.x, location.y ],
						origin: $( event.target )
					};
		},

		stop: function( event ) {
			var data = event.originalEvent.touches ?
					event.originalEvent.touches[ 0 ] : event,
				location = $.event.special.swipe.getLocation( data );
			return {
						time: ( new Date() ).getTime(),
						coords: [ location.x, location.y ]
					};
		},

		handleSwipe: function( start, stop, thisObject, origTarget ) {
			if ( stop.time - start.time < $.event.special.swipe.durationThreshold &&
				Math.abs( start.coords[ 0 ] - stop.coords[ 0 ] ) > $.event.special.swipe.horizontalDistanceThreshold &&
				Math.abs( start.coords[ 1 ] - stop.coords[ 1 ] ) < $.event.special.swipe.verticalDistanceThreshold ) {
				var direction = start.coords[0] > stop.coords[ 0 ] ? "swipeleft" : "swiperight";

				triggerCustomEvent( thisObject, "swipe", $.Event( "swipe", { target: origTarget, swipestart: start, swipestop: stop }), true );
				triggerCustomEvent( thisObject, direction,$.Event( direction, { target: origTarget, swipestart: start, swipestop: stop } ), true );
				return true;
			}
			return false;

		},

		// This serves as a flag to ensure that at most one swipe event event is
		// in work at any given time
		eventInProgress: false,

		setup: function() {
			var events,
				thisObject = this,
				$this = $( thisObject ),
				context = {};

			// Retrieve the events data for this element and add the swipe context
			events = $.data( this, "mobile-events" );
			if ( !events ) {
				events = { length: 0 };
				$.data( this, "mobile-events", events );
			}
			events.length++;
			events.swipe = context;

			context.start = function( event ) {

				// Bail if we're already working on a swipe event
				if ( $.event.special.swipe.eventInProgress ) {
					return;
				}
				$.event.special.swipe.eventInProgress = true;

				var stop,
					start = $.event.special.swipe.start( event ),
					origTarget = event.target,
					emitted = false;

				context.move = function( event ) {
					if ( !start || event.isDefaultPrevented() ) {
						return;
					}

					stop = $.event.special.swipe.stop( event );
					if ( !emitted ) {
						emitted = $.event.special.swipe.handleSwipe( start, stop, thisObject, origTarget );
						if ( emitted ) {

							// Reset the context to make way for the next swipe event
							$.event.special.swipe.eventInProgress = false;
						}
					}
					// prevent scrolling
					if ( Math.abs( start.coords[ 0 ] - stop.coords[ 0 ] ) > $.event.special.swipe.scrollSupressionThreshold ) {
						event.preventDefault();
					}
				};

				context.stop = function() {
						emitted = true;

						// Reset the context to make way for the next swipe event
						$.event.special.swipe.eventInProgress = false;
						$document.off( touchMoveEvent, context.move );
						context.move = null;
				};

				$document.on( touchMoveEvent, context.move )
					.one( touchStopEvent, context.stop );
			};
			$this.on( touchStartEvent, context.start );
		},

		teardown: function() {
			var events, context;

			events = $.data( this, "mobile-events" );
			if ( events ) {
				context = events.swipe;
				delete events.swipe;
				events.length--;
				if ( events.length === 0 ) {
					$.removeData( this, "mobile-events" );
				}
			}

			if ( context ) {
				if ( context.start ) {
					$( this ).off( touchStartEvent, context.start );
				}
				if ( context.move ) {
					$document.off( touchMoveEvent, context.move );
				}
				if ( context.stop ) {
					$document.off( touchStopEvent, context.stop );
				}
			}
		}
	};
	$.each({
		swipeleft: "swipe.left",
		swiperight: "swipe.right"
	}, function( event, sourceEvent ) {

		$.event.special[ event ] = {
			setup: function() {
				$( this ).bind( sourceEvent, $.noop );
			},
			teardown: function() {
				$( this ).unbind( sourceEvent );
			}
		};
	});
})( jQuery, this );
*/});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationUtilTriggers=mod.exports;}})(this,function(){'use strict';var _typeof=typeof Symbol==="function"&&typeof Symbol.iterator==="symbol"?function(obj){return typeof obj;}:function(obj){return obj&&typeof Symbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeof obj;};!function($){var MutationObserver=function(){var prefixes=['WebKit','Moz','O','Ms',''];for(var i=0;i<prefixes.length;i++){if(prefixes[i]+'MutationObserver'in window){return window[prefixes[i]+'MutationObserver'];}}return false;}();var triggers=function triggers(el,type){el.data(type).split(' ').forEach(function(id){$('#'+id)[type==='close'?'trigger':'triggerHandler'](type+'.zf.trigger',[el]);});};// Elements with [data-open] will reveal a plugin that supports it when clicked.
$(document).on('click.zf.trigger','[data-open]',function(){triggers($(this),'open');});// Elements with [data-close] will close a plugin that supports it when clicked.
// If used without a value on [data-close], the event will bubble, allowing it to close a parent component.
$(document).on('click.zf.trigger','[data-close]',function(){var id=$(this).data('close');if(id){triggers($(this),'close');}else{$(this).trigger('close.zf.trigger');}});// Elements with [data-toggle] will toggle a plugin that supports it when clicked.
$(document).on('click.zf.trigger','[data-toggle]',function(){var id=$(this).data('toggle');if(id){triggers($(this),'toggle');}else{$(this).trigger('toggle.zf.trigger');}});// Elements with [data-closable] will respond to close.zf.trigger events.
$(document).on('close.zf.trigger','[data-closable]',function(e){e.stopPropagation();var animation=$(this).data('closable');if(animation!==''){Foundation.Motion.animateOut($(this),animation,function(){$(this).trigger('closed.zf');});}else{$(this).fadeOut().trigger('closed.zf');}});$(document).on('focus.zf.trigger blur.zf.trigger','[data-toggle-focus]',function(){var id=$(this).data('toggle-focus');$('#'+id).triggerHandler('toggle.zf.trigger',[$(this)]);});/**
* Fires once after all other scripts have loaded
* @function
* @private
*/$(window).on('load',function(){checkListeners();});function checkListeners(){eventsListener();resizeListener();scrollListener();closemeListener();}//******** only fires this function once on load, if there's something to watch ********
function closemeListener(pluginName){var yetiBoxes=$('[data-yeti-box]'),plugNames=['dropdown','tooltip','reveal'];if(pluginName){if(typeof pluginName==='string'){plugNames.push(pluginName);}else if((typeof pluginName==='undefined'?'undefined':_typeof(pluginName))==='object'&&typeof pluginName[0]==='string'){plugNames.concat(pluginName);}else{console.error('Plugin names must be strings');}}if(yetiBoxes.length){var listeners=plugNames.map(function(name){return'closeme.zf.'+name;}).join(' ');$(window).off(listeners).on(listeners,function(e,pluginId){var plugin=e.namespace.split('.')[0];var plugins=$('[data-'+plugin+']').not('[data-yeti-box="'+pluginId+'"]');plugins.each(function(){var _this=$(this);_this.triggerHandler('close.zf.trigger',[_this]);});});}}function resizeListener(debounce){var timer=void 0,$nodes=$('[data-resize]');if($nodes.length){$(window).off('resize.zf.trigger').on('resize.zf.trigger',function(e){if(timer){clearTimeout(timer);}timer=setTimeout(function(){if(!MutationObserver){//fallback for IE 9
$nodes.each(function(){$(this).triggerHandler('resizeme.zf.trigger');});}//trigger all listening elements and signal a resize event
$nodes.attr('data-events',"resize");},debounce||10);//default time to emit resize event
});}}function scrollListener(debounce){var timer=void 0,$nodes=$('[data-scroll]');if($nodes.length){$(window).off('scroll.zf.trigger').on('scroll.zf.trigger',function(e){if(timer){clearTimeout(timer);}timer=setTimeout(function(){if(!MutationObserver){//fallback for IE 9
$nodes.each(function(){$(this).triggerHandler('scrollme.zf.trigger');});}//trigger all listening elements and signal a scroll event
$nodes.attr('data-events',"scroll");},debounce||10);//default time to emit scroll event
});}}function eventsListener(){if(!MutationObserver){return false;}var nodes=document.querySelectorAll('[data-resize], [data-scroll], [data-mutate]');//element callback
var listeningElementsMutation=function listeningElementsMutation(mutationRecordsList){var $target=$(mutationRecordsList[0].target);//trigger the event handler for the element depending on type
switch(mutationRecordsList[0].type){case"attributes":if($target.attr("data-events")==="scroll"&&mutationRecordsList[0].attributeName==="data-events"){$target.triggerHandler('scrollme.zf.trigger',[$target,window.pageYOffset]);}if($target.attr("data-events")==="resize"&&mutationRecordsList[0].attributeName==="data-events"){$target.triggerHandler('resizeme.zf.trigger',[$target]);}if(mutationRecordsList[0].attributeName==="style"){$target.closest("[data-mutate]").attr("data-events","mutate");$target.closest("[data-mutate]").triggerHandler('mutateme.zf.trigger',[$target.closest("[data-mutate]")]);}break;case"childList":$target.closest("[data-mutate]").attr("data-events","mutate");$target.closest("[data-mutate]").triggerHandler('mutateme.zf.trigger',[$target.closest("[data-mutate]")]);break;default:return false;//nothing
}};if(nodes.length){//for each element that needs to listen for resizing, scrolling, or mutation add a single observer
for(var i=0;i<=nodes.length-1;i++){var elementObserver=new MutationObserver(listeningElementsMutation);elementObserver.observe(nodes[i],{attributes:true,childList:true,characterData:false,subtree:true,attributeFilter:["data-events","style"]});}}}// ------------------------------------
// [PH]
// Foundation.CheckWatchers = checkWatchers;
Foundation.IHearYou=checkListeners;// Foundation.ISeeYou = scrollListener;
// Foundation.IFeelYou = closemeListener;
}(jQuery);});
(function(global,factory){if(typeof define==="function"&&define.amd){define([],factory);}else if(typeof exports!=="undefined"){factory();}else{var mod={exports:{}};factory();global.foundationOffcanvas=mod.exports;}})(this,function(){'use strict';function _classCallCheck(instance,Constructor){if(!(instance instanceof Constructor)){throw new TypeError("Cannot call a class as a function");}}var _createClass=function(){function defineProperties(target,props){for(var i=0;i<props.length;i++){var descriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"in descriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}return function(Constructor,protoProps,staticProps){if(protoProps)defineProperties(Constructor.prototype,protoProps);if(staticProps)defineProperties(Constructor,staticProps);return Constructor;};}();!function($){var OffCanvas=function(){/**
   * Creates a new instance of an off-canvas wrapper.
   * @class
   * @fires OffCanvas#init
   * @param {Object} element - jQuery object to initialize.
   * @param {Object} options - Overrides to the default plugin settings.
   */function OffCanvas(element,options){_classCallCheck(this,OffCanvas);this.$element=element;this.options=$.extend({},OffCanvas.defaults,this.$element.data(),options);this.$lastTrigger=$();this.$triggers=$();this._init();this._events();Foundation.registerPlugin(this,'OffCanvas');Foundation.Keyboard.register('OffCanvas',{'ESCAPE':'close'});}/**
   * Initializes the off-canvas wrapper by adding the exit overlay (if needed).
   * @function
   * @private
   */_createClass(OffCanvas,[{key:'_init',value:function _init(){var id=this.$element.attr('id');this.$element.attr('aria-hidden','true');this.$element.addClass('is-transition-'+this.options.transition);// Find triggers that affect this element and add aria-expanded to them
this.$triggers=$(document).find('[data-open="'+id+'"], [data-close="'+id+'"], [data-toggle="'+id+'"]').attr('aria-expanded','false').attr('aria-controls',id);// Add an overlay over the content if necessary
if(this.options.contentOverlay===true){var overlay=document.createElement('div');var overlayPosition=$(this.$element).css("position")==='fixed'?'is-overlay-fixed':'is-overlay-absolute';overlay.setAttribute('class','js-off-canvas-overlay '+overlayPosition);this.$overlay=$(overlay);if(overlayPosition==='is-overlay-fixed'){$('body').append(this.$overlay);}else{this.$element.siblings('[data-off-canvas-content]').append(this.$overlay);}}this.options.isRevealed=this.options.isRevealed||new RegExp(this.options.revealClass,'g').test(this.$element[0].className);if(this.options.isRevealed===true){this.options.revealOn=this.options.revealOn||this.$element[0].className.match(/(reveal-for-medium|reveal-for-large)/g)[0].split('-')[2];this._setMQChecker();}if(!this.options.transitionTime===true){this.options.transitionTime=parseFloat(window.getComputedStyle($('[data-off-canvas]')[0]).transitionDuration)*1000;}}},{key:'_events',value:function _events(){this.$element.off('.zf.trigger .zf.offcanvas').on({'open.zf.trigger':this.open.bind(this),'close.zf.trigger':this.close.bind(this),'toggle.zf.trigger':this.toggle.bind(this),'keydown.zf.offcanvas':this._handleKeyboard.bind(this)});if(this.options.closeOnClick===true){var $target=this.options.contentOverlay?this.$overlay:$('[data-off-canvas-content]');$target.on({'click.zf.offcanvas':this.close.bind(this)});}}},{key:'_setMQChecker',value:function _setMQChecker(){var _this=this;$(window).on('changed.zf.mediaquery',function(){if(Foundation.MediaQuery.atLeast(_this.options.revealOn)){_this.reveal(true);}else{_this.reveal(false);}}).one('load.zf.offcanvas',function(){if(Foundation.MediaQuery.atLeast(_this.options.revealOn)){_this.reveal(true);}});}},{key:'reveal',value:function reveal(isRevealed){var $closer=this.$element.find('[data-close]');if(isRevealed){this.close();this.isRevealed=true;this.$element.attr('aria-hidden','false');this.$element.off('open.zf.trigger toggle.zf.trigger');if($closer.length){$closer.hide();}}else{this.isRevealed=false;this.$element.attr('aria-hidden','true');this.$element.off('open.zf.trigger toggle.zf.trigger').on({'open.zf.trigger':this.open.bind(this),'toggle.zf.trigger':this.toggle.bind(this)});if($closer.length){$closer.show();}}}},{key:'_stopScrolling',value:function _stopScrolling(event){return false;}},{key:'_recordScrollable',value:function _recordScrollable(event){var elem=this;// called from event handler context with this as elem
// If the element is scrollable (content overflows), then...
if(elem.scrollHeight!==elem.clientHeight){// If we're at the top, scroll down one pixel to allow scrolling up
if(elem.scrollTop===0){elem.scrollTop=1;}// If we're at the bottom, scroll up one pixel to allow scrolling down
if(elem.scrollTop===elem.scrollHeight-elem.clientHeight){elem.scrollTop=elem.scrollHeight-elem.clientHeight-1;}}elem.allowUp=elem.scrollTop>0;elem.allowDown=elem.scrollTop<elem.scrollHeight-elem.clientHeight;elem.lastY=event.originalEvent.pageY;}},{key:'_stopScrollPropagation',value:function _stopScrollPropagation(event){var elem=this;// called from event handler context with this as elem
var up=event.pageY<elem.lastY;var down=!up;elem.lastY=event.pageY;if(up&&elem.allowUp||down&&elem.allowDown){event.stopPropagation();}else{event.preventDefault();}}},{key:'open',value:function open(event,trigger){if(this.$element.hasClass('is-open')||this.isRevealed){return;}var _this=this;if(trigger){this.$lastTrigger=trigger;}if(this.options.forceTo==='top'){window.scrollTo(0,0);}else if(this.options.forceTo==='bottom'){window.scrollTo(0,document.body.scrollHeight);}/**
     * Fires when the off-canvas menu opens.
     * @event OffCanvas#opened
     */_this.$element.addClass('is-open');this.$triggers.attr('aria-expanded','true');this.$element.attr('aria-hidden','false').trigger('opened.zf.offcanvas');// If `contentScroll` is set to false, add class and disable scrolling on touch devices.
if(this.options.contentScroll===false){$('body').addClass('is-off-canvas-open').on('touchmove',this._stopScrolling);this.$element.on('touchstart',this._recordScrollable);this.$element.on('touchmove',this._stopScrollPropagation);}if(this.options.contentOverlay===true){this.$overlay.addClass('is-visible');}if(this.options.closeOnClick===true&&this.options.contentOverlay===true){this.$overlay.addClass('is-closable');}if(this.options.autoFocus===true){this.$element.one(Foundation.transitionend(this.$element),function(){var canvasFocus=_this.$element.find('[data-autofocus]');if(canvasFocus.length){canvasFocus.eq(0).focus();}else{_this.$element.find('a, button').eq(0).focus();}});}if(this.options.trapFocus===true){this.$element.siblings('[data-off-canvas-content]').attr('tabindex','-1');Foundation.Keyboard.trapFocus(this.$element);}}},{key:'close',value:function close(cb){if(!this.$element.hasClass('is-open')||this.isRevealed){return;}var _this=this;_this.$element.removeClass('is-open');this.$element.attr('aria-hidden','true')/**
       * Fires when the off-canvas menu opens.
       * @event OffCanvas#closed
       */.trigger('closed.zf.offcanvas');// If `contentScroll` is set to false, remove class and re-enable scrolling on touch devices.
if(this.options.contentScroll===false){$('body').removeClass('is-off-canvas-open').off('touchmove',this._stopScrolling);this.$element.off('touchstart',this._recordScrollable);this.$element.off('touchmove',this._stopScrollPropagation);}if(this.options.contentOverlay===true){this.$overlay.removeClass('is-visible');}if(this.options.closeOnClick===true&&this.options.contentOverlay===true){this.$overlay.removeClass('is-closable');}this.$triggers.attr('aria-expanded','false');if(this.options.trapFocus===true){this.$element.siblings('[data-off-canvas-content]').removeAttr('tabindex');Foundation.Keyboard.releaseFocus(this.$element);}}},{key:'toggle',value:function toggle(event,trigger){if(this.$element.hasClass('is-open')){this.close(event,trigger);}else{this.open(event,trigger);}}},{key:'_handleKeyboard',value:function _handleKeyboard(e){var _this2=this;Foundation.Keyboard.handleKey(e,'OffCanvas',{close:function close(){_this2.close();_this2.$lastTrigger.focus();return true;},handled:function handled(){e.stopPropagation();e.preventDefault();}});}},{key:'destroy',value:function destroy(){this.close();this.$element.off('.zf.trigger .zf.offcanvas');this.$overlay.off('.zf.offcanvas');Foundation.unregisterPlugin(this);}}]);return OffCanvas;}();OffCanvas.defaults={/**
   * Allow the user to click outside of the menu to close it.
   * @option
   * @type {boolean}
   * @default true
   */closeOnClick:true,/**
   * Adds an overlay on top of `[data-off-canvas-content]`.
   * @option
   * @type {boolean}
   * @default true
   */contentOverlay:true,/**
   * Enable/disable scrolling of the main content when an off canvas panel is open.
   * @option
   * @type {boolean}
   * @default true
   */contentScroll:true,/**
   * Amount of time in ms the open and close transition requires. If none selected, pulls from body style.
   * @option
   * @type {number}
   * @default 0
   */transitionTime:0,/**
   * Type of transition for the offcanvas menu. Options are 'push', 'detached' or 'slide'.
   * @option
   * @type {string}
   * @default push
   */transition:'push',/**
   * Force the page to scroll to top or bottom on open.
   * @option
   * @type {?string}
   * @default null
   */forceTo:null,/**
   * Allow the offcanvas to remain open for certain breakpoints.
   * @option
   * @type {boolean}
   * @default false
   */isRevealed:false,/**
   * Breakpoint at which to reveal. JS will use a RegExp to target standard classes, if changing classnames, pass your class with the `revealClass` option.
   * @option
   * @type {?string}
   * @default null
   */revealOn:null,/**
   * Force focus to the offcanvas on open. If true, will focus the opening trigger on close.
   * @option
   * @type {boolean}
   * @default true
   */autoFocus:true,/**
   * Class used to force an offcanvas to remain open. Foundation defaults for this are `reveal-for-large` & `reveal-for-medium`.
   * @option
   * @type {string}
   * @default reveal-for-
   * @todo improve the regex testing for this.
   */revealClass:'reveal-for-',/**
   * Triggers optional focus trapping when opening an offcanvas. Sets tabindex of [data-off-canvas-content] to -1 for accessibility purposes.
   * @option
   * @type {boolean}
   * @default false
   */trapFocus:false// Window exports
};Foundation.plugin(OffCanvas,'OffCanvas');}(jQuery);});