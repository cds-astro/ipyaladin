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
npm run dev
```

As long as the terminal is open, this will listen to any changes made in the python and
javascript sides of the widget. You can live-develop and test in a notebook. Your
changes will be applied on kernel restarts.

## Git hooks

We use `Ruff` for formatting the python files, and `husky` with `prettier` for the other
files. These linters are installed as git hooks that will be run at the pre-commit
stage. It means that your commits will not pass with violations to `Ruff` or `prettier`
rules. If one of your commits is rejected, simply apply the requested changes, `git add`
the files again, and attempt to commit again until all the checks pass.

## Development branch

The development happens in the branch `dev` and are merged in `master` only at release
time.
If your modifications only affect the documentation and are related to the latest stable
version of `iPyAladin`, your can use `master` as the base branch.

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

The UI tests do not run in the github CI. It is up to you to run them locally to make
sure that the new changes did not affect the behavior of the widget.
The snapshots can give false negative depending on the installed fonts on your machine,
on the version of your browser... The idea is to check visually if something is
blatantly wrong.

The snapshots can be regenerated with

```sh
npm run update-snapshots
```

### Check that the documentation still builds

You'll need `pandoc`, see https://pandoc.org/installing.html
Then,

```sh
pip install .[docs]
cd docs
make clean html
```

### Adding a changelog entry

The changelog is a single file `CHANGELOG.md`. If your changes affect the users,
write a short description in the [unreleased] section. It is nice to add either a
PR or issue number.

## How does it work

`ipyaladin` wraps `Aladin-Lite` into notebooks thanks to `anywidgets`. The useful
documentation pages are:

- [anywidget](https://anywidget.dev/)
- [Aladin-Lite public API](https://cds-astro.github.io/aladin-lite/)
- [Traitlets](https://traitlets.readthedocs.io/en/stable/) (they are used to share
  information between the python and javascript sides)
