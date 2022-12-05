import { DOMWidgetModel, DOMWidgetView } from '@jupyter-widgets/base';
// Allow us to use the DOMWidgetView base class for our models/views.
// Additionnaly, this is where we put by default all the external libraries
// fetched by using webpack (see webpack.config.js file).
var _ = require("underscore");
// The sole purpose of this module is to load the css stylesheet when the first instance
// of the AladinLite widget
const loadScript = (FILE_URL, async = true, type = "text/javascript") => {
    return new Promise((resolve, reject) => {
        try {
            const scriptEle = document.createElement("script");
            scriptEle.type = type;
            scriptEle.async = async;
            scriptEle.src = FILE_URL;

            scriptEle.addEventListener("load", (ev) => {
                resolve({ status: true });
            });

            scriptEle.addEventListener("error", (ev) => {
                reject({
                    status: false,
                    message: `Failed to load the script ＄{FILE_URL}`
                });
            });

            document.getElementsByTagName("head")[0].appendChild(scriptEle);
        } catch (error) {
            reject(error);
        }
    });
};
var AladinLiteJS_Loader = loadScript("//aladin.u-strasbg.fr/AladinLite/api/v3/latest/aladin.js")
    .then(async () => {
        await A.init;
    });

// See example.py for the kernel counterpart to this file.

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
// differ from the defaults will be serialized.

export class AladinModel extends DOMWidgetModel {
    defaults() {
      return {
        ...super.defaults(),
        _model_name : 'AladinModel',
        _view_name : 'AladinView',

        _model_module : 'ipyaladin',
        _view_module : 'ipyaladin',

        _model_module_version : '0.2.0',
        _view_module_version : '0.2.0',
      };
    }
  }


var idxView = 0;
export class AladinView extends DOMWidgetView {
    render() {
        // We load the aladin lite script
        AladinLiteJS_Loader.then(() => {
            this.fov_js = false;
            this.fov_py = false;
            this.target_js = false;
            this.target_py = false;

            // We create the DOM element that will contain our widget
            // Note: it seems that the 'el' element cannot directly be used as a container for
            // the AladinLite widget wihthout causing rendering issues.
            // Thus we use a div element and put it inside the 'el' element.
            if (this.div) {
                this.el.remove(this.div);
            }

            this.div = document.createElement('div');
            this.div.id = 'aladin-lite-div' + parseInt(idxView);
            idxView += 1;
            // TODO: should this style be somehow inherited from the widget Layout attribute?
            this.div.setAttribute("style","width:100%;height:400px;");

            // We get the options set on the python side and create an instance of the AladinLite object.
            var aladin_options = {};
            var opt = this.model.get('options');
            for(var i = 0; i < opt.length; i++) {
                aladin_options[this.convert_pyname_to_jsname(opt[i])] = this.model.get(opt[i]);
            }

            // Observer triggered when this.el has been changed
            const observer = new MutationObserver((mutations_list) => {
                mutations_list.forEach((mutation) => {
                    mutation.addedNodes.forEach((added_node) => {
                        if(added_node.id == this.div.id) {
                            // In some contexts (Jupyter notebook for instance), the parent div changes little time after Aladin Lite creation
                            // this results in canvas dimension to be incorrect.
                            // The following line tries to fix this issue
                            // This timeout was found in the Aladin Lite code and concerns a fix
                            // regarding its use inside jupyter notebook
                            // Therefore it is better to let it here
                            setTimeout(() => {
                                this.al = A.aladin([this.div], aladin_options);

                                // Declaration of the variable's listeners:
                                this.aladin_events();
                                this.model_events();
                            }, 1000);
                        }
                    });
                });
            });

            observer.observe(this.el, {subtree: false, childList: true});

            this.el.appendChild(this.div);
        })
    }

    convert_pyname_to_jsname(pyname) {
        var i, temp= pyname.split('_');
        for(i=1; i<temp.length; i++){
            temp[i]= temp[i].charAt(0).toUpperCase() + temp[i].slice(1);
        }
        return temp.join('');
    }

    aladin_events() {
        var that = this;
        this.al.on('zoomChanged', function(fov) {
            if(!that.fov_py){
                that.fov_js = true;
                // fov MUST be cast into float in order to be sent to the model
                that.model.set('fov', parseFloat(fov.toFixed(5)));
                // Note: touch function must be called after calling the model's set method
                that.touch();
            } else {
                that.fov_py = false;
            }
        });
        this.al.on('positionChanged', function(position) {
            if(!that.target_py) {
                that.target_js = true;
                that.model.set('target', '' + position.ra.toFixed(6) + ' ' + position.dec.toFixed(6));
                that.touch();
            } else {
                that.target_py = false;
            }
        });
    }

    model_events() {
        var that = this;
        // Model's class parameters listeners
        this.listenTo(this.model, 'change:fov', function () {
            if(!that.fov_js){
                that.fov_py= true;
                that.al.setFoV(that.model.get('fov'));
            } else {
                that.fov_js= false;
            }
        }, this);
        this.listenTo(this.model, 'change:target', function () {
            if(!that.target_js){
                that.target_py= true;
                that.al.gotoObject(that.model.get('target'));
            } else {
                that.target_js= false;
            }
        }, this);
        this.listenTo(this.model, 'change:coo_frame', function () {
            that.al.setFrame(that.model.get('coo_frame'));
        }, this);
        this.listenTo(this.model, 'change:survey', function () {
            that.al.setImageSurvey(that.model.get('survey'));
        }, this);
        this.listenTo(this.model, 'change:overlay_survey', function () {
            that.al.setOverlayImageLayer(that.model.get('overlay_survey'));
        }, this);
        this.listenTo(this.model, 'change:overlay_survey_opacity', function () {
            that.al.getOverlayImageLayer().setAlpha(that.model.get('overlay_survey_opacity'));
        }, this);

        // Model's functions parameters listeners
        this.listenTo(this.model, 'change:votable_from_URL_flag', function(){
            that.al.addCatalog(A.catalogFromURL(that.model.get('votable_URL'), that.model.get('votable_options')));
        }, this);

        this.listenTo(this.model, 'change:moc_from_URL_flag', function(){
            that.al.addMOC(A.MOCFromURL(that.model.get('moc_URL'), that.model.get('moc_options')));
        }, this);

        this.listenTo(this.model, 'change:moc_from_dict_flag', function(){
            that.al.addMOC(A.MOCFromJSON(that.model.get('moc_dict'), that.model.get('moc_options')));
        }, this);

        this.listenTo(this.model, 'change:table_flag', function(){
            var cat = A.catalog({onClick: 'showTable'});
            that.al.addCatalog(cat);
            cat.addSourcesAsArray(that.model.get('table_keys'), that.model.get('table_columns'))
        }, this);

        this.listenTo(this.model, 'change:overlay_from_stcs_flag', function() {
            var overlay = A.graphicOverlay(that.model.get('overlay_options'));
            that.al.addOverlay(overlay);
            overlay.addFootprints(A.footprintsFromSTCS(that.model.get('stc_string')));
        }, this);

        this.listenTo(this.model, 'change:listener_flag', function(){
            var type= that.model.get('listener_type');
            that.al.on(type, function(object) {
                if (type==='select') {
                    var sources = object;
                    // first, deselect previously selected sources
                    for (var k=0; k<that.al.view.catalogs.length; k++) {
                        that.al.view.catalogs[k].deselectAll();
                    }
                    var sourcesData = [];
                    for (var k = 0; k<sources.length ; k++) {
                        var source = sources[k];
                        source.select();
                        sourcesData.push(
                            {
                                data: source.data,
                                dec: source.dec,
                                ra: source.ra,
                                x: source.x,
                                y: source.y
                            }
                        );
                    }
                    that.send({
                        'event': 'callback',
                        'type': type,
                        'data': sourcesData,
                    });

                    return;

                }

                // Send json object to the python-side of the application
                // We only send object.data because the whole object possess a catalog attribute
                // that cause error when trying to convert it into json
                // (at least on chrome, due to object circularization)
                if (object) {
                    that.send({
                        'event': 'callback',
                        'type': type,
                        'data': {'data': object.data,
                                 'dec': object.dec,
                                 'ra': object.ra,
                                 'x': object.x,
                                 'y': object.y}
                    });
                }
            });
        }, this);

        this.listenTo(this.model, 'change:rectangular_selection_flag', function(){
            that.al.select();
        });

        this.listenTo(this.model, 'change:thumbnail_flag', function(){
            that.al.exportAsPNG();
        });

        this.listenTo(this.model, 'change:color_map_flag', function() {
            const cmap = that.model.get('color_map_name');
            that.al.getBaseImageLayer().setColormap(cmap);
        });
    }
}
