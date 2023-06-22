import { DOMWidgetModel, DOMWidgetView } from '@jupyter-widgets/base';
// Allow us to use the DOMWidgetView base class for our models/views.
// Additionnaly, this is where we put by default all the external libraries
// fetched by using webpack (see webpack.config.js file).
let _ = require("underscore");
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
let AladinLiteJS_Loader = loadScript("https://code.jquery.com/jquery-3.6.1.min.js")
    .then(() => { return loadScript("https://aladin.u-strasbg.fr/AladinLite/api/v3/latest/aladin.js") })
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

        _model_module_version : '0.2.4',
        _view_module_version : '0.2.4',
      };
    }
  }


let idxView = 0;
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
            // creates the div section, height is fixed by the user or defaults to 400px
            let height = this.model.get("height");
            this.div.setAttribute("style","width:100%;height:" + height + "px;");

            // We get the options set on the python side and create an instance of the AladinLite object.
            let aladin_options = {};
            let options = this.model.get('options');
            for(let option of options) {
                aladin_options[this.convert_pyname_to_jsname(option)] = this.model.get(option);
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
        let temp= pyname.split('_');
        for(let i=1; i<temp.length; i++){
            temp[i]= temp[i].charAt(0).toUpperCase() + temp[i].slice(1);
        }
        return temp.join('');
    }

    aladin_events() {
        this.al.on('zoomChanged', (fov) => {
            if(!this.fov_py){
                this.fov_js = true;
                // fov MUST be cast into float in order to be sent to the model
                this.model.set('fov', parseFloat(fov.toFixed(5)));
                // Note: touch function must be called after calling the model's set method
                this.touch();
            } else {
                this.fov_py = false;
            }
        });
        this.al.on('positionChanged', (position) => {
            if(!this.target_py) {
                this.target_js = true;
                this.model.set('target', '' + position.ra.toFixed(6) + ' ' + position.dec.toFixed(6));
                this.touch();
            } else {
                this.target_py = false;
            }
        });
    }

    model_events() {
        // Model's class parameters listeners
        this.listenTo(this.model, 'change:fov',  () => {
            if(!this.fov_js){
                this.fov_py= true;
                this.al.setFoV(this.model.get('fov'));
            } else {
                this.fov_js= false;
            }
        }, this);
        this.listenTo(this.model, 'change:target', () => {
            if(!this.target_js){
                this.target_py= true;
                this.al.gotoObject(this.model.get('target'));
            } else {
                this.target_js= false;
            }
        }, this);
        this.listenTo(this.model, 'change:coo_frame', () => {
            this.al.setFrame(this.model.get('coo_frame'));
        }, this);
        this.listenTo(this.model, 'change:height', () => {
            let height = this.model.get('height');
            this.div.setAttribute("style","width:100%;height:" + height + "px;");
        }, this);
        this.listenTo(this.model, 'change:survey', () => {
            this.al.setImageSurvey(this.model.get('survey'));
        }, this);
        this.listenTo(this.model, 'change:overlay_survey', () => {
            this.al.setOverlayImageLayer(this.model.get('overlay_survey'));
        }, this);
        this.listenTo(this.model, 'change:overlay_survey_opacity', () => {
            this.al.getOverlayImageLayer().setAlpha(this.model.get('overlay_survey_opacity'));
        }, this);

        // Model's functions parameters listeners
        this.listenTo(this.model, 'change:votable_from_URL_flag', () => {
            this.al.addCatalog(A.catalogFromURL(this.model.get('votable_URL'), this.model.get('votable_options')));
        }, this);

        this.listenTo(this.model, 'change:moc_from_URL_flag', () => {
            this.al.addMOC(A.MOCFromURL(this.model.get('moc_URL'), this.model.get('moc_options')));
        }, this);

        this.listenTo(this.model, 'change:moc_from_dict_flag', () => {
            this.al.addMOC(A.MOCFromJSON(this.model.get('moc_dict'), this.model.get('moc_options')));
        }, this);

        this.listenTo(this.model, 'change:table_flag', () => {
            let cat = A.catalog({onClick: 'showTable'});
            this.al.addCatalog(cat);
            cat.addSourcesAsArray(this.model.get('table_keys'), this.model.get('table_columns'))
        }, this);

        this.listenTo(this.model, 'change:overlay_from_stcs_flag', () => {
            let overlay = A.graphicOverlay(this.model.get('overlay_options'));
            this.al.addOverlay(overlay);
            overlay.addFootprints(A.footprintsFromSTCS(this.model.get('stc_string')));
        }, this);

        this.listenTo(this.model, 'change:listener_flag', () => {
            let type= this.model.get('listener_type');
            this.al.on(type, (object) => {
                if (type==='select') {
                    let sources = object;
                    // first, deselect previously selected sources
                    for (let catalog of this.al.view.catalogs) {
                        catalog.deselectAll();
                    }
                    let sourcesData = [];
                    for (let source of sources) {
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
                    this.send({
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
                    this.send({
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

        this.listenTo(this.model, 'change:rectangular_selection_flag', () => {
            this.al.select();
        });

        this.listenTo(this.model, 'change:thumbnail_flag', () => {
            this.al.exportAsPNG();
        });

        this.listenTo(this.model, 'change:color_map_flag', () => {
            const cmap = this.model.get('color_map_name');
            this.al.getBaseImageLayer().setColormap(cmap);
        });
    }
}
