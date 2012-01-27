#!/usr/bin/python

"""
A minimal front end to the Docutils Publisher, producing DOT files
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description

from docutils.writers import Writer
from docutils import nodes

class DotTranslator(nodes.GenericNodeVisitor):
    def __init__(self, document):
        self.edges = []
        nodes.GenericNodeVisitor.__init__(self, document)

    def default_visit(self, node):
        pass

    def default_departure(self, node):
        pass

    def visit_title(self, node):
        if "->" in node.astext():
            edge = [c for c in node.children if isinstance(c, nodes.reference)]
            if len(edge) == 2:
                self.edges.append(edge)

    def astext(self):
        edge_statements = []
        for n1, n2 in self.edges:
            n1 = n1.get('refid')
            n2 = n2.get('refid')
            edge_statements.append("\"%s\" -> \"%s\";" % (n1, n2))

        return """digraph {
%(edge_statements)s
}
""" % dict(edge_statements="\n".join(edge_statements))

    def visit_reference(self, node):
        return
        if "->" in node.astext():
            print node, node.parent

class DotWriter(Writer):
    def __init__(self):
        Writer.__init__(self)
        self.translator_class = DotTranslator

    def translate(self):
        vistor = self.translator_class(self.document)
        self.document.walkabout(vistor)
        self.output = vistor.astext()


description = ('Generates DOT files from standalone reStructuredText '
                        'sources.  ' + default_description)
publish_cmdline(writer=DotWriter(), description=description)
