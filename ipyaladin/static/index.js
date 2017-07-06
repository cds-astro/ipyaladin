define(["jupyter-js-widgets"], function(__WEBPACK_EXTERNAL_MODULE_2__) { return /******/ (function(modules) { // webpackBootstrap
/******/ 	// install a JSONP callback for chunk loading
/******/ 	var parentJsonpFunction = window["webpackJsonp"];
/******/ 	window["webpackJsonp"] = function webpackJsonpCallback(chunkIds, moreModules) {
/******/ 		// add "moreModules" to the modules object,
/******/ 		// then flag all "chunkIds" as loaded and fire callback
/******/ 		var moduleId, chunkId, i = 0, callbacks = [];
/******/ 		for(;i < chunkIds.length; i++) {
/******/ 			chunkId = chunkIds[i];
/******/ 			if(installedChunks[chunkId])
/******/ 				callbacks.push.apply(callbacks, installedChunks[chunkId]);
/******/ 			installedChunks[chunkId] = 0;
/******/ 		}
/******/ 		for(moduleId in moreModules) {
/******/ 			if(Object.prototype.hasOwnProperty.call(moreModules, moduleId)) {
/******/ 				modules[moduleId] = moreModules[moduleId];
/******/ 			}
/******/ 		}
/******/ 		if(parentJsonpFunction) parentJsonpFunction(chunkIds, moreModules);
/******/ 		while(callbacks.length)
/******/ 			callbacks.shift().call(null, __webpack_require__);
/******/
/******/ 	};
/******/
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// object to store loaded and loading chunks
/******/ 	// "0" means "already loaded"
/******/ 	// Array means "loading", array contains callbacks
/******/ 	var installedChunks = {
/******/ 		0:0
/******/ 	};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;
/******/
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/ 	// This file contains only the entry chunk.
/******/ 	// The chunk loading function for additional chunks
/******/ 	__webpack_require__.e = function requireEnsure(chunkId, callback) {
/******/ 		// "0" is the signal for "already loaded"
/******/ 		if(installedChunks[chunkId] === 0)
/******/ 			return callback.call(null, __webpack_require__);
/******/
/******/ 		// an array means "currently loading".
/******/ 		if(installedChunks[chunkId] !== undefined) {
/******/ 			installedChunks[chunkId].push(callback);
/******/ 		} else {
/******/ 			// start chunk loading
/******/ 			installedChunks[chunkId] = [callback];
/******/ 			var head = document.getElementsByTagName('head')[0];
/******/ 			var script = document.createElement('script');
/******/ 			script.type = 'text/javascript';
/******/ 			script.charset = 'utf-8';
/******/ 			script.async = true;
/******/
/******/ 			script.src = __webpack_require__.p + "" + chunkId + ".index.js";
/******/ 			head.appendChild(script);
/******/ 		}
/******/ 	};
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

	// Entry point for the notebook bundle containing custom model definitions.
	//
	// Setup notebook base URL
	//
	// Some static assets may be required by the custom widget javascript. The base
	// url for the notebook is not known at build time and is therefore computed
	// dynamically.
	__webpack_require__.p = document.querySelector('body').getAttribute('data-base-url') + 'nbextensions/jupyter-widget-ipyaladin/';
	
	// Export widget models and views, and the npm package version number.
	module.exports = __webpack_require__(1);
	
	module.exports['version'] = __webpack_require__(5).version;


/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

	var widgets = __webpack_require__(2);
	
	// Custom Model. Custom widgets models must at least provide default values
	// for model attributes, including
	//
	//  - `_view_name`
	//  - `_view_module`
	//  - `_view_module_version`
	//
	//  - `_model_name`
	//  - `_model_module`
	//  - `_model_module_version`
	//
	//  when different from the base class.
	
	// When serialiazing the entire widget state for embedding, only values that
	// differ from the defaults will be specified.
	
	var ViewAladin = widgets.DOMWidgetView.extend({
	
	    // Render the view.
	    render: function() {
	        var link = document.createElement('link');
	        link.type = "text/css";
	        link.rel = "stylesheet";
	        link.href = "//aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css";
	        document.getElementsByTagName("head")[0].appendChild(link);
	
	        ;
	        __webpack_require__.e/* require */(1, function(__webpack_require__) { var __WEBPACK_AMD_REQUIRE_ARRAY__ = [__webpack_require__(3)]; (function(path) {   
	            return {};
	        }.apply(null, __WEBPACK_AMD_REQUIRE_ARRAY__));});
	
	        // variation UN
	        var div_test = document.createElement('div');
	        div_test.id = 'aladin-lite-div';
	        div_test.setAttribute("style","width:100%;height:400px;");
	        this.el.appendChild(div_test);
	        var Aladin = A.aladin([div_test], {showFullscreenControl: false, fov:1.5});
	    }
	});
	
	
	module.exports = {
	    ViewAladin: ViewAladin,
	};


/***/ }),
/* 2 */
/***/ (function(module, exports) {

	module.exports = __WEBPACK_EXTERNAL_MODULE_2__;

/***/ }),
/* 3 */,
/* 4 */,
/* 5 */
/***/ (function(module, exports) {

	module.exports = {
		"name": "jupyter-widget-ipyaladin",
		"version": "0.1.0",
		"description": "test ipyaladin",
		"author": "JD",
		"main": "src/index.js",
		"repository": {
			"type": "git",
			"url": "https://github.com/jupyter/test_ipyaladin.git"
		},
		"keywords": [
			"jupyter",
			"widgets",
			"ipython",
			"ipywidgets"
		],
		"scripts": {
			"prepublish": "webpack",
			"test": "echo \"Error: no test specified\" && exit 1"
		},
		"devDependencies": {
			"json-loader": "^0.5.4",
			"webpack": "^1.12.14"
		},
		"dependencies": {
			"jupyter-js-widgets": "^2.1.4",
			"underscore": "^1.8.3"
		}
	};

/***/ })
/******/ ])});;
//# sourceMappingURL=index.js.map