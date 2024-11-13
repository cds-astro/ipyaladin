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

## [Unreleased]

### Fixed

- in `add_marker`, markers don't use the default icon anymore. Do
  `use_marker_default_icon = True` in `add_marker` to recover the previous
  behavior [#129]
- Fix wrapper `widget_should_be_loaded` that was over-writing the methods documentation
  [#130]

## [0.5.1]

### Changed

- DeprecationWarning messages now clearly say that the methods won't exist in v1.0.0

### Added

- it is now possible to extend the widget's height to 100% of its container. To do so,
  do `Aladin(height=-1)`. This is implemented to support use in dashboard
  applications, this cannot work in a notebook.

### Fixed

- remove `requests` from mandatory dependencies (accident in version 0.5.0)

## [0.5.0]

### Added

- Reading WCS and FOV from `wcs` and `fov_xy` properties (#96)
- FITS images can be added to the view with `ipyaladin.Aladin.add_fits`.
  The method accepts `astropy.io.fits.HDUList`, `pathlib.Path`, or `string` representing
  paths (#86)
- New `selection` method replaces `rectangular selection` and also has a circular
  selection option (#100)
- Selected sources are exported as an `astropy.Table` list in the property
  `selected_objects` (#100)
- new `get_view_as_fits` exports the view as a `astropy.io.fits.HDUList` (#98)
- new `save_view_as_image` saves the view as an image file (#108)
- Support planetary objects for ipyaladin targets (#103)
- new method `add_marker` to add marker(s) to the view (#111)

### Deprecated

- Deprecated `rectangular_selection` method in favor of `selection` (#100)

### Changed

- Upgrade Aladin Lite version to 3.5.1-beta
- instantiation options are now directly mirroring those of Aladin-Lite instead of being
  hand-picked for the widget. Any option in
  https://cds-astro.github.io/aladin-lite/global.html#AladinOptions will be accepted.

## [0.4.0]

### Added

- attribute `__aladin_lite_version__` added to point to the corresponding Aladin Lite released version
- Support for `astropy.coordinates.SkyCoord` for assigning and reading the `target` property (#80)
- Support for `astropy.coordinates.Angle` for reading the `fov` property (#83)
- Support for `regions.LineSkyRegion`, `regions.CircleSkyRegion`, `regions.EllipseSkyRegion`, `regions.PolygonSkyRegion`, `regions.RectangleSkyRegion`, `regions.Regions` with `add_graphic_overlay_from_region` (#88)

### Fixed

- `clicked_object` was not properly updated after a click
- Fix asynchronous update for the `target` property (#80)
- some options were not accepted in snake_case anymore in `add_moc` and in `add_catalog_from_url` (#82)

### Changed

- Change the jslink target trait from `target` to `shared_target` (#80)
- Change the jslink fov trait from `fov` to `shared_fov` (#83)
- Upgrade Aladin Lite version to 3.4.4-beta (#88)
- Add support for list of strings in `add_overlay_from_stcs` (#88)

### Deprecated

- Deprecate `add_overlay_from_stcs` in favor of `add_graphic_overlay_from_stcs` (#88)
- Deprecate the `add_listener` method for a preferred use of `set_listener` method (#82)

## [0.3.0]

### Changed

- The ipyaladin module is now built on anywidget (https://anywidget.dev/)
- Aladin instances now have a `clicked_object` attribute that contains the information of
  the last clicked object (ra, dec, and catalog content)
- Each ipyaladin version now point to a specific Aladin-lite version instead of the latest available version
- add_table takes new arguments (documented here https://cds-astro.github.io/aladin-lite/Catalog.Catalog.html)
- the new method `add_moc` can take mocpy.MOC objects, URLs, or the dictionary serialization of a MOC. This will replace `moc_from_URL` and `moc_from_dict` in the future.

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
