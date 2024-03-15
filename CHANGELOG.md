# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Memo on sections

- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.

## [0.3.0]

### Changed

- The ipyaladin module is now built on anywidget (https://anywidget.dev/)
- Aladin instances now have a `clicked_object` attribute that contains the information of
  the last clicked object (ra, dec, and catalog content)
- Each ipyaladin version now point to a specific Aladin-lite version instead of the latest available version

## [0.2.6]

### Fixed

- fix deprecated npm_install jupyter module and replaced by hatch_jupyter_builder.npm_builder

### Changed

- The corresponding Aladin-lite version is now pinned instead of pointing to the latest version.
- There is no dependency to jquery anymore

## [0.2.5]

### Fixed

- fix traitlet warning on unicode (issue #69)
- fix warning on version export in index.js

## [0.2.4]

### Fixed

- add_listener function had a bug introduced in precedent version

## [0.2.3]

### Changed

- ipywidgets >= 8.0.6 install dependency
- ipyaladin compatible jupyterlab 4 and python 3.11

## [0.2.2]

### Added

- the `height` parameter can now be called at instantiation to shape the ipyaladin widget
- there is now a right-click menu with the following options:
  - take snapshot
  - add
    - new image layer
    - new catalog layer
  - load local file
    - FITS Image
    - FITS MOC
    - VOTable
  - What is this?
  - HiPS2FITS cutout
  - Select sources
- the attribute "show_simbad_pointer_control" can now be set to `True` at the instantiation of the widget

### Fixed

- compatible with JupyterLab4
