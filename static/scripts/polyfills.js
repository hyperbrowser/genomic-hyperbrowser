!function(){"use strict";window.console=window.console||{log:function(){},debug:function(){},info:function(){},warn:function(){},error:function(){},assert:function(){}},Object.assign=Object.assign||_.extend;for(var a=0,b=["ms","moz","webkit","o"],c=0;c<b.length&&!window.requestAnimationFrame;++c)window.requestAnimationFrame=window[b[c]+"RequestAnimationFrame"],window.cancelRequestAnimationFrame=window[b[c]+"CancelRequestAnimationFrame"];window.requestAnimationFrame||(window.requestAnimationFrame=function(b){var c=(new Date).getTime(),d=Math.max(0,16-(c-a)),e=window.setTimeout(function(){b(c+d)},d);return a=c+d,e}),window.cancelAnimationFrame||(window.cancelAnimationFrame=function(a){clearTimeout(a)});var d=[{name:"canvas",compatible:function(){return window.CanvasRenderingContext2D}},{name:"sessionStorage",compatible:function(){try{return window.sessionStorage.length>=0}catch(a){}return!1}}],e=d.filter(function(a){return!a.compatible()}).map(function(a){return a.name});if(e.length){var f=document.querySelectorAll('link[rel="index"]').item(0);f&&(window.location=f.href+"static/incompatible-browser.html"),console.log("incompatible browser:\n"+e.join("\n"))}}();
//# sourceMappingURL=../maps/polyfills.js.map