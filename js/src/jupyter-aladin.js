// For the moment, the AladinLite library is not online,
// and is located in the same repository of this file.
// The version currently used is the beta version, whose url is:
// http://aladin.u-strasbg.fr/AladinLite/api/v2/beta/aladin.js
// For the library to be compatible with node.js, the following code must be added at the file's end:
//module.exports = {
//    A: A
//};
var aladin_lib= require('./aladin_lib.js');

// Allow us to use the DOMWidgetView base class for our models/views.
// Additionnaly, this is where we put by default all the external libraries
// fetched by using webpack (see webpack.config.js file).
var widgets = require('jupyter-js-widgets');

// The sole purpose of this module is to load the css stylesheet when the first instance
// of the AladinLite widget
var CSS_Loader= ({

    is_css_loaded: false,

    load_css: function(data){
        if(!CSS_Loader.is_css_loaded){
            var link = document.createElement('link');
            link.type = "text/css";
            link.rel = "stylesheet";
            link.href = "//aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css";
            document.getElementsByTagName("head")[0].appendChild(link);
            CSS_Loader.is_css_loaded= true;
        }
    }
});

/**
 * Definition of the AladinLite widget's model in the browser
 * Useful documentation about the widget's global implementation : 
 * (from http://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Custom.html)
 * The IPython widget framework front end relies heavily on Backbone.js.
 * Backbone.js is an MVC (model view controller) framework. 
 * Widgets defined in the back end are automatically synchronized with generic Backbone.js
 * models in the front end.
 * The traitlets are added to the front end instance automatically on first state push.
 * The _view_name trait that you defined earlier is used by the widget framework to create
 * the corresponding Backbone.js view and link that view to the model.
 */
var ModelAladin = widgets.DOMWidgetModel.extend({
    defaults: _.extend({}, widgets.DOMWidgetModel.prototype.defaults, {
        _view_name : "ViewAladin",
        _model_name : "ModelAladin",
        _model_module : "jupyter-aladin",
        _view_module : "jupyter-aladin",
    })
});


/**
 * Definition of the AladinLite widget's view in the browser
 */
var ViewAladin = widgets.DOMWidgetView.extend({
    // The attr_js and attr_py variables are used as lock between the listeners
    // of the corresponding attribute, python-side and javascript-side,
    // in order to prevent infinite loop between listener calls on value change
    fov_js: false,
    fov_py: false,
    target_js: false,
    target_py: false,

    // This function is automatically called when the python-side widget's instance is displayed
    // (by calling it at the end of a bloc or by using the display() function)
    render: function() {
        // We load the css stylesheet.
        CSS_Loader.load_css();
        // We create the DOM element that will contain our widget
        // Note: it seems that the 'el' element cannot directly be used as a container for
        // the AladinLite widget wihthout causing rendering issues.
        // Thus we use a div element and put it inside the 'el' element.
        var div_test = document.createElement('div');
        div_test.id = 'aladin-lite-div'
        div_test.setAttribute("style","width:100%;height:400px;");
        this.el.appendChild(div_test);
        // We get the options set on the python side and create an instance of the AladinLite object.
        var aladin_options= {};
        var opt= this.model.get('options');
        for(i=0; i<opt.length; i++)
            aladin_options[this.convert_pyname_to_jsname(opt[i])]= this.model.get(opt[i]);
        this.al= aladin_lib.A.aladin([div_test], aladin_options);
        // Declaration of the variable's listeners:
        this.aladin_events();
        this.model_events();
    },

    convert_pyname_to_jsname: function (pyname) {
        var i, temp= pyname.split('_');
        for(i=1; i<temp.length; i++){
            temp[i]= temp[i].charAt(0).toUpperCase() + temp[i].slice(1);
        }
        return temp.join('');
    },

    // Variables's listeners on the js side:
    aladin_events: function () {
        var that = this;
        this.al.on('zoomChanged', function(fov) {
            if(!that.fov_py){
                that.fov_js= true;
                // fov MUST be cast into float in order to be sent to the model
                that.model.set('fov', parseFloat(fov.toFixed(5)));
                // Note: touch function must be called after calling the model's set method
                that.touch();
            }else{
                that.fov_py= false;
            }
        });
        this.al.on('positionChanged', function(position) {
            if(!that.target_py){
                that.target_js= true;
                that.model.set('target', '' + position.ra.toFixed(6) + ' ' + position.dec.toFixed(6));
                that.touch();
            }else{
                that.target_py= false;
            }
            
        });
    },

    // Variables's listeners on the python side:
    model_events: function () {
        var that = this;
        // Model's class parameters listeners
        this.listenTo(this.model, 'change:fov', function () {
            if(!that.fov_js){
                that.fov_py= true;
                that.al.setFoV(that.model.get('fov'));
            }else{
                that.fov_js= false;
            }
        }, this);
        this.listenTo(this.model, 'change:target', function () {
            if(!that.target_js){
                that.target_py= true;
                that.al.gotoObject(that.model.get('target'));
            }else{
                that.target_js= false;
            }
        }, this);
        this.listenTo(this.model, 'change:coo_frame', function () {
            that.al.setFrame(that.model.get('coo_frame'));
        }, this);
        this.listenTo(this.model, 'change:survey', function () {
            that.al.setImageSurvey(that.model.get('survey'));
        }, this);
        // Model's functions parameters listeners
        this.listenTo(this.model, 'change:votable_from_URL_flag', function(){
            that.al.addCatalog(aladin_lib.A.catalogFromURL(that.model.get('votable_URL'), that.model.get('votable_options')));
        }, this);
        this.listenTo(this.model, 'change:table_flag', function(){
            var cat = aladin_lib.A.catalog({onClick: 'showTable'});
            that.al.addCatalog(cat);
            cat.addSourcesAsArray(that.model.get('table_keys'), that.model.get('table_columns'))
        }, this);
    }

});

// Node.js exports
module.exports = {
    ViewAladin : ViewAladin,
    ModelAladin : ModelAladin
};

/** 
TODO:
load AladinLite library from http...
zoom problem...
 */