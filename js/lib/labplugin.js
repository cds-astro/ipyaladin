import {AladinModel, AladinView} from './index';
import {IJupyterWidgetRegistry} from '@jupyter-widgets/base';
import packageInfo from '../package.json';

export const aladinWidgetPlugin = {
  id: 'ipyaladin:plugin',
  requires: [IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'ipyaladin',
          version: packageInfo.version,
          exports: { AladinModel, AladinView }
      });
  },
  autoStart: true
};

export default aladinWidgetPlugin;
