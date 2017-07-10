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
            aladin_options[opt[i]]= this.model.get(opt[i]);
        this.al= aladin_lib.A.aladin([div_test], aladin_options);
        // Declaration of the variable's listeners:
        this.aladin_events();
        this.model_events();
    },

    // Variables's listeners on the js side:
    aladin_events: function () {
        var that = this;
        /*this.al.view.fov.on('change', function (e) {
            // TO COMPLETE
        });*/
    },

    // Variables's listeners on the python side:
    model_events: function () {
        var that = this;
        this.listenTo(this.model, 'change:fov', function () {
            this.al.setFoV(this.model.get('fov'));
        }, this);
        this.listenTo(this.model, 'change:target', function () {
            this.al.gotoObject(this.model.get('target'));
        }, this);
        this.listenTo(this.model, 'change:cooFrame', function () {
            this.al.view.changeFrame(this.model.get('cooFrame'));
        }, this);
        this.listenTo(this.model, 'change:survey', function () {
            this.al.setImageSurvey(this.model.get('survey'));
        }, this);
    }

});

// Node.js exports
module.exports = {
    ViewAladin : ViewAladin,
    ModelAladin : ModelAladin
};

/* TODO:

 PRIORITIES:
      Synchrnoize options (js side)
 POST-PRIORITIES:
      implements others functionalities (more precisely: python-side functions)
 DISTANT FUTURE:
 load AladinLite library from http...
 zoom problem...
 */