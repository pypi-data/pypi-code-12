# -*- coding: utf-8 -*-
import wx


def first(*args):
    """return first not None argument or None"""
    for arg in args:
        if not arg is None:
            return arg
    return None

def settuple(t, index, value):
    l = list(t)
    l[index] = value
    return tuple(l)


class TreeCtrl(wx.TreeCtrl):
    """Special override of wxTreeCtrl providing TCommon oriented features.
    The idea beyond this specialization is to provide transparent integration
    of TCommon elements in the tree, hidding its characteristics."""
    def __init__(self, *args, **kwargs):
        """ __init__(self, Window parent, int id=-1, Point pos=DefaultPosition,
        Size size=DefaultSize, long style=TR_DEFAULT_STYLE,
        Validator validator=DefaultValidator,
         String name=TreeCtrlNameStr) -> TreeCtrl"""
        self._map = {}
        super(TreeCtrl, self).__init__(*args, **kwargs)


    def GetItemChildren(self, item=None, recursively=False):
        """ Return the children of item as a list. """
        if not item:
            item = self.GetRootItem()
            if not item:
                return []
        children = []
        child, cookie = self.GetFirstChild(item)
        while child:
            children.append(child)
            if recursively:
                children.extend(self.GetItemChildren(child, True))
            child, cookie = self.GetNextChild(item, cookie)
        return children

    def GetExpansionState(self):
        """ GetExpansionState() -> list of expanded items. Expanded items
        are coded as determined by the result of GetItemIdentity(item). """
        root = self.GetRootItem()
        if not root:
            return []
        if self.HasFlag(wx.TR_HIDE_ROOT):
            return self.GetExpansionStateOfChildren(root)
        else:
            return self.GetExpansionStateOfItem(root)

    def GetExpansionStateOfItem(self, item):
        """return a diccionary about expansion status"""
        if self.IsExpanded(item):
            return {'self': True, 'child': self.GetExpansionStateOfChildren(item)}
        else:
            return {'self': False}

    def GetExpansionStateOfChildren(self, item):
        """return an array with expansion status"""
        return [self.GetExpansionStateOfItem(child)
            for child in self.GetItemChildren(item)]

    def SetExpansionState(self, listOfExpandedItems):
        """ SetExpansionState(listOfExpandedItems). Expands all tree items
        whose identity, as determined by GetItemIdentity(item), is present
        in the list and collapses all other tree items. """
        root = self.GetRootItem()
        if not root:
            return
        if self.HasFlag(wx.TR_HIDE_ROOT):
            self.SetExpansionStateOfChildren(listOfExpandedItems, root)
        else:
            self.SetExpansionStateOfItem(listOfExpandedItems, root)

    def SetExpansionStateOfItem(self, listOfExpandedItems, item):
        """Recovers expansion status (temptative)"""
        if listOfExpandedItems['self']:
            self.Expand(item)
            self.SetExpansionStateOfChildren(listOfExpandedItems['child'], item)
        else:
            self.Collapse(item)

    def SetExpansionStateOfChildren(self, listOfExpandedItems, item):
        """Recovers expansion status (temptative)"""
        i = 0
        for child in self.GetItemChildren(item):
            if i > len(listOfExpandedItems):
                break
            self.SetExpansionStateOfItem(listOfExpandedItems[i], child)
            i = i + 1

    def __getargchoice__(self, argpos, name1, name2, sync, *args, **kwargs):
        """
        Follow the correct interpretation for some argument that must be
        eiter a treeid or a object, this method returns the pair (id, obj).
        The argpos is the postion of the argument when received in positional
        args, and name1, name2 are the optional names when it's a mapped kwarg.
        The sync argument do object matching, if possible, in dictionary.
        """
        if len(args) > argpos:
            unk = args[argpos]
        else:
            unk = kwargs.get(name1, kwargs.get(name2, None))
        if unk is None:
            return None, None
        if isinstance(unk, wx.TreeItemId):
            item = unk
            obj = None
            if sync:
                data = super(TreeCtrl, self).GetItemData(item)
                if data is not None:
                    obj = data.GetData()
        else:
            obj = unk
            item = self.__ref__(obj)
        return obj, item

    def __fer__(self, *args, **kwargs):
        """__fer__(self, TreeItemId item) -> object.
        Finds the object and returns it or None"""
        if len(args) > 0:
            item = args[0]
        else:
            item = kwargs.get('item', None)
        if item is None or not item.IsOk():
            return None
        data = super(TreeCtrl, self).GetItemData(item)
        if data is not None:
            obj = data.GetData()
            if self.__ref__(obj) == item:
                return obj
        return None

    def __ref__(self, *args, **kwargs):
        """Gets the tree reference for any object"""
        import model
        if len(args) > 0:
            obj = args[0]
        else:
            obj = kwargs.get('obj', None)
        if obj is not None:
            if isinstance(obj, model.TCommon):
                return self._map.get(obj._uid, None)
            else:
                return self._map.get(obj, None)
        return None

    def __addref__(self, obj, treeid):
        """Add a map inside """
        import model
        if isinstance(obj, model.TCommon):
            self._map[obj._uid] = treeid
        else:
            self._map[obj] = treeid

    def __subref__(self, obj):
        """Remove a object reference"""
        import model
        if isinstance(obj, model.TCommon):
            self._map.pop(obj._uid, False)
        else:
            self._map.pop(obj, False)

    def HoldsObject(self, obj):
        """HoldsObject(self, TCommon obj) -> boolean"""
        import model
        if obj is None:
            return False
        if isinstance(obj, model.TCommon):
            return obj._uid in self._map
        else:
            return obj in self._map

    def AddRoot(self, *args, **kwargs):
        """AddRoot(self, String text, int image=-1, int selectedImage=-1,
            {TreeItemData data=None|TCommon obj=None}) -> {TreeItemId |TCommon}"""
        if len(args) >= 1:
            nargs = ['image', 'selectedImage', 'data']
            for i in range(len(args) - 1):
                kwargs[nargs[i]] = args[i + 1]
            args = (args[0],)
        else:
            args = ('')
        unk = kwargs.get('data', kwargs.get('obj', None))
        obj = None
        data = None
        if unk is not None:
            if isinstance(unk, wx.TreeItemData):
                data = unk
            else:
                obj = unk
                data = wx.TreeItemData(obj)
        kwargs['data'] = data
        treeid = super(TreeCtrl, self).AddRoot(*args, **kwargs)
        if obj is None:
            return treeid
        self.__addref__(obj, treeid)
        return obj

    def AppendItem(self, *args, **kwargs):
        """AppendItem(self, {TreeItemId|TCommon} parent, String text,
        int image=-1, int selectedImage=-1,
        {TreeItemData data=None|TCommon obj=None}) -> TreeItemId"""
        pobj, parent = self.__getargchoice__(0, 'parent', 'parent', True,
            *args, **kwargs)
        if len(args) >= 2:
            nargs = ['image', 'selectedImage', 'data']
            for i in range(len(args) - 2):
                kwargs[nargs[i]] = args[i + 2]
            args = (parent, args[1])
        else:
            args = (parent, '')
        unk = kwargs.get('data', kwargs.get('obj', None))
        obj = None
        data = None
        if unk is not None:
            if isinstance(unk, wx.TreeItemData):
                data = unk
            else:
                obj = unk
                data = wx.TreeItemData(obj)
        kwargs['data'] = data
        treeid = super(TreeCtrl, self).AppendItem(*args, **kwargs)
        if obj is None:
            return treeid
        self.__addref__(obj, treeid)
        return obj

    def Collapse(self, *args, **kwargs):
        """Collapse(self, {TreeItemId item, TCommon obj})"""
        # we allow to collapse over obj
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).Collapse(item)

    def CollapseAllChildren(self, *args, **kwargs):
        """CollapseAllChildren(self, {TreeItemId item|TCommon obj})"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).CollapseAllChildren(item)

    def CollapseAndReset(self, *args, **kwargs):
        """CollapseAndReset(self, {TreeItemId item|TCommon obj})"""
        # This method is specially hard: we must travel over the
        # childrens for ensure unmap deleted childs
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).Collapse(item)
        while super(TreeCtrl, self).GetChildrenCount(item) > 0:
            child = super(TreeCtrl, self).GetFirstChild(item)
            self.Delete(child)
        self.__subref__(obj)

    def Delete(self, *args, **kwargs):
        """Delete(self, {TreeItemId item|TCommon obj})"""
        # we do it carefully. It's possible to use item instead of using
        # obj, so we must check the tree item data
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args,
            **kwargs)
        # delete childs first
        while super(TreeCtrl, self).GetChildrenCount(item) > 0:
            child = super(TreeCtrl, self).GetFirstChild(item)
            self.Delete(child)
        super(TreeCtrl, self).Delete(item)
        self.__subref__(obj)

    def DeleteAllItems(self, *args, **kwargs):
        """DeleteAllItems(self)"""
        self._map = {}
        super(TreeCtrl, self).DeleteAllItems()

    def DeleteChildren(self, *args, **kwargs):
        """DeleteChildren(self, {TreeItemId item|TCommon obj})"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        while super(TreeCtrl, self).GetChildrenCount(item) > 0:
            child = super(TreeCtrl, self).GetFirstChild(item)
            self.Delete(child)

    def EditLabel(self, *args, **kwargs):
        """EditLabel(self, {wxTreeItemId item|TCommon obj})"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).EditLabel(item)

    def EnsureVisible(self, *args, **kwargs):
        """EnsureVisible(self, {wxTreeItemId item|TCommon obj})"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).EnsureVisible(item)

    def Expand(self, *args, **kwargs):
        """Expand(self, {wxTreeItemId item|TCommon obj})"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).Expand(item)

    def ExpandAllChildren(self, *args, **kwargs):
        """ExpandAllChildren(self, {wxTreeItemId item|TCommon obj})"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).ExpandAllChildren(item)

    def GetBoundingRect(self, *args, **kwargs):
        """GetBoundingRect(self, {wxTreeItemId item|TCommon obj},
            bool textOnly=False) -> PyObject"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        return super(TreeCtrl, self).GetBoundingRect(*args, **kwargs)

    def GetChildrenCount(self, *args, **kwargs):
        """GetChildrenCount(self, {TreeItemId item|TCommon obj},
        bool recursively=True) -> size_t"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        return super(TreeCtrl, self).GetChildrenCount(*args, **kwargs)

    def GetFirstChild(self, *args, **kwargs):
        """GetFirstChild(self, {TreeItemId item|TCommon obj}) -> PyObject"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', False, *args, **kwargs)

        # the return in the original is a pair (treeid, cookie). We
        # will change this meaning for (obj, cookie) only when the
        # following conditions meets:
        # - the reference argument is an object rather than a item.
        # - the child has, itself an associated object
        # in other case, old result style will be used
        if obj is None:
            return super(TreeCtrl, self).GetFirstChild(item)
        citem, cookie = super(TreeCtrl, self).GetFirstChild(item)
        return first(self.__fer__(citem), citem), cookie

    def GetFirstVisibleItem(self, *args, **kwargs):
        """GetFirstVisibleItem(self) -> {TreeItemId|TCommon}"""
        item = super(TreeCtrl, self).GetFirstVisibleItem()
        return first(self.__fer__(item), item)

    def GetFocusedItem(self, *args, **kwargs):
        """GetFocusedItem(self) -> {TreeItemId|TCommon}"""
        item = super(TreeCtrl, self).GetFocusedItem()
        return first(self.__fer__(item), item)

    def GetItemBackgroundColour(self, *args, **kwargs):
        """GetItemBackgroundColour(self,
        {TreeItemId item|TCommon obj}) -> Colour"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).GetItemBackgroundColour(item)

    def GetItemFont(self, *args, **kwargs):
        """GetItemFont(self, {TreeItemId item|TCommon obj}) -> Font"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).GetItemFont(item)

    def GetItemImage(self, *args, **kwargs):
        """GetItemFont(self, {TreeItemId item|TCommon obj},
        int which=TreeItemIcon_Normal) -> Font"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        return super(TreeCtrl, self).GetItemImage(*args, **kwargs)

    def GetItemParent(self, *args, **kwargs):
        """GetItemParent(self, {TreeItemId item|TCommon obj})
        -> {TreeItemId|TCommon}"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if obj is None:
            return super(TreeCtrl, self).GetItemParent(item)
        #Ok, now, we attempt to extract parent object first
        pitem = super(TreeCtrl, self).GetItemParent(item)
        if not pitem.IsOk():
            return None
        return first(self.__fer__(pitem), pitem)

    def GetItemPyData(self, *args, **kwargs):
        """GetItemPyData(self, {TreeItemId item|TCommon obj) -> PyObject"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).GetItemPyData(item)

    def GetItemState(self, *args, **kwargs):
        """GetItemState(self, {TreeItemId item|TCommon obj}) -> int"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).GetItemState(item)

    def GetItemText(self, *args, **kwargs):
        """GetItemText(self, {TreeItemId item|TCommon obj}) -> int"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).GetItemText(item)

    def GetItemTextColour(self, *args, **kwargs):
        """GetItemText(self, {TreeItemId item|TCommon obj}) -> int"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).GetItemTextColour(item)

    def GetLastChild(self, *args, **kwargs):
        """GetLastChild(self, {TreeItemId item|TCommon obj})
        -> {TreeItemId|TCommon}"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, sync=False, **kwargs)
        if obj is None:
            return super(TreeCtrl, self).GetLastChild(item)
        citem = super(TreeCtrl, self).GetLastChild(item)
        return first(self.__fer__(citem), citem)

    def GetNextChild(self, *args, **kwargs):
        """GetNextChild(self, {TreeItemId item|TCommon obj},
        void cookie) -> PyObject"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        if obj is None:
            return super(TreeCtrl, self).GetNextChild(*args, **kwargs)
        citem, cookie = super(TreeCtrl, self).GetNextChild(
            *args, **kwargs)
        return first(self.__fer__(citem), citem), cookie

    def GetNextSibling(self, *args, **kwargs):
        """GetNextSibling(self, {TreeItemId item|TCommon obj})
            -> {TreeItemId|TCommon}"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, sync=False, **kwargs)
        citem = super(TreeCtrl, self).GetNextSibling(item)
        if obj is None:
            return citem
        return first(self.__fer__(citem), citem)

    def GetNextVisible(self, *args, **kwargs):
        """GetNextVisible(self, {TreeItemId item|TCommon obj})
        -> {TreeItemId|TCommon}"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, sync=False, **kwargs)
        citem = super(TreeCtrl, self).GetNextVisible(item)
        if obj is None:
            return citem
        return first(self.__fer__(citem), citem)

    def GetPrevSibling(self, *args, **kwargs):
        """GetPrevSibling(self, {TreeItemId item|TCommon obj})
            -> {TreeItemId|TCommon}"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, sync=False, **kwargs)
        citem = super(TreeCtrl, self).GetPrevSibling(item)
        if obj is None:
            return citem
        return first(self.__fer__(citem), citem)

    def GetPrevVisible(self, *args, **kwargs):
        """GetPrevVisible(self, {TreeItemId item|TCommon obj})
        -> {TreeItemId|TCommon}"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, sync=False, **kwargs)
        citem = super(TreeCtrl, self).GetPrevVisible(item)
        if obj is None:
            return citem
        return first(self.__fer__(citem), citem)

    def GetRootItem(self):
        """GetRootItem(self) -> {TreeItemId|TCommon}"""
        item = super(TreeCtrl, self).GetRootItem()
        return first(self.__fer__(item), item)

    def GetSelection(self):
        """GetSelection(self)-> {TreeItemId|TCommon}"""
        item = super(TreeCtrl, self).GetSelection()
        return first(self.__fer__(item), item)

    def HitTest(self, *args, **kwargs):
        """HitTest(Point point) -> {item, where)"""
        item, where = super(TreeCtrl, self).HitTest(*args, **kwargs)
        return first(self.__fer__(item), item), where

    def InsertItem(self, *args, **kwargs):
        """InsertItem(self, {TreeItemId|TCommon} parent,
            {TreeItemId idPrevious|TCommon objPrevious}, String text,
            int image=-1, int selectedImage=-1,
            {TreeItemData data|TComponen obj}= None)->{TreeItemId|TCommon}"""
        pobj, pitem = self.__getargchoice__(0, 'parent',
            'parent', True, *args, **kwargs)
        vobj, vitem = self.__getargchoice__(1, 'idPrevious',
            'objPrevious', True, *args, **kwargs)
        if len(args) >= 3:
            nargs = ['image', 'selectedImage', 'data']
            for i in range(len(args) - 3):
                kwargs[nargs[i]] = args[i + 3]
            args = (pitem, vitem, args[2])
        else:
            args = (pitem, vitem, '')
        unk = kwargs.get('data', kwargs.get('obj', None))
        obj = None
        data = None
        if unk is not None:
            if isinstance(unk, wx.TreeItemData):
                data = unk
            else:
                obj = unk
                data = wx.TreeItemData(obj)
        kwargs['data'] = data
        treeid = super(TreeCtrl, self).InsertItem(*args, **kwargs)
        if obj is None:
            return treeid
        self.__addref__(obj, treeid)
        return obj

    def InsertItemBefore(self, *args, **kwargs):
        """InsertItemBefore(self, {TreeItemId|TCommon} parent, size_t index, String text,
            int image=-1, int selectedImage=-1, {TreeItemData data|TComponen obj}= None)
            ->{TreeItemId|TCommon}"""
        pobj, pitem = self.__getargchoice__(0, 'parent', 'parent', True, *args, **kwargs)
        if len(args) >= 3:
            nargs = ['image', 'selectedImage', 'data']
            for i in range(len(args) - 3):
                kwargs[nargs[i]] = args[i + 3]
            args = (pitem, args[1], args[2])
        elif len(args) > 1:
            args = (pitem, args[1], 0)
        else:
            args = (pitem, '', 0)
        unk = kwargs.get('data', kwargs.get('obj', None))
        obj = None
        data = None
        if unk is not None:
            if isinstance(unk, wx.TreeItemData):
                data = unk
            else:
                obj = unk
                data = wx.TreeItemData(obj)
        kwargs['data'] = data
        item = super(TreeCtrl, self).InsertItemBefore(*args, **kwargs)
        if obj is None:
            return item
        self.__addref__(obj, item)
        return obj

    def IsBold(self, *args, **kwargs):
        """IsBold(self, {TreeItemId item|TCommon obj}) -> bool"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).IsBold(item)

    def IsEmpty(self, *args, **kwargs):
        """IsEmpty(self, {TreeItemId item|TCommon obj}) -> bool"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).IsEmpty(item)

    def IsExpanded(self, *args, **kwargs):
        """IsEmpty(self, {TreeItemId item|TCommon obj}) -> bool"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).IsExpanded(item)

    def IsSelected(self, *args, **kwargs):
        """IsSelected(self, {TreeItemId item|TCommon obj}) -> bool"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).IsSelected(item)

    def IsVisible(self, *args, **kwargs):
        """IsVisible(self, {TreeItemId item|TCommon obj}) -> bool"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).IsVisible(item)

    def ItemHasChildren(self, *args, **kwargs):
        """ItemHasChildren(self, {TreeItemId item|TCommon obj}) -> bool"""
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        return super(TreeCtrl, self).ItemHasChildren(item)

    def PrependItem(self, *args, **kwargs):
        """PrependItem(self, {TreeItemId|TCommon} parent, String text,
        int image=-1, int selectedImage=-1,
        {TreeItemData data=None|TCommon obj=None}) -> TreeItemId"""
        pobj, pitem = self.__getargchoice__(0, 'parent', 'parent', True, *args, **kwargs)
        if len(args) >= 2:
            nargs = ['image', 'selectedImage', 'data']
            for i in range(len(args) - 2):
                kwargs[nargs[i]] = args[i + 2]
            args = (pitem, args[1])
        else:
            args = (pitem, '')
        unk = kwargs.get('data', kwargs.get('obj', None))
        obj = None
        data = None
        if unk is not None:
            if isinstance(unk, wx.TreeItemData):
                data = unk
            else:
                obj = unk
                data = wx.TreeItemData(obj)
        kwargs['data'] = data
        item = super(TreeCtrl, self).PrependItem(*args, **kwargs)
        if obj is None:
            return item
        self.__addref__(obj, item)
        return obj

    def ScrollTo(self, *args, **kwargs):
        """ScrollTo(self, {TreeItemId item|TCommon obj}) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).ScrollTo(item)

    def SelectChildren(self, *args, **kwargs):
        """SelectChildren(self, {TreeItemId parent|TCommon obj}) """
        obj, parent = self.__getargchoice__(0, 'parent', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, parent)
        else:
            kwargs['parent'] = parent
        super(TreeCtrl, self).SelectChildren(*args, **kwargs)

    def SelectItem(self, *args, **kwargs):
        """SelectItem(self, {TreeItemId item|TCommon obj}, select=True) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SelectItem(*args, **kwargs)

    def SetFocusedItem(self, *args, **kwargs):
        """SetFocusedItem(self, {TreeItemId item|TCommon obj}) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).SetFocusedItem(item)

    def SetItemBackgroundColour(self, *args, **kwargs):
        """SetItemBackgroundColour(self, {TreeItemId item|TCommon obj}, Colour col) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SetItemBackgroundColour(*args, **kwargs)

    def SetItemBold(self, *args, **kwargs):
        """SetItemBold(self, {TreeItemId item|TCommon obj}, bool bold=True) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 1:
            kwargs['bold'] = bool(args[1])
        args = (item, )
        super(TreeCtrl, self).SetItemBold(*args, **kwargs)

    def SetItemDropHighlight(self, *args, **kwargs):
        """SetItemDropHighlight(self, {TreeItemId item|TCommon obj}, bool highlight=True) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SetItemDropHighlight(*args, **kwargs)

    def SetItemFont(self, *args, **kwargs):
        """SetItemFont(self, {TreeItemId item|TCommon obj}, Font font) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SetItemFont(*args, **kwargs)

    def SetItemHasChildren(self, *args, **kwargs):
        """SetItemHasChildren(self, {TreeItemId item|TCommon obj}, bool has=True) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SetItemHasChildren(*args, **kwargs)

    def SetItemImage(self, *args, **kwargs):
        """SetItemImage(self, {TreeItemId item|TCommon obj}, int wich=TreeItemIcon_Normal) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SetItemImage(*args, **kwargs)

    def SetItemState(self, *args, **kwargs):
        """SetItemState(self, {TreeItemId item|TCommon obj}, int state) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SetItemState(*args, **kwargs)

    def SetItemText(self, *args, **kwargs):
        """SetItemState(self, {TreeItemId item|TCommon obj}, String text) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SetItemText(*args, **kwargs)

    def SetItemTextColour(self, *args, **kwargs):
        """SetItemTextColour(self, {TreeItemId item|TCommon obj}, Colour col) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        if len(args) > 0:
            args = settuple(args, 0, item)
        else:
            kwargs['item'] = item
        super(TreeCtrl, self).SetItemTextColour(*args, **kwargs)

    def SortChildren(self, *args, **kwargs):
        """SortChildren(self, {TreeItemId item|TCommon obj}) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).SortChildren(item)

    def Toggle(self, *args, **kwargs):
        """Toggle(self, {TreeItemId item|TCommon obj}) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).Toggle(item)

    def ToggleItemSelection(self, *args, **kwargs):
        """ToggleItemSelection(self, {TreeItemId item|TCommon obj}) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).ToggleItemSelection(item)

    def UnselectItem(self, *args, **kwargs):
        """UnselectItem(self, {TreeItemId item|TCommon obj}) """
        obj, item = self.__getargchoice__(0, 'item', 'obj', True, *args, **kwargs)
        super(TreeCtrl, self).UnselectItem(item)
