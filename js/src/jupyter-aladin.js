var widgets = require('jupyter-js-widgets');

var test= require('./aladin_lib.js');

var CSS_Loader= ({
    is_css_loaded: false,

    load_css: function(data){
        // le chargement s'effectue uniquement si la feuille de style n'est pas déjà présente
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

var ViewAladin = widgets.DOMWidgetView.extend({
    
    initialize: function (options) {
        ViewAladin.__super__.initialize.apply(this, arguments);
    },

    // Render the view.
    render: function() {
        // chargement de la feuille de style css
        CSS_Loader.load_css();
        // creation de l'element div contenant le widget
        var div_test = document.createElement('div');
        div_test.id = 'aladin-lite-div';
        div_test.setAttribute("style","width:100%;height:400px;");
        this.el.appendChild(div_test);
        // creation de l'instance d'Aladin avec application des options passées dans le constructeur
        var aladin_options= {};
        var opt= this.model.get('options');
        for(i=0; i<opt.length; i++)
            aladin_options[opt[i]]= this.model.get(opt[i]);
        // Attention!
        // si de la forme Aladin= test.aladin(....) :
        //  -> ne se lance pas automatiquement lors du chargement de la page
        //  -> plante systématiquement lorsqu'on tente de réexécuter le code dans la cellule
        //     (jusqu'au rechargement de la page)
        test.A.aladin([div_test], aladin_options);
    },
});

var ModelAladin = widgets.DOMWidgetModel.extend({
    defaults: _.extend({}, widgets.DOMWidgetModel.prototype.defaults, {
        _view_name : "ViewAladin",
        _model_name : "ModelAladin",
        _model_module : "jupyter-aladin",
        _view_module : "jupyter-aladin",

        target : "messier 104",
        options : []
    })
});

module.exports = {
    CSS_Loader : CSS_Loader,
    ViewAladin : ViewAladin,
    ModelAladin : ModelAladin
};

// TODO:
// !!! documentation propre de code anglais avec explications, etc....
// voir si module.exports possible de retirer qq uns
// voir options (cf options non declarees en .py mais existantes dans lib)
//  -> target='NGC 2175', cooFrame='galactic', reticleSize= 64 :fonctionne
// sur example_1: flash des 2 widget lorsque reload du code d'1 cell
// (=> normal cf m^ instance? => poser q.)
// charger aladin.js depuis http...
// faire fonction changement état widget
// autres fonctionnalités
// problème du zoom

//--------- notes:
// maj cachées des notebook exemples (attention lors du puch sur dépôt)
// nécessité de supprimer la librairie manuellement (??)
//  -> dans ~/anaconda3/share/jupyter/nbextensions