import {AladinModel, AladinView, version} from './index';
import {IJupyterWidgetRegistry} from '@jupyter-widgets/base';

export const aladinWidgetPlugin = {
  id: 'ipyaladin:plugin',
  requires: [IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'ipyaladin',
          version: version,
          exports: { AladinModel, AladinView }
      });
  },
  autoStart: true
};

export default aladinWidgetPlugin;
