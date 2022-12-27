from html import *

TITLE = 'YouFace'
SUBTITLE = "A billion dollars and it's yours!"
STYLESHEET = '/youface.css'
LINKLIST = [('http://cit.cs.dixie.edu/cs/1410/', 'CS 1410'), \
  ('http://new.dixie.edu/reg/syllabus/', 'College calendar'),]

class Form(BlockContainer):
    def __init__(self, action):
        BlockContainer.__init__(self, 'form')
        self.addAttr('method', 'post')
        self.addAttr('action', action)

class Label(Container):
    def __init__(self, forAttr):
        Container.__init__(self, 'label')
        self.addAttr('for', forAttr)

class Input(Tag):
    def __init__(self, inputType, name, value=None):
        Tag.__init__(self, 'input')
        self.addAttr('type', inputType)
        self.addAttr('name', name)
        if value:
            self.addAttr('value', value)

class Box(Div):
    def __init__(self, title):
        Div.__init__(self)
        self.addClass('box')
        titleTag = H(1)
        titleTag.addText(title)
        self.addTag(titleTag)

class StatusBox(Box):
    def __init__(self, userName):
        Box.__init__(self, 'Welcome, ' + userName)
        p1 = P()
        p1.addTag(Label('status').addText('Change your status:'))
        p1.addTag(Input('text', 'status'))
        p2 = P()
        p2.addTag(Input('submit', 'change', 'Change'))
        self.addTag(Form('/status').addTag(p1).addTag(p2))

class RecentActivityBox(Box):
    def __init__(self, activities):
        Box.__init__(self, 'Recent status updates')
        activityList = Ul()
        for a in activities:
            activityList.addTag(Li().addText(str(a)))
        self.addTag(activityList)

class UnFriendBox(Box):
    def __init__(self, friendName):
        Box.__init__(self, 'You are currently friends with ' + friendName)
        f = Form('/unfriend')
        f.addTag(Input('hidden', 'name', friendName))
        p = P()
        p.addTag(Input('submit', 'unfriend', 'Unfriend'))
        f.addTag(p)
        self.addTag(P().addTag(f))

class LoginBox(Box):
    def __init__(self):
        Box.__init__(self, 'Login')
        p1 = P()
        p1.addTag(Label('name').addText('Name:'))
        p1.addTag(Input('text', 'name'))
        p2 = P()
        p2.addTag(Label('password').addText('Password:'))
        p2.addTag(Input('password', 'password'))
        p3 = P()
        p3.addTag(Input('submit', 'type', 'Login'))
        p3.addTag(Input('submit', 'type', 'Create'))
        p3.addTag(Input('submit', 'type', 'Delete'))
        self.addTag(Form('/login').addTag(p1).addTag(p2).addTag(p3))

class Gadget(Div):
    def __init__(self, title):
        Div.__init__(self)
        self.addClass('gadget')
        self.addTag(H(1).addText(title))

class LinksGadget(Gadget):
    def __init__(self, links=LINKLIST):
        Gadget.__init__(self, 'Links')
        linkList = Ul()
        for link in links:
            linkList.addTag(Li().addTag(A(link[0]).addText(str(link[1]))))
        self.addTag(linkList)

class FriendsGadget(Gadget):
    def __init__(self, friends):
        Gadget.__init__(self, 'Friends')
        friendList = Ul()
        for name in friends:
            listItem = Li().addTag(A('/friend/' + name).addText(name))
            friendList.addTag(listItem)
        self.addTag(friendList)
        p = P()
        p.addTag(Input('text', 'name'))
        p.addTag(Input('submit', 'addfriend', 'Add Friend'))
        self.addTag(Form('/addfriend').addTag(p))

class LogoutGadget(Gadget):
    def __init__(self):
        Gadget.__init__(self, 'Logout')
        p = P().addTag(Input('submit', 'logout', 'Logout'))
        self.addTag(Form('/logout').addTag(p))

class Page:
    def __init__(self):
        self.boxList = []
        self.gadgetList = []
        self.head = Head().addTag(Meta()).addTag(Title().addText(TITLE))
        self.head.addTag(Stylesheet(STYLESHEET))
        self.header = Div().setId('header')
        self.header.addTag(H(1).addTag(A('/').addText(TITLE)))
        self.header.addTag(H(2).addText(SUBTITLE))

    def addBox(self, box):
        self.boxList.append(box)
        return self

    def addGadget(self, gadget):
        self.gadgetList.append(gadget)
        return self

    def __str__(self):
        mainColumn = Div().setId('maincolumn')
        for b in self.boxList:
            mainColumn.addTag(b)
        sidebar = Div().setId('sidebar')
        for g in self.gadgetList:
            sidebar.addTag(g)
        mainContainer = Div().setId('maincontainer').addTag(self.header)
        mainContainer.addTag(mainColumn).addTag(sidebar)
        body = Body().addTag(mainContainer)
        html = Html().addTag(self.head).addTag(body)
        return str(html)

    def __repr__(self):
        return self.__str__()

class LoginPage(Page):
    def __init__(self, linkList=LINKLIST):
        Page.__init__(self)
        self.addBox(LoginBox()).addGadget(LinksGadget(linkList))

class UserPage(Page):
    def __init__(self, friends, linkList=LINKLIST):
        Page.__init__(self)
        self.addGadget(LogoutGadget()).addGadget(FriendsGadget(friends))
        self.addGadget(LinksGadget(linkList))

class FeedPage(UserPage):
    def __init__(self, name, recentStatusUpdates, friends):
        UserPage.__init__(self, friends)
        self.addBox(StatusBox(name))
        self.addBox(RecentActivityBox(recentStatusUpdates))

class FriendPage(UserPage):
    def __init__(self, name, recentStatusUpdates, friends):
        UserPage.__init__(self, friends)
        self.addBox(UnFriendBox(name))
        self.addBox(RecentActivityBox(recentStatusUpdates))

def main():
    print 'page.py'

if __name__ == '__main__':
    main()
