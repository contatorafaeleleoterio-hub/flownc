## 1. Implement CodeCombo class

- [ ] 1.1 Add imports to compositor.py: `QStyle`, `QStyleOptionComboBox`, `QColor`, `QPainter`
- [ ] 1.2 Create `CodeCombo(QComboBox)` subclass with `__init__`, `showPopup`, `hidePopup` methods
- [ ] 1.3 Implement placeholder via `lineEdit().setPlaceholderText("Selecione o código")`
- [ ] 1.4 Add `_popup_open` state tracking in showPopup/hidePopup
- [ ] 1.5 Implement `paintEvent()` with QPainter to draw arrow (▾/▴) in gray (#56616D)

## 2. Update code combo factory

- [ ] 2.1 Simplify `_make_code_combo()` to return `CodeCombo()` only
- [ ] 2.2 Verify no changes needed in calling code (signals, usage remain same)

## 3. Update stylesheet

- [ ] 3.1 Add `QComboBox#CodeCombo::down-arrow { image: none; }` to style.qss to hide native arrow

## 4. Testing

- [ ] 4.1 Run pytest (expect 146 green) — `python -m pytest flownc/tests/test_ui_smoke.py -q`
- [ ] 4.2 Launch app and verify placeholder in `cb_origem` when empty
- [ ] 4.3 Launch app and verify placeholder in `cb_destino` when empty
- [ ] 4.4 Click origin combo and verify arrow changes to ▴
- [ ] 4.5 Click origin combo again and verify arrow returns to ▾
- [ ] 4.6 Type in origin combo and verify placeholder disappears
- [ ] 4.7 Select value from origin dropdown and verify placeholder disappears
- [ ] 4.8 Repeat 4.4–4.7 for destination combo
- [ ] 4.9 Compare visual result with mockup reference `mockups/painel-final.v2.html`
