# BlockComet Engine (recipe)

A game engine editor based on [Godot Engine](https://godotengine.org) (MIT) with a different look and layout:
dark grey panels with a blue selection, thin borders, compact spacing, the *Project* (file system) panel at the bottom next to
Output and the debugger, scene tree on the left and inspector on the right, and BlockComet branding.

This branch holds only a **recipe**. `.github/workflows/godot.yml` downloads Godot at the tag in `GODOT_TAG`, applies
`godot-custom/apply.py` (each replacement checks that the text it changes exists), builds the editor with SCons and takes
screenshots of it in a virtual screen. Not affiliated with the Godot Foundation; "Godot" is their trademark.
Godot's license (MIT) is kept in the built editor (Help → About → License).
