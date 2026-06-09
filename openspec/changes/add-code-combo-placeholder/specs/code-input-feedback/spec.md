## ADDED Requirements

### Requirement: Placeholder text in code selector
The system SHALL display the placeholder text "Selecione o código" in code selector fields (origin and destination) when they are empty.

#### Scenario: Placeholder appears when empty
- **WHEN** the code selector field is empty and has no current text
- **THEN** the placeholder "Selecione o código" is displayed in gray

#### Scenario: Placeholder hides on input
- **WHEN** the user types a character or selects a value from the dropdown
- **THEN** the placeholder text disappears and the selected/typed value is shown

### Requirement: Dropdown state indicator arrow
The system SHALL display a visual arrow indicator next to code selector fields that changes based on dropdown state.

#### Scenario: Arrow shows closed state
- **WHEN** the dropdown menu is closed
- **THEN** a downward-pointing arrow (▾) is displayed in the field's trailing area in gray (#56616D)

#### Scenario: Arrow shows open state
- **WHEN** the dropdown menu is open
- **THEN** the arrow points upward (▴) in gray (#56616D)

#### Scenario: Arrow hides on selection
- **WHEN** the user closes the dropdown by selecting a value or clicking elsewhere
- **THEN** the arrow returns to downward (▾) state

### Requirement: Code selector remains editable
The system SHALL maintain the existing edit capability of code selectors (users can type or select).

#### Scenario: User can type custom code
- **WHEN** user types characters in the code selector field
- **THEN** text is entered without auto-inserting from dropdown (NoInsert policy)

#### Scenario: User can select from dropdown
- **WHEN** user clicks the dropdown or field
- **THEN** the list of available codes appears and user can select one
