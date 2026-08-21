# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.3.6]

### Fixed

- Improve fallback and version compatibility in `transpose_im`:
  - Broaden exception handling from `NotImplementedError` to `Exception` to handle `OSError` caused by corrupted or truncated EXIF data.
  - Discard corrupted EXIF after fallback transpose to avoid double rotation from stale orientation tags.
  - Pillow 8 compatibility: replace `ExifTags.Base.Orientation` with constant `0x0112`; fall back from `Image.Transpose` to `Image` via `getattr`.
- Default to `JPEG` in `save_img_to_file` when `im.format` is empty, avoiding `AttributeError` when `fmt` is `None`.

## [1.3.5]

### Fixed

- Fix `NotImplementedError` when `ImageOps.exif_transpose` handles multistrip images.
  - Add `transpose_im` to encapsulate EXIF orientation transpose logic: prefer `exif_transpose`, fall back to manual Orientation tag handling.
  - Use `transpose_im` in both `pre_processing` and `ProcessorCtr.handle_img_actions`.

## [1.3.4]

### Added

- Support `animation` parameter to preserve animated frames.

### Fixed

- Adjust `ProcessorCtr.save_img_to_file` mode handling by format:
  - Fix typo in JPEG mode check: `"GBA"` → `"RGB"`.
  - Add mode handling for transparency to fix loss of transparency info for mode `P`.

## [1.3.3]

### Fixed

- Extend `blur` radius range from `[1, 50]` to `[1, 512]`.
- Fix JPEG save error for images with `mode=P` (JPEG only supports RGB and L).
- Fix `ImageFormat.WEBP` value; unify to uppercase `WEBP`.

## [1.3.2]

### Fixed

- Set `Image.MAX_IMAGE_PIXELS` so `PROCESSOR_MAX_PIXEL` takes effect.
- Fix typing declarations for `ImageFile` objects.

## [1.3.1]

### Fixed

- Fix function name `process_image_obj`.

## [1.3.0]

### Added

- Add `process_image_obj` to accept a Pillow `Image` object directly as input.

### Changed

- Remove image-save parameter keys from `OpAction` enum.
- Adjust parameter order in `process_image`; allow `out_path` to be `None` and pass through `kwargs` to `Image.save`.

## [1.2.4]

### Added

- Add `PROCESSOR_TEMP_DIR` setting for configurable temporary directory (e.g. `/dev/shm`).

### Fixed

- Parse file suffix from URL before saving downloaded temp file.

## [1.2.3]

### Fixed

- Handle case where `im.format` may be empty in `save_img_to_file`.

## [1.2.2]

### Changed

- Use `with` context manager for all `Image.open` calls to avoid memory leaks.
- Bump dependency to `py-enum>=2.1.1` to fix mypy enum checks.

### Fixed

- Fix `trans_uri_to_im` losing `info` when copying the image.

## [1.2.1]

### Fixed

- Fix handling of `p` in `merge` action; apply after `bg` is processed.
- Correct documentation.

## [1.2.0]

### Added

- Support URL-based image resources.

### Changed

- Rename `process_image_by_path` to `process_image`.
- Restrict input resources via settings when exposing processing parameters externally (no restrictions by default):
  - `PROCESSOR_WORKSPACES` — restrict filesystem paths (`startswith` match).
  - `PROCESSOR_ALLOW_DOMAINS` — restrict URL domains (`endswith` match).

## [1.1.0]

### Fixed

- Use `round` instead of `int` when computing pixel dimensions from ratios in `resize` and similar operations.

## [1.0.3]

### Fixed

- Remove dependency on `typing_extensions`.

## [1.0.1]

### Fixed

- Fix output file naming in the `img-processor` CLI.

## [1.0.0] - 2024-06-23

### Added

- Initial release.
