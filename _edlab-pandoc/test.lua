-- box-filter.lua
function Para(el)
    -- Verifica se o parágrafo contém um RawInline com <box>
    local has_box = false
    local content = {}
    
    for _, item in pairs(el.content) do
        if item.t == "RawInline" and item.format == "html" and item.text:match("^<box>") then
            has_box = true
        elseif item.t == "RawInline" and item.format == "html" and item.text:match("</box>$") then
            -- ignora a tag de fechamento
        else
            if item.t == "Str" then
                table.insert(content, item.text)
            elseif item.t == "Space" then
                table.insert(content, " ")
            end
        end
    end
    
    if has_box then
        -- Junta todo o conteúdo em uma string
        local content_str = table.concat(content, "")
        
        -- Remove espaços extras e quebras de linha
        content_str = content_str:gsub("^%s+", ""):gsub("%s+$", "")
        
        -- Retorna o ambiente LaTeX com a formatação desejada
        return pandoc.RawBlock("latex", "\\begin{box}\n" .. content_str .. "\n\\end{box}")
    end
    
    return el
end