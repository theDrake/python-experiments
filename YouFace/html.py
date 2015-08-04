import cgi

class Tag:
    def __init__(self, name):
        self.name = name
        self.id = ''
        self.classes = []
        self.attributes = []

    def setId(self, id):
        self.id = id
        return self

    def addClass(self, className):
        self.classes.append(className)
        return self

    def addAttr(self, key, value):
        self.attributes.append((key, value))
        return self

    def attrs(self):
        s = ''
        if self.id:
            s += ' id="%s"' % (cgi.escape(self.id))
        if len(self.classes) > 0:
            s += ' class="'
            i = 0
            while i < len(self.classes):
                if i > 0:
                    s += ' '
                s += cgi.escape(self.classes[i])
                i += 1
            s += '"'
        for a in self.attributes:
            s += ' %s="%s"' % (cgi.escape(str(a[0])), cgi.escape(str(a[1])))
        return s

    def makeTag(self, contents):
        s = ''
        s += '<' + self.name + self.attrs()
        if contents:
            s += '>' + contents + '</' + self.name + '>'
        else:
            s += ' />'
        return s

    def __str__(self):
        return self.makeTag('')

    def __repr__(self):
        return self.__str__()

class BlockTag(Tag):
    def __init__(self, name):
        Tag.__init__(self, name)

    def __str__(self):
        s = Tag.__str__(self)
        if s:
            s = '\n' + s
        return s

class Container(Tag):
    def __init__(self, name):
        Tag.__init__(self, name)
        self.children = []

    def addTag(self, child):
        self.children.append(child)
        return self

    def addText(self, text):
        self.children.append(cgi.escape(text))
        return self

    def contents(self):
        s = ''
        for child in self.children:
            s += str(child)
        return s

    def __str__(self):
        return self.makeTag(self.contents())

class BlockContainer(Container):
    def __init__(self, name):
        Container.__init__(self, name)

    def __str__(self):
        s = self.contents()
        if s.startswith('\n') and not s.endswith('\n'):
            s += '\n'
        return '\n' + self.makeTag(s)

class Img(Tag):
    def __init__(self, src, alt):
        Tag.__init__(self, 'img')
        self.addAttr('src', src)
        self.addAttr('alt', alt)

class Meta(BlockTag):
    def __init__(self):
        BlockTag.__init__(self, 'meta')
        self.addAttr('http-equiv', 'content-type')
        self.addAttr('content', 'text/html; charset=utf-8')

class Stylesheet(BlockTag):
    def __init__(self, href, rel='stylesheet', ssType='text/css'):
        BlockTag.__init__(self, 'link')
        self.addAttr('rel', rel)
        self.addAttr('href', href)
        self.addAttr('type', ssType)

class Br(Tag):
    def __init__(self):
        Tag.__init__(self, 'br')

class Hr(Tag):
    def __init__(self):
        Tag.__init__(self, 'hr')

class A(Container):
    def __init__(self, href):
        Container.__init__(self, 'a')
        self.addAttr('href', href)

class Title(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'title')

class Div(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'div')

class Strong(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'strong')

class Em(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'em')

class P(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'p')

class H(BlockContainer):
    def __init__(self, num):
        num = int(num)
        if num < 1:
            num = 1
        elif num > 6:
            num = 6
        BlockContainer.__init__(self, 'h' + str(num))

class Ul(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'ul')

class Ol(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'ol')

class Li(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'li')

class Head(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'head')

class Body(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'body')

class Html(BlockContainer):
    def __init__(self):
        BlockContainer.__init__(self, 'html')

    def __str__(self):
        return '<!DOCTYPE html>' + BlockContainer.__str__(self)

def main():
    print 'hello'

if __name__ == '__main__':
    main()
