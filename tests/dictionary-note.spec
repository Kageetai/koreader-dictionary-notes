-- Contract checks with stand-ins for KOReader's device-dependent UI.
-- Catches lost selections, duplicate highlights, and dictionary-only lookups.
local Dictionary = {}
function Dictionary:init() self._dict_buttons = {} end
function Dictionary:addToDictButtons(spec) self._dict_buttons[spec.id] = spec end
package.loaded['apps/reader/modules/readerdictionary'] = Dictionary
package.loaded.gettext = function(s) return s end
package.loaded['ui/size'] = {border = {window = 1}, padding = {default = 2}}
local button_config
G_reader_settings = {}
function G_reader_settings:readSetting(key)
    assert(key == 'dict_button_config')
    return button_config
end
local Lookup = {}
function Lookup:buildButtonLayout() return self.rows end
package.loaded['ui/widget/dictquicklookup'] = Lookup
local patch = io.open('2-dictionary-add-note.lua', 'r')
if patch then patch:close(); dofile('2-dictionary-add-note.lua') end
local dict = setmetatable({}, { __index = Dictionary })
dict:init()
local action = dict._dict_buttons.dictionary_add_note
assert(action, 'Add note action must be registered')
assert(not action.conditional and action.menu_text == 'Note',
    'Note must be registered for KOReader sorting and toggling')
local selection = { text = 'word', pos0 = 'start', pos1 = 'end' }
local notes, saves = {}, 0
local highlight = { selected_text = selection }
function highlight:saveHighlight(extend)
    assert(not extend, 'Must preserve the exact word')
    assert(self.selected_text == selection, 'Selection must survive closing dictionary')
    saves = saves + 1
    return 7
end
function highlight:clear() self.selected_text = nil end
function highlight:editNote(index, new)
    assert(self.selected_text == nil, 'Temporary selection must be cleared')
    notes[#notes + 1] = {index, new}
end
local popup = { highlight = highlight, save_highlight = true }
function popup:isDocless() return false end
function popup:onClose(no_clear)
    self.closed = true
    if self.save_highlight then self.highlight:saveHighlight(); self.highlight:clear()
    elseif not no_clear then self.highlight:clear() end
end
assert(action.show_func(popup))
local function checkInline(rows, want_rows, want_position)
    local layout = setmetatable({rows = rows, width = 500}, {__index = Lookup}):buildButtonLayout()
    assert(#layout == want_rows, 'Must remove the separate Add note row')
    assert(layout[1][want_position].id == 'dictionary_add_note', 'Add note must follow Highlight')
end
checkInline({{{id='prev_dict'}, {id='highlight'}, {id='next_dict'}}, {{id='close'}}, {{id='dictionary_add_note'}}}, 2, 3)
checkInline({{{id='search'}, {id='highlight'}}, {{id='dictionary_add_note'}, {id='other_plugin'}}}, 2, 3)
-- Other plugins retain their rows, with and without Add note present.
local xray = {id='xray_lookup', callback=function() return 'original action' end}
local layout = setmetatable({rows={{{id='wikipedia'}, {id='search'}, {id='close'}}, {xray}}, width=500}, {__index=Lookup}):buildButtonLayout()
assert(#layout == 2 and layout[2][1] == xray, 'Keep the standalone X-Ray row')
assert(xray.callback() == 'original action', 'Preserve the X-Ray action')
local legacy = {text='X-Ray'}
local other = {id='other_plugin'}
local mixed = setmetatable({rows={{{id='highlight'}}, {{id='wikipedia'}, {id='search'}}, {other, legacy}, {{id='dictionary_add_note'}}}, width=500}, {__index=Lookup}):buildButtonLayout()
assert(#mixed == 3 and mixed[1][2].id == 'dictionary_add_note', 'Keep Add note inline')
assert(mixed[3][1] == other and mixed[3][2] == legacy and #mixed[2] == 2, 'Preserve other plugin positions')
button_config = {layout = {{'dictionary_add_note', 'highlight', 'next_dict', 'prev_dict'}}}
local custom_rows = {{{id='dictionary_add_note'}, {id='highlight'}, {id='next_dict'}, {id='prev_dict'}}}
local custom = setmetatable({rows=custom_rows, width=500}, {__index=Lookup}):buildButtonLayout()
assert(#custom == 1 and #custom[1] == 4 and custom[1][1].id == 'dictionary_add_note'
    and custom[1][2].id == 'highlight', 'Honor the saved Note position')
assert(custom[1][3].width == nil and custom[1][4].width == nil,
    'Leave custom layout widths to KOReader')
local disabled_rows = {{{id='highlight'}, xray}}
local disabled = setmetatable({rows=disabled_rows, width=500}, {__index=Lookup}):buildButtonLayout()
assert(#disabled == 1 and #disabled[1] == 2 and disabled[1][2] == xray,
    'Do not reinsert a disabled Note button')
button_config = nil
action.callback(popup)
assert(popup.closed and saves == 1, 'Create exactly one highlight')
assert(#notes == 1 and notes[1][1] == 7 and notes[1][2] == true, 'Edit new highlight note')
assert(not action.show_func(popup), 'Hide once selection is gone')
assert(not action.show_func({isDocless = function() return true end}))
assert(not action.show_func({isDocless = function() return false end}))
action.callback({isDocless = function() return true end})
assert(saves == 1, 'Invalid lookups must not create highlights')
print('PASS: sortable Note registration, default placement, custom placement, disabled Note, unchanged plugin rows, exact selection, single save, note editor, invalid lookups')
