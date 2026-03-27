
/^<component class="sector" macro=/ {
    match($0, /^<component class="sector" macro="([^"]*)"/, m)
    sector = m[1]
}
/^<resourceareas>/ {
    minable = 1
}
/^<area id=/ {
    if ($minable) {
        match($0, /^<area id=.*yieldid="([^"]*)"/, m)
        field_count[m[1]]++
    }
}
/^<\/resourceareas/ {
    print sector
    for(field in field_count) {
        print "\t" field,  field_count[field]
    }
    minable = 0
    delete field_count
}