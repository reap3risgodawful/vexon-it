# Wi-Fi versus internet

Original caption-led networking explainer. The supplied `landscape.mp4` is 46 seconds, 1920 × 1080, 30 fps. It includes silent audio; the on-screen captions carry the explanation.

## Inspect

- `caption-script.json`: visible copy and timing.
- `landscape-source.py`: exact source snapshot used for the published landscape export.
- `vertical-source.py`: exact source snapshot used for the separately composed portrait export.
- `episode.py`: final source, with the portrait layout corrections included.
- `verification.json`: original export hashes, dimensions, frame counts, codecs, full-decode results and renderer image digest.

The two source snapshots differ because the portrait layout was refined after the landscape render. The published landscape video matches its recorded source and file hash. Source or encoder changes may produce a different file hash.

## Reproduce the animation

Requires Python, Manim 0.21.0, its NumPy/Pango/FFmpeg dependencies, and DejaVu Sans. The original render used the pinned Manim container digest recorded in `verification.json`. Review and prepare dependencies in your own environment before running code.

```bash
python -m manim --fps 30 --disable_caching --media_dir ./output-landscape landscape-source.py WifiVsInternet
PORTRAIT=1 python -m manim --fps 30 --disable_caching --media_dir ./output-portrait vertical-source.py WifiVsInternet
```

These commands recreate the animation. The published delivery file additionally received a silent AAC track and faststart remux; that private production wrapper is not part of this source example. Inspect the metadata before treating a new render as upload-ready. No credentials, paid API or online asset retrieval is used by the scene source.

## Factual references

- [Microsoft: Wi-Fi connection troubleshooting](https://support.microsoft.com/en-us/windows/experience/connectivity-networking/fix-wi-fi-connection-issues-in-windows)
- [Apple: Wi-Fi troubleshooting](https://support.apple.com/en-gb/111786)
- [Google: troubleshoot connectivity](https://support.google.com/googlehome/answer/9239727?hl=en)

The diagrams simplify a typical network. They do not measure or diagnose a particular installation. Restoring mobile data after the comparison is included in the phone-specific instructions.

Original media and scene source are available here for portfolio inspection. Contact the owner for reuse or licensing; Manim and other third-party dependencies retain their licenses.
