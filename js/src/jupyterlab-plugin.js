var aladin = require('./index');

var base = require('@jupyter-widgets/base');

/**
 * The widget manager provider.
 */
module.exports = {
  id: 'ipyaladin',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'ipyaladin',
          version: aladin.version,
          exports: aladin
      });
    },
  autoStart: true
}
