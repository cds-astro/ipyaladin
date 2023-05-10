# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Memo on sections

* **Added** for new features.
* **Changed** for changes in existing functionality.
* **Deprecated** for soon-to-be removed features.
* **Removed** for now removed features.
* **Fixed** for any bug fixes.
* **Security** in case of vulnerabilities.

## [unreleased]

### Added

* there is now a right-click menu with the following options:
  * take snapshot
  * add
    * new image layer
    * new catalog layer
  *  load local file
     * FITS Image
     * FITS MOC
     * VOTable
  * What is this?
  * HiPS2FITS cutout
  * Select sources
![image](https://github.com/cds-astro/ipyaladin/assets/16650466/8cd78b68-6634-4f24-ad9b-27e7dc02ba48)
* the attribute "show_simbad_pointer_control" can now be set to `True` at the instantiation of the widget
