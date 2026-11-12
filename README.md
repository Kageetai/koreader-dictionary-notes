# KOReader Dictionary Notes

Add a note to a selected word directly from KOReader’s dictionary popup, and keep its actions in compact rows.

```text
◀◀        Highlight    Note    ▶▶
Wikipedia             Search      Close
```

The default layout places Note immediately after Highlight. Customized layouts use your chosen button order and visibility. Other plugins keep their own button positions.

## Features

- Note highlights the exact selected word and opens KOReader’s normal note editor.
- No need to tap Highlight first.
- Keeps Highlight and Note in the same default row, with smaller dictionary navigation buttons.
- Adds Note to KOReader’s **Sort and toggle buttons** settings.
- Preserves other plugin buttons and their callbacks.

## Requirements

- A recent KOReader version providing `ReaderDictionary:addToDictButtons` and `DictQuickLookup:buildButtonLayout`.
- On Android, the official **rocks** build. The F-Droid build disables user patches.
- Tested by a user on a Boox Palma 2. Other devices have not been tested.

Check **Help → Report a bug → Build flavor** in KOReader to identify the Android build. Opening this screen does not submit a report.

## Install manually

1. Download [2-dictionary-add-note.lua](https://raw.githubusercontent.com/Kageetai/koreader-dictionary-notes/main/2-dictionary-add-note.lua).
2. Put it in KOReader’s `patches` folder. On Android this is usually `Internal storage/koreader/patches`. Create the folder if needed.
3. Fully close KOReader and reopen it.
4. Long-press a word to open the dictionary, then tap **Note**.

To update, replace the existing file with the same filename and restart KOReader. To uninstall, delete the file and restart.

If you already customized dictionary buttons, enable **Note** under **Dictionary settings → Customize buttons → Sort and toggle buttons**. You can reorder it there and adjust **Max buttons in row** to put it in your preferred row.

## Storefront and App Store

This repository uses the `koreader-user-patch` topic for discovery by community stores. Search for **koreader-dictionary-notes** in the patches section after refreshing the catalog. Discovery depends on the store’s catalog rebuild and cache refresh; it is not immediate.

If your store supports installation by repository URL, use:

https://github.com/Kageetai/koreader-dictionary-notes

## Notes

- Note saves the highlight before opening the note editor; cancelling the editor leaves the highlight.
- The action is offered for selections in the book, not dictionary-only searches or Wikipedia popups.
- The standard layouts use four buttons per row. Custom layouts with more actions can become crowded.
- Other patches that replace dictionary layout methods may conflict.

## Development

Run `luajit tests/dictionary-note.spec` from the repository root. These contract checks use stand-ins for KOReader’s device-dependent UI; they do not replace on-device testing.

## License

MIT. See [LICENSE](LICENSE).
