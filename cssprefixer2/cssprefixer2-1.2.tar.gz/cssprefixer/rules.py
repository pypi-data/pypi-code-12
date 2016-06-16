def cssReplaceBase(style, vendors=None, base=True, own=True): 
    if not vendors: vendors=[]
    if base:
        vendors += ['moz', 'webkit']
    result = [['-%s-%s'%(vendor, style[0]), style[1]] for vendor in sorted(vendors)]

    if own: result+=[style]
    return result

def cssReplaceFull(style):
    return cssReplaceBase(style, ['o', 'ms'])

def cssReplaceBaseIE(style):
    return cssReplaceBase(style, ['ms'])

def cssReplaceBaseOpera(style):
    return cssReplaceBase(style, ['o'])

def cssReplaceIE(style):
    return cssReplaceBase(style, ['ms'], False)

def cssReplaceOpera(style):
    return cssReplaceBase(style, ['o'], False)

def cssReplaceOperaIE(style):
    return cssReplaceBase(style, ['o', 'ms'], False)

def cssReplaceWebkit(style):
    return cssReplaceBase(style, ['webkit'], False)

def cssReplaceMoz(style):
    return cssReplaceBase(style, ['moz'], False)

def cssReplaceDisplay(style):
    ### flexbox legacy & stuff
    if style[1]=='flex':
        return map(lambda x:['display',x], [
            '-webkit-box',      # OLD: iOS6-, Safari 3.1-6
            '-moz-box',         # OLD: Firefox 19-
            '-ms-flexbox',      # IE:  IE10
            '-webkit-flex',     # NEW: Chrome
            'flex'              # NEW: Opera 12.1, Firefox 20+
        ])
    else:
        return [style]

def cssReplaceFlex(style):
    ### flex-basis
    vals = style[1].split(' ')
    result = []
    if len(vals)==3:
        result.append(['width', vals[2]])
    
    ### legacy replacment
    result += map(lambda x:[x, style[1]], [
        '-webkit-box-flex',     # OLD: iOS6-, Safari 3.1-6
        '-moz-box-flex',        # OLD: Firefox 19-
        '-ms-flex',             # IE:  IE10
        '-webkit-flex',         # NEW: Chrome
        'flex'                  # NEW: Opera 12.1, Firefox 20+
    ])

    return result

def cssReplaceFlexOrder(style):
    ### legacy replacement
    return  map(lambda x:[x, style[1]], [
        '-webkit-box-ordinal-group',    # OLD: iOS6-, Safari 3.1-6
        '-moz-box-ordinal-group',       # OLD: Firefox 19-
        '-ms-flex-order',               # IE:  IE10
        '-webkit-flex-order',           # NEW: Chrome
        'order'                         # NEW: Opera 12.1, Firefox 20+
    ])

def cssReplaceFlexItems(style):
    ### for flex-start and flex-end
    old = style[1]
    if old.count('-'): old = old.split('-')[1]

    result = cssReplaceBase(['box-align', old], own=False)
    result += [['-ms-flex-align', old]]
    result += cssReplaceWebkit(style)
    
    return result

def cssReplaceFlexItem(style):
    ### for flex-start and flex-end
    old = style[1]
    if old.count('-'): old = old.split('-')[1]

    result = cssReplaceBase(['box-item-align', old], own=False)
    result += [['-ms-flex-item-align', old]]
    result += cssReplaceWebkit(style)
    
    return result

def cssReplaceFlexJustify(style):
    ### for flex-start and flex-end
    old = style[1]
    if old.startswith('flex'): old = old.split('-')[1]

    ### old and mid for space-between & space-around
    mid = old
    if old=='space-around': mid = 'distribute'
    if old.startswith('space'): old = 'justify'

    result = cssReplaceBase(['box-pack', old], own=False)
    result += [['-ms-flex-pack', mid]]
    result += cssReplaceWebkit(style)
    
    return result

def cssReplaceFlexDirection(style):
    ### old
    direction = style[1].split('-')
    if(direction[0]=='row'):
        old = 'horizontal'
    elif(direction[0]=='column'):
        old = 'vertical'
    else:
        raise ValueError('flex direction value wrong')

    reverse = 'normal'
    if len(direction)>1:
        reverse = 'reverse'

    result = cssReplaceBase(['box-direction', reverse], own=False)
    result += cssReplaceBase(['box-orient', old], own=False)
    
    ### new
    result += cssReplaceBase(style, ['ms', 'webkit'], base=False)
    return result

def cssReplaceFlexWrap(style):
    return cssReplaceBase(style, ['ms', 'webkit'], base=False)

def cssReplaceFlexFlow(style): 
    vals = style[1].split(' ')
    direction = vals[0]
    result = cssReplaceFlexDirection(['flex-direction', direction])
    
    if len(vals)>1:
        result += cssReplaceFlexWrap(['flex-wrap', vals[1]])
    return result

def cssReplaceFlexContent(style):
    ### for flex-start and flex-end
    old = style[1]
    if old.startswith('flex'): old = old.split('-')[1]

    ### old and mid for space-between & space-around
    mid = old
    if old=='space-around': old = 'distribute'
    elif old=='space-between': old = 'justify'

    result = [['-ms-flex-line-pack', old]]
    result += cssReplaceWebkit(style)
    
    return result

### linear gradient
def cssReplaceGradient(style):
    olds = {
        'right': 'left',
        'left': 'right',
        'top': 'bottom',
        'bottom': 'top'
    }
    old = 'left'
    for key in olds.keys():
        if key in style[1]:
            old = olds[key]
    
    oldvars = 'linear-gradient(%s,'%old+','.join(style[1].split(',')[1:])
    result = map(lambda x:['background',x], ['-%s-%s'%(i, oldvars) for i in ['moz','webkit']])
    result += [style]
    
    return result

def cssReplaceBackground(style):
    if 'gradient' in style[1]:
        return cssReplaceGradient(style)
    
    return [style]

def cssReplaceTextAlign(style):
    if 'center' in style[1]:
        return map(lambda x:['text-align', x+'center'], ['', '-moz-', '-webkit-'])

    return [style]

rules = {
    ### copy from cssprefixer
    'border-radius': cssReplaceBase,
    'border-image': cssReplaceFull,
    'box-shadow': cssReplaceFull, 
   	'box-sizing': cssReplaceMoz,
    'box-orient': cssReplaceBaseIE,
    'box-direction': cssReplaceBaseIE,
    'box-ordinal-group': cssReplaceBaseIE,
    'box-align': cssReplaceBaseIE,
    'box-flex': cssReplaceBaseIE,
    'box-flex-group': cssReplaceBase,
    'box-pack': cssReplaceBaseIE,
    'box-lines': cssReplaceBaseIE,
    'user-select': cssReplaceBase,
    'user-modify': cssReplaceBase,
    'margin-start': cssReplaceBase,
    'margin-end': cssReplaceBase,
    'padding-start': cssReplaceBase,
    'padding-end': cssReplaceBase,
    'column-count': cssReplaceBase,
    'column-gap': cssReplaceBase,
    'column-rule': cssReplaceBase,
    'column-rule-color': cssReplaceBase,
    'column-rule-style': cssReplaceBase,
    'column-rule-width': cssReplaceBase,
    'column-span': cssReplaceWebkit,
    'column-width': cssReplaceBase,
    'columns': cssReplaceWebkit,
    
    'background':cssReplaceBackground,
    'background-clip': cssReplaceWebkit,
    'background-origin': cssReplaceWebkit,
    'background-size': cssReplaceWebkit, 
    
    'text-align': cssReplaceTextAlign,
	'text-overflow': cssReplaceOperaIE,
	'appearance': cssReplaceWebkit,
    'hyphens': cssReplaceBase,	

	'transition': cssReplaceFull,
    'transition-delay': cssReplaceBaseOpera,
    'transition-duration': cssReplaceBaseOpera,
    'transition-property': cssReplaceFull,
    'transition-timing-function': cssReplaceBaseOpera,
    'transform': cssReplaceFull,
    'transform-origin': cssReplaceFull,	
 
    #flexbox
    'display': cssReplaceDisplay,
    'flex':cssReplaceFlex,
    'align-items':cssReplaceFlexItems,
    'align-self':cssReplaceFlexItem,
    'justify-content':cssReplaceFlexJustify,
    'order':cssReplaceFlexOrder,
    'flex-direction':cssReplaceFlexDirection,
    'flex-wrap':cssReplaceFlexWrap,
    'flex-flow':cssReplaceFlexFlow,
    'align-content':cssReplaceFlexContent
}

def process(style):
    func = rules.get(style[0])
    if not func:
        return [style]
    else:
        return func(style)
