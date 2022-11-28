import {ModelAladin, ViewAladin} from './index.js';
import {IJupyterWidgetRegistry} from '@jupyter-widgets/base';

export const IPyAladinWidgetPlugin = {
  id: 'ipyaladin:plugin',
  requires: [IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'ipyaladin',
          version: '0.1.10',
          exports: { ModelAladin, ViewAladin }
      });
  },
  autoStart: true
};

export default IPyAladinWidgetPlugin;