var widgets = require('jupyter-js-widgets');

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

        requirejs.config({
            paths: { 
                'path': ['http://aladin.u-strasbg.fr/AladinLite/api/v2/beta/aladin']
                                                       // strip .js ^, require adds it back
            }
        })
        require(['path'], function(path) {   
            return {};
        });

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
