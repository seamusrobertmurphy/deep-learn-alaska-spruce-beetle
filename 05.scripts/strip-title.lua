-- Drops the title from the document metadata at render time, so the title block written by hand on the first page, laid
-- out as Forestry's template asks (editorial office, 23 October 2026), is the only one in the output. The YAML title stays in
-- the file because the review-queries chunk checks every literature search term against the title and keywords.
function Meta(m)
  m.title = nil
  return m
end
