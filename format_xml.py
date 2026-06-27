import xml.dom.minidom

dom = xml.dom.minidom.parse('document_repo.xml')
pretty_xml = dom.toprettyxml()
with open('document_repo_pretty.xml', 'w', encoding='utf-8') as f:
    f.write(pretty_xml)
