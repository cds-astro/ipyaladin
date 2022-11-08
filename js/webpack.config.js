const path = require('path');

module.exports = (env, argv) => {
    const devtool = argv.mode === 'development' ? 'source-map' : false;
    return [
        {// Notebook extension
        //
        // This bundle only contains the part of the JavaScript that is run on
        // load of the notebook. This section generally only performs
        // some configuration for requirejs, and provides the legacy
        // "load_ipython_extension" function which is required for any notebook
        // extension.
        //
            entry: './src/extension.js',
            output: {
                filename: 'extension.js',
                path: path.resolve(__dirname, '..', 'ipyaladin', 'static'),
                libraryTarget: 'amd'
            },
            devtool
        },
        {// Bundle for the notebook containing the custom widget views and models
        //
        // This bundle contains the implementation for the custom widget views and
        // custom widget.
        // It must be an amd module
        //
            entry: './src/index.js',
            output: {
                filename: 'index.js',
                path: path.resolve(__dirname, '..', 'ipyaladin', 'static'),
                libraryTarget: 'amd',
                publicPath: '',
            },
            devtool,
            externals: ['@jupyter-widgets/base']
        },
        /*{// Embeddable ipyaladin bundle
        //
        // This bundle is generally almost identical to the notebook bundle
        // containing the custom widget views and models.
        //
        // The only difference is in the configuration of the webpack public path
        // for the static assets.
        //
        // It will be automatically distributed by unpkg to work with the static
        // widget embedder.
        //
        // The target bundle is always `dist/index.js`, which is the path required
        // by the custom widget embedder.
        //
            entry: './src/embed.js',
            output: {
                filename: 'index.js',
                path: './dist/',
                libraryTarget: 'amd',
                publicPath: 'https://unpkg.com/ipyaladin@' + version + '/dist/'
            },
            devtool: 'source-map',
            module: {
                loaders: loaders
            },
            externals: ['jupyter-widgets']
        }*/
        // test
        /*{
            entry: './src/embed.js',
            output: {
                filename: 'test.js',
                path: './src/',
                libraryTarget: 'amd',
                publicPath: 'https://unpkg.com/ipyaladin@' + version + '/dist/'
            },
            devtool: 'source-map',
            module: {
                loaders: loaders
            },
            externals: ['jupyter-widgets']
        }*/
        /*{
            entry: './src/embed.js',
            output: {
                filename: 'test_aladin_output.js',
                // path: là où webpack build
                path: './dist/',
                libraryTarget: 'amd',
                // publicpath: utilisée lors du require des fichiers
                publicPath: 'http://aladin.u-strasbg.fr/AladinLite/api/v2/beta/aladin.js'
            },
            devtool: 'source-map',
            module: {
                loaders: loaders
            },
            externals: ['jupyter-widgets']
        }*/
    ];
}
