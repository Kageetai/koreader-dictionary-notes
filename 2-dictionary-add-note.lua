-- Add a book annotation from the dictionary popup.
-- Requires ReaderDictionary:addToDictButtons (modern KOReader).
local ReaderDictionary = require("apps/reader/modules/readerdictionary")
local DictQuickLookup = require("ui/widget/dictquicklookup")
local Size = require("ui/size")
local _ = require("gettext")

assert(type(ReaderDictionary.addToDictButtons) == "function",
    "Dictionary Add note patch requires a newer KOReader version")

local function hasSelection(popup)
    if popup.is_wiki or popup:isDocless() then return false end
    local highlight = popup.highlight
    local selected = highlight and highlight.selected_text
    return selected ~= nil and selected.pos0 ~= nil and selected.pos1 ~= nil
end

-- Keep Add note beside Highlight without rearranging other plugins.
local original_build = DictQuickLookup.buildButtonLayout
function DictQuickLookup:buildButtonLayout(...)
    local rows = original_build(self, ...)
    local anchor_row, anchor_column, action_row, action_column
    for r, row in ipairs(rows) do
        for c, button in ipairs(row) do
            if button.id == "highlight" then
                anchor_row, anchor_column = r, c
            elseif button.id == "dictionary_add_note" then
                action_row, action_column = r, c
            end
        end
    end
    if not anchor_row or not action_row then return rows end
    local target = rows[anchor_row]
    local source = rows[action_row]
    local action = table.remove(source, action_column)
    if source == target and action_column < anchor_column then
        anchor_column = anchor_column - 1
    end
    table.insert(target, anchor_column + 1, action)
    if source ~= target and #source == 0 then table.remove(rows, action_row) end
    -- Leave most of a standard four-button row to the two text actions.
    if target and #target == 4 then
        local prev, next_button
        for _, button in ipairs(target) do
            if button.id == "prev_dict" then prev = button end
            if button.id == "next_dict" then next_button = button end
        end
        if prev and next_button then
            local width = self.width - 2 * Size.border.window - 2 * Size.padding.default
            prev.width = math.floor(width * 0.15)
            next_button.width = prev.width
        end
    end
    return rows
end

local original_init = ReaderDictionary.init
function ReaderDictionary:init(...)
    original_init(self, ...)
    self:addToDictButtons({
        id = "dictionary_add_note",
        text = _("Add note"),
        -- A contextual row also appears with existing customized layouts.
        conditional = true,
        show_func = hasSelection,
        callback = function(popup)
            if not hasSelection(popup) then return end
            local highlight = popup.highlight
            -- Highlight normally saves on popup close. Let this action save
            -- once, retaining the book selection until it has been saved.
            popup.save_highlight = false
            popup:onClose(true)
            local index = highlight:saveHighlight()
            highlight:clear()
            if index then
                highlight:editNote(index, true)
            end
        end,
    })
end
