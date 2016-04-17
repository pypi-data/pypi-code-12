#!/usr/bin/env python
# -*- coding:utf-8 -*-
# (c)Ing. Zdenek Dlauhy, Michal Dlauhy, info@dlauhy.cz

class CabinetMakerBase(object):

    def add_area_array(self, area_id=None,diff=None,incremental_diff=None,move=None,number=None,pos=None,save=True,size=None):
        '''
        :param area_id: 1,2 id of area to insert shelve
        :type area_id: int or list
        :param pos: position of object ``[300,100,0]``
        :type pos: list
        :param size: size of object ``[100,100,33]``
        :type size: list
        :param number: number of elements to insert
        :type number: int
        :param move: move object by this distance 
        :type move: list
        :param incremental_diff: diff which is used to increment for next area
        :type incremental_diff: list
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_area_array', **_loc)


    def add_drawers(self, area_id=None,diff=None,drawer_type='AUTOMAT',grains=True,handle=True,info=None,mat=None,mat_front=None,number=None,pars_front=[3, 3, 3, 3, 3],pars_in=[12, 12, 0, 40, 10, 40],save=True):
        '''
        :param area_id: number of area into which insert another divider
        :type area_id: int or list
        :param number: number of drawers ``3`` or ``[1,100,1,300]`` combination of size >10 and ratio of remaining space
        :type number: int or list
        :param pars_in: 6 numbers defining inside gaps [left, right, bottom,top,bottom of fronts, top of fronts]
        :type pars_in: list
        :param pars_front: 5 numbers defining front gaps between fronts of drawers[left,right,bottom, top, between]
        :type pars_front: list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param drawer_type: overlay of front part
        :type drawer_type: string
        :param handle: True to insert handle element, False dont insert
        :type: handle: bool
        :param save: use if you want save a function
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict

        If drawer_type is set to OUTSIDE - front cover size will be increased in width
        and height by construction thickness in all directions. After this dimension
        change, pars_front parameters are applied to calculate front parts dimensions.

        TODO: add options for handles(now automatic - middle)
        TODO: new function for inside of drawer
        TODO: unite inside height and define inside height
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_drawers', **_loc)


    def add_area(self, area_id=None,diff=None,dims=True,name=None,pos=None,save=True,size=None,typ=None):
        '''
        :param area_id:
        :type area_id: int or list
        :param pos:
        :type pos: list
        :param size:
        :type size: list
        :param name:
        :type name: string
        :param dims: add dimension text info into drawing
        :type dims: boolean True/False
        :param save: save function
        :type save: boolean

        Adds numbered size specified area to product
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_area', **_loc)


    def add_del_element(self, index=None,save=True):
        '''
        :param index: element index in product to remove
        :type index: int or list

        set status DELETED for elements specified by their index
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_del_element', **_loc)


    def add_dividers(self, area_id=None,areas=True,array_dist=None,diff=None,info=None,mat=None,part=True,part_size=None,save=True,thickness=None,typ='B'):
        '''
        :param area_id: number of area into which insert another divider
        :type area_id: int or list
        :param part_size: None - size of inserted divider part ``[700,300,18]``
        :type part_size: list
        :param mat: None - code name of material in database ``H1032``, ``F509``
        :type mat: str
        :param part: True if divider part should be inserted, False not to insert False/True
        :type part: bool
        :param areas: True if new areas should be created on each side of divider part True/False, 0,1
        :type areas: bool or int
        :param typ: orientation of divider part A,B,C or direction in which to divide area X,Y,Z
        :type typ: str
        :param array_dist: size of subareas ``[1,2,600,200,50,1]``
            1,2..9 defines sizes of areas as ratio of remaining length to each other
            10.. is actual inner size of area desired
        :type array_dist: list of ints
        :param array_dist: equal division of area into specified number of subareas
        :type array_dist: int
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list

        function to create new division in product, which can then be
        used as space limiter of other functions.
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_dividers', **_loc)


    def add_side_left(self, area_id=None,diff=None,info=None,mat=None,pos=None,save=True,size=None):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]`` in self.divs
        :type area_id: int or list
        :param pos: inserts part to specified location ``[100,20,50]`` -
        :type pos: list
        :param size: part size ``[600,330,18]`` or thickness ``32``
        :type size: int or list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param mat: material id from database ``F509`` - open database library
        :type mat: str
        :param save: save function to data?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict

        Appends main side element to product, usefull for creation of main parts
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_side_left', **_loc)


    def add_diffs(self, area_id=None,diff=None,increase=True,revert_last=False,save=True):
        '''
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param revert_last: True if u want to revert previous change to diffs made by this function
        :type revert_last: bool
        :param area_id: area where to apply changes - 0 or [0,2,3]
        :type area_id: int or list
        :param save: True If you want to save function run
        :type save: bool

        Changes actual usable space for next funtions for whole product or specified area.
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_diffs', **_loc)


    def add_bar(self, area_id=None,bar_length='X',bar_width='Y',diff=None,diff_X=False,diff_Y=False,diff_Z=True,edge=None,grains=True,info=None,locations=[1, 2],mat=None,name=None,post_diff=None,save=True,size=70):
        '''
        :param area_id: id of area 0 or 2 or ``[1,2,3]`` to apply on multiple areas
        :type area_id: int or list
        :param locations: id of inserting corners 0,1,2,3, numbered from left-down-front corner ``[0,2]``
        :type locations: list
        :param bar_length: axis of length X,Y,Z
        :type bar_length: str
        :param size: width of bar 90, or [width, thickness]
        :type size: int or list
        :param bar_width: axis of width X,Y,Z not same as as bar_length
        :type bar_width: str
        :param mat: code of material U108
        :type mat: str
        :param diff_X: True to change available space after inserting part in X
        :type diff_X: bool
        :param diff_Y: True to change available space after inserting part in Y
        :type diff_Y: bool
        :param diff_Z: True to change available space after inserting part in Z
        :type diff_Z: bool
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param edge: edges used on element ``['Z','G','H','F']``
        :type edge: list
        :param save: Save function
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param post_diff: same as diff but affects only function after this one
        :type post_diff: list

        Function to create and insert bars, sockles and other types of variable emlements.
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_bar', **_loc)


    def add_element(self, area_id=None,diff=None,edge=None,info=None,joints=None,mat=None,name=None,number=None,pos=None,rot=None,save=True,shape_contour=None,size=None,size_override=False,typ=None):
        '''
        :param area_id: 1,2 id of area to insert shelve
        :type area_id: int or list
        :param pos: position of object ``[300,100,0]``
        :type pos: list
        :param size: size of object ``[100.100,33]``
        :type size: list
        :param typ: element type A,B or C
        :type typ: str
        :param mat: material name ``"H1111"``
        :type mat: str
        :param rot: rotation of element ``[10,15,30]``
        :type rot: list
        :param name: name of element
        :type name: str
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param edge: edges on element
        :type edge: list
        :param number: number of elements to insert
        :type number: int
        :param shape_contour: shape of element in list with data
        :type shape_contour: list
        :param joints: list of joints objects
        :type joints: list

        function specified for creating not standard elements. With this
        function you can usually creat almost any constructuion you would want.
        Usually you will have to specify position, size and probably also area_id
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_element', **_loc)


    def add_func_run(self, area_id=None,find=False,number=None,save=True):
        '''
        :param area_id: id of area 0 or 2 or ``[1,2,3]`` to apply on multiple areas
        :type area_id: int or list
        :param number: list of functions or index of functions ie ``[['add_bar',{}]]``
        :type number: list
        :param save: Save function
        :type save: bool
        :param find: find data in self.data_functions
        :type find: bool

        function to run other functions with diffrent area_id. Usefull to create
        and embed diffrent products inside diffrent one.
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_func_run', **_loc)


    def add_doors(self, area_id=None,diff=None,door_type='AUTOMAT',grains=True,handle=True,handleHeight='TOP',handleOrientation='VERTICAL',handlePos=[50, 50],handleSide=None,handleSize=[160, 25, 5],info=None,mat=None,number=None,pars_front=[3, 3, 3, 3, 3],post_diff=None,save=True,stacking='HORIZONTAL',style='FLAT'):
        '''
        :param area_id: 1,2 or ``[1,3,4]`` id of area to insert shelve
        :type area_id: int or list
        :param door_type: INSIDE/OUTSIDE/AUTOMAT - position of doors inside or outside of construciton
        :type door_type: str
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param pars_front: 5 numbers defining front gaps between fronts of drawers[left,right,bottom, top, between]
        :type pars_front: list
        :param number: number of doors
        :type number: int
        :param framed: 'FLAT' for flat doors, 'FRAMED' for framed construction
        :type framed: str
        :param stacking: Stacking of doors
        :type stacking: str
        :param mat: materiál DV ``'H1111'``
        :type mat: str
        :param handleOrientation: ``'VERTICAL'``/``'HORIZONTAL'``
        :type handleOrientation: str
        :param handleHeight: height of handle ``'TOP'``, ``'MID'``,``'DOWN'``
        :type handleHeight: str
        :param handleSide: handle position on side ``'LEFT'``, ``'RIGHT'``, ``'MID'``
        :type handleSide: str
        :param handlePos: position of hadle
        :type handlePos: list
        :param handleSize: velikost úchytky
        :type handleSize: list
        :param save: save function to save run or other more complex runs default True?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param post_diff: same as diff but affects only function after this one
        :type post_diff: list
        :param style: 'FLAT' or 'FRAMED' - using default sizes in product
        :type style: str

        Doors for product based on input variables and mainly area ID.
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_doors', **_loc)


    def add_back(self, area_id=None,diff=None,edge=None,info=None,mat=None,pos=None,save=True,size=None):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]`` in self.divs
        :type area_id: int or list
        :param size: part size ``[600,330,18]`` or thickness ``32``
        :type size: int
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param mat: material id from database ``F509`` - open database library
        :type mat: str
        :param save: save function to data?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param edge: set element edge like ``["X",0,0,0]``
        :type edge: list

        inserts back object into product
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_back', **_loc)


    def add_shelve(self, area_id=None,diff=None,info=None,mat=None,number=None,rotation=None,save=True,size=None):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]`` in self.divs
        :type area_id: int or list
        :param size: part size ``[600,330,18]`` or thickness 32
        :type size: int or list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param mat: material id from database ``F509`` - open database library
        :type mat: str
        :param save: save function to data?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param number: Number of shelves to create, or gaps between shelves
        :type number: int or list

        Appends main shelves to product, usefull for creation of main parts
        diff - no automatic diff after insertion
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_shelve', **_loc)


    def add_front(self, area_id=None,diff=None,edge=None,info=None,mat=None,pos=None,save=True,size=None):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]`` in self.divs
        :type area_id: int or list
        :param size: part size ``[600,330,18]`` or thickness ``32``
        :type size: int
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param mat: material id from database ``F509`` - open database library
        :type mat: str
        :param save: save function to data?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param edge: set element edge like ``["X",0,0,0]``
        :type edge: list

        inserts front object into product
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_front', **_loc)


    def add_socle(self, area_id=None,bottom=50,diff=[0, 0, 2, 10, 0, 0],info=None,insert_back=False,left=None,mat=None,order=[0, 1, 2, 3],right=None,save=True,top=None):
        '''
        :param area_id: number of area to insert socle - 0,1 or ``[0,1,2]`` for multiple areas
        :type area_id: int or list
        :param mat: code of material 'H1111'
        :type mat: str
        :param save: True
        :type save: bool
        :param bottom: width of bottom element 90
        :type bottom: int
        :param top: width of top element 80
        :type top: int
        :param left: width of left element 50
        :type left: int
        :param right: width of right element 60
        :type right: int
        :param order: numbered order in which to insert elements ``[left,right,bottom, top]``
        :type order: list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict

        By default adds bottom ``element(socle)`` into the construction, by filling in
        dimensions of other sides (left,right..) insert other distancing elements at
        given position.
        Applies only X and Z diffs, for advanced diffs use add_diffs.
        Descreases usable volume of product by width

        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_socle', **_loc)


    def add_label(self, area_id=None,center=True,height=35,pos=None,save=True,text=None):
        '''
        :param text: label text eg. ``Microwave``
        :type text: str
        :param area_id: id of area into which you want to place label
        :type area_id: int or list
        :param pos: XY pos - front view ``[50,60]``
        :type pos: list
        :param center: move text into the center of area True/False
        :type center: bool
        :param height: height of text
        :type height: int

        Function adds a text label into the FRONT view of this product drawing
        if both area_id and pos is filled in area_id returns center pos
        of chosen area and pos parameter is apllied afterwards.
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_label', **_loc)


    def add_frame(self, area_id=None,diff=None,diff_fill=[0, 0, 5, 0, 0, 0],diff_frame=None,edge_fill=None,edge_frame=None,info=None,info_fill=None,insert_fill=True,low_profile=True,mat=None,mat_fill=None,order=[0, 1, 2, 3],planes=None,post_diff=None,rotate_fill_diff=False,rotate_frame_diff=False,save=True,thick=None,thick_fill=None,width=None):
        '''
        :param area_id: id of area 0 or 2 or ``[1,2,3]`` to apply on multiple areas
        :type area_id: int or list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param planes: plane where to put frame
        :type planes: int or list
        :param mat: code of material U108
        :type mat: str
        :param mat_fill: code of fill material U108
        :type mat_fill: str
        :param insert_fill: code of fill material U108
        :type insert_fill: bool
        :param diff_fill: changes of space material inside frame [left,right, front,back, bottom, top]
        :type diff_fill: list
        :param diff_frame: changes of space material for frame [left,right, front,back, bottom, top]
        :type diff_frame: list
        :param low_profile: switch to low profile, usefull to create another type of frames
        :type low_profile: bool
        :param thick: thickness of profile
        :type thick: int
        :param width: width of profile
        :type width: int
        :param order: order of profiles put inside of frame
        :type frame_rotate_diff: bool
        :param frame_rotate_diff: if True diff applies for every plane in local coordinate system
        :type fill_rotate_diff: bool
        :param fill_rotate_diff: if True diff applies for every plane in local coordinate system
        :type order: list
        :param save: Save function
        :type save: bool
        :param post_diff: same as diff but affects only function after this one
        :type post_diff: list

        Inserts frame into the construction into specified plane of cube
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_frame', **_loc)


    def add_top(self, area_id=None,bars_width=None,diff=None,info=None,mat=None,pos=None,save=True,size=None):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]`` in self.divs
        :type area_id: int or list
        :param pos: inserts part to specified location ``[100,20,50]`` -
        :type pos: list
        :param size: part size ``[600,330,18]`` or thickness ``32``
        :type size: int or list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param mat: material id from database ``F509`` - open database library
        :type mat: str
        :param save: save function to data?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param bars_width: width of bars to replace Top element, 0 = False
        :type bars_width: int

        inserts top object into product or specified area id
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_top', **_loc)


    def add_basic(self, area_id=None,back=5,diff=None,info=None,save=True,socle=None,top_bars=None,variant='H'):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]``
        :type area_id: int or list
        :param back: use if you want to add backside
        :type back: int or False
        :param variant: order in which parts are inserted ``H``,``I``,``T``,``O``
        :type variant: str
        :param socle: number - height of socle ``125``, replace prod.socle parametr
        :type socle: int
        :param save: use if you want save a function
        :type save: bool
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param top_bars: insert width of top bars to replace Top element
        :type top_bars: int

        This function creates basic outer construction for product.
        Just shortcut function instead of adding sides, top and base or socle separetly.
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_basic', **_loc)


    def add_backside(self, area_id=None,diff=[-7, -7, 0, 0, -7, -7],edge=None,info=None,mat=None,planes=3,rotate_fill_diff=False,save=True,thickness=None):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]`` in self.divs
        :type area_id: int or list
        :param pos: inserts part to specified location ``[100,20,50]`` -
        :type pos: list
        :param thickness: backside thickness 5 or product defaults if None
        :type thickness: int or list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param mat: material id from database ``F509`` - open database library
        :type mat: str
        :param save: save function to data?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict
        :param edge: set element edge like ``["X",0,0,0]``
        :type edge: list

        Will create main back side element dpending of size
        post_diff - thickness of backside
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_backside', **_loc)


    def add_mod_element(self, elementEdge=None,elementInfo=None,elementMaterial=None,elementPosition=None,elementRotation=None,index=None,save=True,sizeLength=None,sizeThickness=None,sizeWidth=None):
        '''
        :param index: element index in product
        :type index: int or list
        :param elementPosition: element position ``[1,100,300]``
        :type elementPosition: list
        :param elementRotation: element rotation ``[30,0,0]``
        :type elementRotation: list
        :param elementMaterial: element material ``[True,'MAT1',True]``
        :type elementMaterial: list
        :param sizeWidth: element size ``600``
        :type sizeWidth: int
        :param sizeThickness: element thickness ``20``
        :type sizeThickness: int
        :param sizeLength: element length ``2000``
        :type sizeLength: int
        :param elementEdge: element edge ``['X',0,0,'A']``
        :type elementEdge: list
        :param elementInfo: element info dict ``{}``
        :type elementInfo: dict
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_mod_element', **_loc)


    def add_base(self, area_id=None,diff=None,info=None,mat=None,save=True,size=None):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]`` in self.divs
        :type area_id: int or list
        :param size: part size ``[600,330,18]`` or thickness ``32``
        :type size: int or list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param mat: material id from database ``F509`` - open database library
        :type mat: str
        :param save: save function to data?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict

        inserts bottom object into product
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_base', **_loc)


    def add_side_right(self, area_id=None,diff=None,info=None,mat=None,pos=None,save=True,size=None):
        '''
        :param area_id: area id number or list of numbers of areas 1 or ``[0,1]`` in self.divs
        :type area_id: int or list
        :param pos: inserts part to specified location ``[100,20,50]`` -
        :type pos: list
        :param size: part size ``[600,330,18]`` or thickness 32
        :type size: int or list
        :param diff: differences in axis ``[X left, X right, Y front, Y back, Z bottom, Z top]``
        :type diff: list
        :param mat: material id from database ``F509`` - open database library
        :type mat: str
        :param save: save function to data?
        :type save: bool
        :param info: element info object as ``{'fittings':{}, 'production':{},'visibility':'BACK'}``
        :type info: dict

        Appends main side element to product, usefull for creation of main parts
        '''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_side_right', **_loc)


    def add_empty(self, func_key='add_empty'):
        '''function which adds empty run function to data_functions whith custom parameters'''
        _loc = dict(locals())
        _loc.pop('self')
        self.custom_action(method='add_empty', **_loc)

