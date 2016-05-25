'''
Created on 22 Jan 2016

@author: steve
'''
#Graph module
from pylab import * #@UnusedWildImport
import matplotlib.pyplot as plt # @Reimport


def den_plot(x_ref, 
        y_fwd_smoothed, y_rvs_smoothed, nt, fileFig, 
        fileName, onscreen, x_label, plot_ylim, pub = False):
    """
    TODO: add y_lim adjustment
    Single sRNA length den map plot:
    x-axis - reference
    y-axis - RPMR
    21,22,24 nt plots in default colours
    """
    plt.plot(x_ref,y_fwd_smoothed, color=nt_colour(nt), 
             label='{0} nt'.format(nt))
    plt.plot(x_ref,y_rvs_smoothed, color=nt_colour(nt))
    axhline(y=0)
    if pub:
        plt.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='on',      # ticks along the bottom edge are off
        top='off',
        right='on',
        left='on',         # ticks along the top edge are off
        labelbottom='off',
        labelleft = 'off',
        labelright = 'off',
        labelsize=15) # labels along the bottom edge are off
        clear_frame() 
    else:
        xlabel(x_label)
        ylabel('Reads per million reads')
        plt.legend(loc='upper left',borderaxespad=0)
    if plot_ylim !=0:
        ylim(-plot_ylim, plot_ylim)
    fig1 = plt.gcf()
    if onscreen:
        plt.show()
    if fileFig:
        fig1.savefig(fileName, format='pdf')
    plt.close(fig1)


def den_multi_plot_3(x_ref, 
        y_fwd_smoothed_21, y_rvs_smoothed_21, 
        y_fwd_smoothed_22, y_rvs_smoothed_22, 
        y_fwd_smoothed_24, y_rvs_smoothed_24, fileFig,
        fileName, onscreen, x_label, plot_y_lim,
        pub = False):
    
    """
    21,22 and 24 nt sRNA length den map plot:
    x-axis - reference
    y-axis - RPMR
    21,22,24 nt plots in default colours
    """

    plt.plot(x_ref,y_fwd_smoothed_21, color='#00CC00',label='21 nt')
    plt.plot(x_ref,y_rvs_smoothed_21, color='#00CC00')
    plt.plot(x_ref,y_fwd_smoothed_22, color='#FF3399', label='22 nt')
    plt.plot(x_ref,y_rvs_smoothed_22, color='#FF3399')
    plt.plot(x_ref,y_fwd_smoothed_24, color='#3333FF', label='24 nt')
    plt.plot(x_ref,y_rvs_smoothed_24, color='#3333FF')
    axhline(y=0)
    if pub:
        plt.tick_params(
            axis='both',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='on',      # ticks along the bottom edge are off
            top='off',
            right='on',
            left='on',         # ticks along the top edge are off
            labelbottom='off',
            labelleft = 'off',
            labelright = 'off',
            labelsize=15) # labels along the bottom edge are off
        clear_frame() 

    else:     #no_publication
        xlabel(x_label)
        ylabel('Reads per million reads')
        plt.rc('font',family='Arial')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=3, mode="expand", borderaxespad=0., fontsize=12)   
    if plot_y_lim !=0:
        ylim(-plot_y_lim, plot_y_lim)
    fig1 = plt.gcf()
    
    if onscreen:
        plt.show()
    if fileFig:
        fig1.savefig(fileName, format='pdf')
    plt.close(fig1)


def cdp_plot(counts_by_ref, seq1, seq2, nt, onscreen, fileFig, fileName, pub):
    """
    Scatter plot of alignments to references
    x-axis: seq1 reads aligned to reference
    y-axis: seq2 reads aligned to reference
    """
    
    results_list=[]
    for counts in counts_by_ref.itervalues():
        results_list.append((counts[0]+0.01, counts[1]+0.01))
 
    results_list=sorted(results_list)
  
    _max=max(results_list[-1][0], results_list[-1][1])+100
     
    plt.scatter(*zip(*results_list), 
                s=10, 
                color = nt_colour(nt) , 
                marker = 'o',
                label = "{0} nt".format(nt))
     
    arrow(0.1,0.1,_max,_max, color = 'r')
    xscale('log')
    yscale('log')
    xlim(0.1,_max)
    ylim(0.1,_max)
    if pub:
        plt.tick_params(
            axis='both',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='on',      # ticks along the bottom edge are off
            top='off',
            right='on',
            left='on',         # ticks along the top edge are off
            labelbottom='off',
            labelleft = 'off',
            labelright = 'off',
            labelsize=15) # labels along the bottom edge are off
        clear_frame() 
    else:
        plt.legend(loc='upper left',borderaxespad=0)
        xlabel(seq1)
        ylabel(seq2)
    fig1 = plt.gcf()
    if onscreen:
        plt.show()
    if fileFig:
        fig1.savefig(fileName, format='pdf')
    plt.close(fig1)

def clear_frame(ax=None):
    """
    Removes frame for publishing plots
    """ 
    if ax is None: 
        ax = plt.gca() 
    ax.xaxis.set_visible(True) 
    ax.yaxis.set_visible(True) 
    for spine in ax.spines.itervalues(): 
        spine.set_visible(False) 

def nt_colour(nt):
    """
    Set default colours for 21, 22 and 24 nt sRNAs
    """
    if nt==21:
        col = '#00CC00'
    elif nt ==22:
        col = '#FF3399'
    elif nt ==24:
        col = '#3333FF'
    else:
        col = 'black'
    return col







