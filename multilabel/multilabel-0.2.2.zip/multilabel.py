
# coding: utf-8

# In[1]:

def multilabel(axes, current_tick_variable, new_variables, titles=[], label_format='%.2f', time_format='%H:%M'):
    
    for var in new_variables:
        if len(var) != len(current_tick_variable):
            raise(ValueError('All variables must be the same length'))
    
    import bisect as bi
    from matplotlib import dates
    from datetime import datetime
    
##### convert datetimes to easier to use numbers
    if isinstance(current_tick_variable[0], datetime):
        current_tick_variable = dates.date2num(current_tick_variable)
    
    newlabs = []
    
##### for each already created xticklabel, find the corresponding
##### values in the requested new label variables, and create
##### new labels with new lines separating them
##### if a variable is in datetime format, convert it to a string
##### with the given time_format
##### or else format the variable into a string
##### with the given label_format
    
    for label, tick in zip(axes.get_xticklabels(), axes.get_xticks()):
        idx = bi.bisect(current_tick_variable, tick)
        if idx == len(current_tick_variable):
            idx = idx - 1
        if isinstance(new_variables[0][idx], datetime):
            newlabel = new_variables[0][idx].strftime(time_format)
        else:
            newlabel = new_variables[0][idx]
        for var in new_variables[1:]:
            if isinstance(var[idx], datetime):
                newlabel = newlabel + '\n' + var[idx].strftime(time_format)
            else:
                newlabel = newlabel + '\n' + label_format%var[idx]
        newlabs.append(newlabel)
    axes.set_xticklabels(newlabs)

##### if label titles are requested
    if titles:
        
######### draw the canvas, so that we can find where the labels were drawn
        axes.get_figure().canvas.draw()
        
######### get the renderer instance to reference later
        renderer = axes.get_renderer_cache()
    
######### find the first non-blank label
        for u in axes.get_xticklabels():
            if u.get_text != '':
                t = u
                break

######### the transform allows us to convert axes coordinates 
#########to data coordinates
        transform = t.get_transform()

######### now we do the conversion and get the data coordinates
######### of the first label
        pos = transform.inverted().transform(t.get_window_extent(renderer=renderer))
        
######### if the left edge of the left-most label is left of the
######### left edge of the axes,
######### offset the right edge of the labels to slightly
######### left of the labels
######### or else, just put the right edge of the titles at the 
######### left edge of the axes
        if pos[0, 0] <= axes.get_xlim()[0]:
            right = 2*pos[0, 0]-axes.get_xlim()[0]
        else:
            right = axes.get_xlim()[0]
            
######### line up the top of the titles with the top of the labels
        top = pos[1, 1]
    
######### match the title font style with the label font style
        props = dict((p, getattr(t, 'get_' + p)()) for p in
             ['color', 'family', 'size', 'style', 'variant', 'weight'])
    
######### create the title text
        title = titles[0]
        for ti in titles[1:]:
            title = title + '\n' + ti

######### return the newly created title text instance
        return axes.text(right, top, title, transform=transform,
                       ha='right', va='top', **props)    

##### if no titles were requested, just return true
    else: 
        return True

