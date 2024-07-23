# Community

Ipyaladin is developed by the Strasbourg Astronomical Data Centre. If it was useful for your
research, please consider [citing it](https://aladin.cds.unistra.fr/AladinLite/ipyaladin/#acknowledgement).

## Contributions

Contributions are welcome, you can for example:

- open an issue if you find a bug or would like a new feature,
- work on one of the open issues that have been discussed and milestoned
- improve the documentation

## Development installation

To start developing `ipyaladin`, clone the repository and do

```sh
pip install pre-commit
pre-commit install
npm run dev
```

This will listen to any changes made in the python and javascript sides of the widget.
You can live-develop in a notebook application and your changes will be affected on
kernel restarts.

We use pre-commit with `Ruff` for formatting the python files, and `husky` with
`prettier` for the other files. This means than before accepting you commits, you'll
see if any change is needed. If it is the case, apply the requested changes, `git add`
the files again, and attempt to commit until all the checks pass.

## Running the tests

There are different tests in the module.

### Python tests

To run the python tests, do:

```sh
python -m pytest
```

### Javascript tests

To run the javascript tests, do:

```sh
npm run start-test-server
```

then in an other terminal,

```sh
npm run js-test
```

### Check that the documentation still builds

You'll need `pandoc`, see https://pandoc.org/installing.html
Then,

```sh
pip install .[docs]
cd docs
make clean html
```

## How does it work

`ipyaladin` wraps `Aladin-Lite` into notebooks thanks to `anywidgets`. The useful
documentation pages are:

- [anywidget](https://anywidget.dev/)
- [Aladin-Lite public API](https://cds-astro.github.io/aladin-lite/)
- [Traitlets](https://traitlets.readthedocs.io/en/stable/) (they are used to share
  information between the python and javascript sides)
