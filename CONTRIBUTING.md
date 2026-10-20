# Contributing

Thank you for helping. Small, focused changes are easiest to review.

* **Bug reports**: use the issue template and include your device, Android version and the launcher version (About screen or
  release tag). A screenshot helps a lot for layout problems.
* **Ideas**: open an issue before a big change.
* **Code**: the scripts patch Copper's files, so test with the workflow (push to your fork and watch the run). A script must fail
  with a clear message when the text it patches is missing. Keep each script's header comment accurate.
* **Translations**: Arabic text for strings Copper does not translate is in `copper-custom/translate_ar.py`. Keep placeholders
  (`%s`, `%1$d`) exactly as in English; the script checks them.
* **Licensing**: by contributing you agree that your contribution is released under the LGPL-3.0, like the rest of the project.
  Do not add code or files you do not have the right to share, and do not add anything that helps run Minecraft without a license.
