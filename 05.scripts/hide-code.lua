-- Drops echoed source code and printed console output from a render, keeping figures, tables and prose.
-- Used for the review copy only: quarto render manuscript-jars.qmd --to docx --output manuscript-jars-2026-11-06.docx --lua-filter ../05.scripts/hide-code.lua
function CodeBlock(el)
  if el.classes:includes("cell-code") then return {} end
end

function Div(el)
  if el.classes:includes("cell-output-stdout") or el.classes:includes("cell-output-stderr") then return {} end
end
