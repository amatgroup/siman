# -*- coding: utf-8 -*- 
from __future__ import division, unicode_literals, absolute_import 
import sys

# import header
# from operator import itemgetter
# from classes import res_loop , add_loop
# from pairs import 
# from functions import image_distance, local_surrounding
# from chargeden.functions import chg_at_point, cal_chg_diff
# from dos.functions import plot_dos

# from ase.utils.eos import EquationOfState
import scipy
from scipy import interpolate
from scipy.interpolate import spline 
# print (scipy.__version__)
# print (dir(interpolate))
try:
    from scipy.interpolate import  CubicSpline
except:
    print('scipy.interpolate.CubicSpline is not avail')

import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import header
from header import print_and_log
from functions import write_xyz, replic


def plot_mep(atom_pos, mep_energies, image_name = None, show = None):
    """
    Used for NEB method
    atom_pos (list) - xcart positions of diffusing atom along the path,
    mep_energies (list) - full energies of the system corresponding to atom_pos
    """

    #Create
    atom_pos = np.array(atom_pos)
    data = atom_pos.T #
    tck, u= interpolate.splprep(data) #now we get all the knots and info about the interpolated spline
    path = interpolate.splev(np.linspace(0,1,500), tck) #increase the resolution by increasing the spacing, 500 in this example
    path = np.array(path)


    diffs = np.diff(path.T, axis = 0)
    path_length =  np.linalg.norm( diffs, axis = 1).sum()
    mep_pos =  np.array([p*path_length for p in u])


    if 0: #plot the path in 3d
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.plot(data[0], data[1], data[2], label='originalpoints', lw =2, c='Dodgerblue')
        ax.plot(path[0], path[1], path[2], label='fit', lw =2, c='red')
        ax.legend()
        plt.show()







    mine = min(mep_energies)
    eners = np.array(mep_energies)-mine

    
    
    xnew = np.linspace(0, path_length)

    # ynew = spline(mep_pos, eners, xnew )
    spl = CubicSpline(mep_pos, eners, bc_type = 'natural' )
    ynew = spl(xnew)

    #minimum now is always zero,
    spl_der = spl.derivative()

    mi = min(xnew)
    ma = max(xnew)
    r = spl_der.roots()
    r = r[ np.logical_and(mi<r, r<ma) ] # only roots inside the interval are interesting


    diff_barrier = max( spl(r) ) # the maximum value 
    print_and_log('plot_mep(): Diffusion barrier =',round(diff_barrier, 2),' eV', imp = 'y')
    # sys.exit()


    path2saved = fit_and_plot(orig = (mep_pos, eners, 'ro'), spline = (xnew, ynew, 'b-'), xlim = (-0.05, None  ),
    xlabel = 'Reaction coordinate ($\AA$)', ylabel = 'Energy (eV)', image_name =  image_name, show = show)


    return path2saved, diff_barrier




def fit_and_plot(power = None, xlabel = "xlabel", ylabel = "ylabel", image_name = None, show = None,
    xlim = None, ylim = None, title = None, figsize = None,
    xlog = False,ylog = False, scatter = False, legend = False, markersize = 10,  linewidth = 3, hor = False, fig_format = 'eps', dpi = 300,
    **data):
    """Should be used in two below sections!
    Creates one plot with two dependecies and fit them;
    return minimum fitted value of x2 and corresponding value of y2; 
    if name == "" image will not be plotted
    power - the power of polynom


    fig_format - format of saved file.
    dpi    - resolution of saved file

    data - each entry should be (X, Y, 'r-')
    """

    # print data


    if 1:

        
        plt.figure(figsize=figsize)
        if title: 
            plt.title(title)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)



        scatterpoints = 1
        for key in sorted(data):



            if scatter:
                
                plt.scatter(data[key][0], data[key][1],  s = data[key][2], c = data[key][-1], alpha = 0.8, label = key)
            else:

                try:
                    label = data[key][3]
                except:
                    label = key
                # print 'label is ', label

                plt.plot(data[key][0], data[key][1], data[key][2], linewidth = linewidth, label = label, markersize = markersize, alpha = 0.8)





        if hor: plt.axhline(color = 'k') #horizontal line

        plt.axvline(color='k')
        if xlim: 
            plt.xlim(xlim)
            # axes = plt.gca()
            # axes.set_xlim([xmin,xmax])
            # axes.set_ylim([ymin,ymax])
        if ylim:
            plt.ylim(ymin=ylim[0])
            if ylim[1]: plt.ylim(ymax=ylim[1])


        if power:
            for key in data:
                coeffs1 = np.polyfit(data[key][0], data[key][1], power)        
                
                fit_func1 = np.poly1d(coeffs1)
                x_range = np.linspace(min(data[key][0]), max(data[key][0]))
                fit_y1 = fit_func1(x_range); 
         
                plt.plot(x_range, fit_y1, data[key][-1][0], )

                # x_min  = fit_func2.deriv().r[power-2] #derivative of function and the second cooffecient is minimum value of x.
                # y_min  = fit_func2(x_min)
                slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(data[key][0], data[key][1])
                # print 'R^2 = ', r_value**2, key


        if xlog: plt.xscale('log')
        if ylog: 
            if "sym" in str(ylog):
                plt.yscale('symlog', linthreshx=0.1)
            else:
                plt.yscale('log')



        if legend: 
            plt.legend(loc = legend, scatterpoints = scatterpoints)


        plt.tight_layout()
        path2saved = ''
        if image_name:
            try:
                path_to_images
            except:
                path_to_images = ''
            

            if fig_format in image_name:
                path2saved = str(image_name)

            elif str(image_name).split('.')[-1] in ['eps', 'png', 'pdf']:
                path2saved = str(image_name)
                fig_format = str(image_name).split('.')[-1]

            else:
                path2saved = str(image_name)+'.'+fig_format
            


            plt.savefig(path2saved, dpi = dpi, format=fig_format)
            print_and_log("Image saved to ", path2saved)

            plt.clf()
            plt.close('all')
        elif show is None:
            show = True
        if show:
            plt.show()



    return path2saved


def plot_bar(xlabel = "xlabel", ylabel = "ylabel",
    xlim = None, ylim = None,
    image_name = None, title = None, bottom = 0.18, hspace = 0.15, barwidth = 0.2,
    data1 = [],data2 = [],data3 = [],data4 = [],
    **data):

    width = barwidth      # the width of the bars

    if data: 
        N = len(data.values()[0][0])
        key = data.keys()[0]
        xlabels = data[key][0]
        # print N
        ind = np.arange(N)  # the x locations for the groups
        shift = 0
        fig, ax = plt.subplots()
        for key in sorted(data):
            # print 'color', data[key][2]
            ax.bar(ind+shift, data[key][1], width, color = data[key][2], label = data[key][-1])# yerr=menStd)
            # print ind
            shift+=width

    elif data1 and data4:
        fig = plt.figure(figsize=(10,5))   #5:7 ratio for A4, 
        gs = gridspec.GridSpec(2, 2,
                               width_ratios =[5,1],
                               height_ratios=[1,1]
                               )
        gs.update(top=0.98, bottom=bottom, left=0.1, right=0.98, wspace=0.15, hspace=hspace)

        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        ax3 = plt.subplot(gs[2])
        ax4 = plt.subplot(gs[3])
        # fig, ax = plt.subplots()
        # fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col')#, sharey='row') equal

        for ax, data in (ax1, data1), (ax2,data2), (ax3,data3), (ax4, data4):
            N = len(data[0][0])
            xlabels = data[0][0]
            ind = np.arange(N)  # the x locations for the groups
            shift = 0

            for d in data:
                ax.bar(ind+shift, d[1], width, color = d[2], label = d[-1])# yerr=menStd)
                # print ind
                shift+=width

            ax.axhline(y=0, color='black')
            # ax.set_xticklabels(xlabels , rotation=70 )

            ax.set_xticks(ind+width)
    
        ax3.set_xticklabels(data3[0][0] , rotation=80 )
        ax4.set_xticklabels(data4[0][0] , rotation=80 )

        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
            
        ax3.set_ylabel(ylabel)
        ax3.yaxis.set_label_coords(-0.1, 1.1)
        # plt.ylabel(ylabel)

        ax1.legend(loc=2, )
        ax3.legend(loc=2, )
        # ax1.axis('tight')
        # ax2.axis('tight')
        # ax3.axis('tight')
        # ax4.axis('tight')
        ax1.margins(0.0, 0.2)
        ax2.margins(0.0, 0.2)
        ax3.margins(0.0, 0.2)
        ax4.margins(0.0, 0.2)





    elif data1 and data2 and not data4:
        fig = plt.figure(figsize=(10,5))   #5:7 ratio for A4, 
        gs = gridspec.GridSpec(1, 2,
                               width_ratios =[5,1],
                               height_ratios=[1,0]
                               )
        gs.update(top=0.95, bottom=bottom, left=0.1, right=0.98, wspace=0.15, hspace=hspace)

        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])

        for ax, data in (ax1, data1), (ax2,data2):
            N = len(data[0][0])
            xlabels = data[0][0]
            ind = np.arange(N)  # the x locations for the groups
            # print ind+width
            # print data[0][0]
            shift = 0.2

            for d in data:
                ax.bar(ind+shift, d[1], width, color = d[2], label = d[-1])# yerr=menStd)
                # print ind
                shift+=width

            ax.axhline(y=0, color='black')
            # ax.set_xticklabels(xlabels , rotation=70 )

            ax.set_xticks(ind+width+len(data)*width/2)
            
        names1 = [ n1  for n1, n2 in  zip( data1[0][0], data1[1][0] ) ] # 
        names2 = [ n1  for n1, n2 in  zip( data2[0][0], data2[1][0] ) ]

        ax1.set_xticklabels( names1, rotation = 80 ) # Names of configurations on x axis
        ax2.set_xticklabels( names2, rotation = 80 ) 

        ax1.set_ylabel(ylabel)

        ax1.legend(loc=2, )
        ax1.axis('tight')
        ax2.axis('tight')

    elif data1 and not data2:
        # fig = plt.figure(figsize=(10,5))   #5:7 ratio for A4, 
        gs = gridspec.GridSpec(1,2, width_ratios =[9,1],
                               height_ratios=[1,0])                               
        gs.update(top=0.95, bottom=bottom, left=0.1, right=0.98, wspace=0.15, hspace=hspace)

        ax1 = plt.subplot(gs[0])
        # ax2 = plt.subplot(gs[1])

        for ax, data in (ax1, data1),:
            N = len(data[0][0])
            xlabels = data[0][0]
            ind = np.arange(N)  # the x locations for the groups
            # print ind+width
            # print data[0][0]
            shift = 0.2

            for d in data:
                ax.bar(ind+shift, d[1], width, color = d[2], label = d[-1])# yerr=menStd)
                # print ind
                shift+=width

            ax.axhline(y=0, color='black')
            # ax.set_xticklabels(xlabels , rotation=70 )

            ax.set_xticks(ind+width+len(data)*width/2)
            
        names1 = [ n1 + '; ' + n2 for n1, n2 in  zip( data1[0][0], data1[1][0] ) ] # 

        ax1.set_xticklabels( names1, rotation = 80 ) # Names of configurations on x axis

        ax1.set_ylabel(ylabel)

        ax1.legend(loc=2, )
        ax1.axis('tight')
        # ax2.axis('tight')

    # ax.set_yscale('log')
    # plt.yscale('symlog', linthreshx=0.1)

    # ax.set_title('Scores by group and gender')


    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                    ha='center', va='bottom')

    # autolabel(rects1)
    # autolabel(rects2)


    # plt.axis('tight')
    # plt.margins(0.05, 0)

    # plt.tight_layout()
    # elif data1: gs.tight_layout(fig)

    if image_name:
        print_and_log( "Saving image ...", str(image_name), imp = 'y')
        plt.savefig(str(image_name)+'.png', dpi = 200, format='png')
    else:
        plt.show()

    return





def plot_and_annotate(power = 2, xlabel = "xlabel", ylabel = "ylabel", image_name = None,
    xlim = None, ylim = None, title = None, fit = None,
    legend = None, 
    **data):
    """Should be used in two below sections!
    Creates one plot with two dependecies and fit them;
    return minimum fitted value of x2 and corresponding valume of y2; 
    if name == "" image will not be plotted
    power - the power of polynom

    data - each entry should be (X, Y, 'r-')
    """

    # print data
    # coeffs1 = np.polyfit(x1, y1, power)        
    # coeffs2 = np.polyfit(x2, y2, power)
    
    # fit_func1 = np.poly1d(coeffs1)
    # fit_func2 = np.poly1d(coeffs2)
    
    #x_min  = fit_func2.deriv().r[power-2] #derivative of function and the second cooffecient is minimum value of x.
    #y_min  = fit_func2(x_min)
    
    if 1:
        # x_range = np.linspace(min(x2), max(x2))
        # fit_y1 = fit_func1(x_range); 
        # fit_y2 = fit_func2(x_range); 
        
        plt.figure()
        if title: plt.title(title)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        




        for key in data:
            plt.plot(data[key][0], data[key][1], data[key][-1], markersize = 15, label = key)
            
            for x, y, name in zip(data[key][0], data[key][1], data[key][2]): 
                xytext = (-20,20)
                if 'T1m' in name: xytext = (20,20)
                plt.annotate(name, xy=(x, y), xytext=xytext, 
                textcoords='offset points', ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5', 
                                color='red'))










        if fit:
            for key in data:

                f1 = interp1d(data[key][0], data[key][1], kind='cubic')
                x = np.linspace(data[key][0][0], data[key][0][-1], 100) 
                plt.plot(x, f1(x), '-', label = key+'fit')


        plt.axvline(color='k')
        if xlim: 
            plt.xlim(xlim)
            # axes = plt.gca()
            # axes.set_xlim([xmin,xmax])
            # axes.set_ylim([ymin,ymax])
        if ylim:
            plt.ylim(ymin=ylim[0])
            if ylim[1]: plt.ylim(ymax=ylim[1])


        # plt.plot(x2, y2, 'bo', label = 'r'   )
        # plt.plot(x_range, fit_y1, 'r-', label = 'init_fit')
        # plt.plot(x_range, fit_y2, 'b-', label = 'r_fit'   )



        plt.tight_layout()

        if legend: plt.legend(loc = 2)

        if image_name:
            # print "Saving image ..."
            if not os.path.exists('images/'):
                os.makedirs('images/')
            plt.savefig(str(image_name)+'.png', dpi = 300, format='png')
            plt.close()
        else:
            plt.show()


    return 


def plot_bar_simple(xlabel = "xlabel", ylabel = "ylabel",
    xlim = None, ylim = None,
    image_name = None, title = None, 
    data = []):

    width = 0.6       # the width of the bars



    plt.figure(figsize=(10,5))   #5:7 ratio for A4, 
    fig, ax = plt.subplots()


    N = len(data[0])
    xlabels = data[0]
    # print xlabels
    ind = np.arange(N)  # the x locations for the groups
    shift = 0
    # for d in data:
    d = data
    # print d[2]

    rects = ax.bar(ind+shift, d[1], width, color = d[2], label = d[-1],align="center" )# yerr=menStd)
    rects[0].set_color('g')
    rects[-1].set_color('g')
    # rects[1].set_color('b')

    # print ind
    shift+=width

    ax.axhline(y=0, color='black')

    ax.set_xticks(ind)#+width)
    ax.set_xticklabels(xlabels , rotation=50 )
        
    ax.set_ylabel(ylabel)
    
    handles, labels = ax.get_legend_handles_labels()
    import matplotlib.patches as mpatches
    red_patch = mpatches.Patch(color='red', label='Substitutional')
    ax.legend(handles+[red_patch], labels+['Substitutional'], loc = 4)
    # ax.legend(handles=[red_patch], loc = 8)
    

    # ax.legend(loc=2, )

    # ax.set_yscale('log')
    # plt.yscale('symlog', linthreshx=0.1)

    # ax.set_title('Scores by group and gender')
    if xlim: 
        plt.xlim(xlim)
        # axes = plt.gca()
        # axes.set_xlim([xmin,xmax])
        # axes.set_ylim([ymin,ymax])
    if ylim:
        plt.ylim(ymin=ylim[0])
        if ylim[1]: plt.ylim(ymax=ylim[1])

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., -1.05*height, '%.0f'%float(height),
                    ha='center', va='top')
    autolabel(rects)
    # autolabel(rects2)
    plt.tight_layout()

    if image_name:
        # print "Saving image ..."
        if not os.path.exists('images/'):
            os.makedirs('images/')
        plt.savefig('images/'+str(image_name)+'.png', dpi = 200, format='png')
        plt.close()
    else:
        plt.show()
    return








def plot_conv(list_of_calculations, calc, type_of_plot, conv_ext = [], labelnames = None):
    """
    Allows to fit and plot different properties;
    Input:
    'type_of_plot' - ("fit_gb_volume"-fits gb energies and volume and plot dependencies without relaxation and after it,
     )


    """

            
    def fit_and_plot(x1, y1, x2, y2, power, name = "", xlabel = "", ylabel = "", image_name = "test", lines = None):
        """Should be used in two below sections!
        Creates one plot with two dependecies and fit them;
        return minimum fitted value of x2 and corresponding valume of y2; 
        if name == "" image will not be plotted
        power - the power of polynom

        lines - add lines at x = 0 and y = 0

        """
        coeffs1 = np.polyfit(x1, y1, power)        
        coeffs2 = np.polyfit(x2, y2, power)
        
        fit_func1 = np.poly1d(coeffs1)
        fit_func2 = np.poly1d(coeffs2)
        
        #x_min  = fit_func2.deriv().r[power-2] #derivative of function and the second cooffecient is minimum value of x.
        #y_min  = fit_func2(x_min)
        
        if name:

            x_range = np.linspace(min(x2), max(x2))
            fit_y1 = fit_func1(x_range); 
            fit_y2 = fit_func2(x_range); 
            
            plt.figure(figsize=(8,6.1))
            # plt.title(name)
            plt.ylabel(ylabel)
            plt.xlabel(xlabel)
            plt.xlim(min(x2)-0.1*abs(min(x2) ), max(x2)+0.1*abs(min(x2)))

            plt.plot(x1, y1, 'ro', label = 'initial')
            plt.plot(x2, y2, 'bo', label = 'relaxed'   )
            plt.plot(x_range, fit_y1, 'r-',) #label = 'init_fit')
            plt.plot(x_range, fit_y2, 'b-',) #label = 'r_fit'   )
            plt.legend(loc =9)
            
            if lines == 'xy':
                plt.axvline(color='k')
                plt.axhline(color='k')



            plt.tight_layout()
            #plt.savefig('images/'+image_name)
            print_and_log( 'Saving file ...',path_to_images+str(image_name)+'.png', imp = 'y' )
            plt.savefig(path_to_images+str(image_name)+'.png',format='png', dpi = 300)
        return fit_func2  




    conv = list_of_calculations
    name = []; n = conv[0]
    name.append( n[0] )
    image_name = n[0]+'_'+n[1]+'_'+str(n[2])

    energies = []; init_energies = []
    volumes = []
    gb_volumes = []
    pressures = []
    pressures_init = []
    sigma_xx = []
    sigma_yy = []
    sigma_zz = []
    e_gbs = [] 
    e_gbs_init = []

    if type_of_plot == "e_imp":
        e_imps = []
        v_imps = []
        lengths = []
        for id in conv:        
            e_imps.append(calc[id].e_imp*1000)
            v_imps.append(calc[id].v_imp)
            l = calc[id].vlength
            lengths.append( "%s\n%.1f\n%.1f\n%.1f"%(id[0],l[0], l[1], l[2]) )
        #l = lengths[0]
        #print str(l[0])+'\n'+str(l[1])+'\n'+str(l[2])


        xlabel = "Sizes, $\AA$"
        ylabel = "Impurity energy, meV"
        ylabel2 = "Impurity volume, $\AA^3$"
        plt.figure()
        plt.title(str(name)+' other cells')
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        x = range( len(e_imps) )
        plt.xticks(x, lengths)
        plt.plot(x, e_imps, 'ro-', label = 'energy')
        plt.legend()
        plt.twinx()
        plt.ylabel(ylabel2)
        plt.plot(x, v_imps, 'bo-', label = 'volume')

        plt.subplots_adjust(left=None, bottom=0.2, right=None, top=None,
                wspace=None, hspace=None)
        #plt.ticker.formatter.set_scientific(True)
        plt.legend(loc =9)
        plt.savefig('images/e_imp_'+str(image_name)+'.png',format='png')#+str(image_name))#+'e_imp')


    if type_of_plot == "e_2imp":

        def dist_between_imp(cl):
            """Only for two impurities"""

            return np.linalg.norm(cl.end.xcart[-1] - cl.end.xcart[-2]) #assuming that impurities are at the end of xcart list.

        e_imps = [] # binding energy
        dist = [] #dist between impurities
        
        e_imps_ex = []
        dist_ex = []
        name_ex = []

        for id in conv:        
            cl = calc[id]
            e_imps.append(cl.e_imp*1000)
            #dist.append( "%s\n%.1f"%(id[0],dist_between_imp(cl) ) )
            dist.append( dist_between_imp(cl)  )







        xlabel = "Distance between atoms, $\AA$"
        ylabel = "Interaction energy, meV"
        plt.figure()
        
        # plt.title(str(name)+' v1-15')

        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        #x = range( len(e_imps) )
        #plt.xticks(x, dist)
        # plt.yscale('log')
        # plt.yscale('semilog')
        if labelnames:
            label = labelnames
        else:
            label = []
            label[0] = str(name)
            label[1] = name_ex[0]
            label[2] = name_ex[1]


        plt.plot(dist, e_imps, 'ro-', label = label[0], linewidth = 2 )
        

        if conv_ext: #manually add 
            for conv in conv_ext:
                e_imps_ex.append([])
                dist_ex.append([])
                for id in conv:        
                    cl = calc[id]
                    e_imps_ex[-1].append(cl.e_imp*1000)
                    #dist.append( "%s\n%.1f"%(id[0],dist_between_imp(cl) ) )
                    dist_ex[-1].append( dist_between_imp(cl)  )
                name_ex.append(id[0])
            plt.plot(dist_ex[0], e_imps_ex[0], 'go-', label = label[1], linewidth = 2)
            plt.plot(dist_ex[1], e_imps_ex[1], 'bo-', label = label[2], linewidth = 2)






        plt.axhline(color = 'k') #horizontal line

        plt.tight_layout()

        # plt.subplots_adjust(left=None, bottom=0.2, right=None, top=None,
        #         wspace=None, hspace=None)
        # #plt.ticker.formatter.set_scientific(True)
        plt.legend(loc =9)
        plt.savefig(path_to_images+'e_2imp_'+str(image_name)+'.png',format='png', dpi = 300)#+str(image_name))#+'e_imp')


    if type_of_plot == "fit_gb_volume_pressure":

        for id in conv:
            #energies.append(calc[id].energy_sigma0)
            #init_energies.append( calc[id].list_e_sigma0[0] ) 
            gb_volumes.append(calc[id].v_gb)
            #volumes.append(calc[id].end.vol)
            pressures.append(calc[id].extpress/1000. )
            pressures_init.append(calc[id].extpress_init/1000. )
            sigma_xx.append( calc[id].stress[0]  )
            sigma_yy.append( calc[id].stress[1]  )
            sigma_zz.append( calc[id].stress[2]  )
            #pressures_init = pressures
            e_gbs.append(calc[id].e_gb)
            e_gbs_init.append(calc[id].e_gb_init )           
            # print calc[id].bulk_extpress

        power = 3

        fit_ve = fit_and_plot(gb_volumes, e_gbs_init,  gb_volumes, e_gbs, power, 
            name, "Grain boundary expansion (m$\AA$)", "Grain boundary energy (mJ/m$^2$)", 
            image_name+"_fit_ve")


        fit = fit_and_plot(pressures_init, e_gbs_init,  pressures, e_gbs, power, 
            name, "External pressure (GPa)", "Grain boundary  energy (mJ/m$^2$)", 
            image_name+"_pe")
        #print fit
        ext_p_min  = fit.deriv().r[power-2] #external pressure in the minimum; derivative of function and the value of x in minimum

        fit_sxe = fit_and_plot(sigma_xx, e_gbs_init,  sigma_xx, e_gbs, power, 
            name, "Sigma xx (MPa)", "Grain boundary energy (mJ/m$^2$)", 
            image_name+"_sxe")
        sxe_min = fit_sxe.deriv().r[power-2] #sigma xx at the minimum of energy
        print_and_log( "sigma xx at the minimum of energy is", sxe_min," MPa")


        fit1 = fit_and_plot(pressures_init, gb_volumes,  pressures, gb_volumes, 1,
            name, "External pressure (GPa)", "Grain boundary expansion (m$\AA$)", 
            image_name+"_pv", lines = 'xy')
        #print fit1
        pulay = - calc[id].bulk_extpress
        #print " At external pressure of %.0f MPa; Pulay correction is %.0f MPa." % (ext_p_min+pulay, pulay)       
        #print " Egb = %.1f mJ m-2; Vgb = %.0f mA;"%(fit(ext_p_min), fit1(ext_p_min)  )
        print_and_log ("%s.fit.pe_pv & %.0f & %.0f & %0.f & %0.f \\\\" %
            (n[0]+'.'+n[1], fit(ext_p_min), fit1(ext_p_min),ext_p_min, ext_p_min+pulay   ))


        #print "\n At zero pressure with Pullay correction:"
        #print " Egb = %.1f mJ m-2; Vgb = %.0f mA; " % (fit(-pulay), fit1(-pulay))
        outstring =  ("%s.fit.pe_pv & %.0f & %.0f & %0.f & %0.f\\\\" %(n[0]+'.'+n[1], fit(-pulay), fit1(-pulay),-pulay,0    ))
        # print outstring
        calc[conv[0]].egb = fit(-pulay)
        calc[conv[0]].vgb = fit1(-pulay)

        return outstring #fit(ext_p_min), fit1(ext_p_min) 


    if type_of_plot == "fit_gb_volume":
        """
        should be rewritten using fit_and_plot() function
        """

        for id in conv:
            #energies.append(calc[id].energy_sigma0)
            #init_energies.append( calc[id].list_e_sigma0[0] ) 
            gb_volumes.append(calc[id].v_gb)
            e_gbs.append(calc[id].e_gb)
            e_gbs_init.append(calc[id].e_gb_init )           


        power = 3
        fit_ve = fit_and_plot(gb_volumes, e_gbs_init,  gb_volumes, e_gbs, power, 
            name, "Excess volume ($m\AA$)", "Twin energy ($mJ/m^2$)", 
            image_name+"_fit_ve")

        vgb_min  = fit_ve.deriv().r[power-2]


        #print "Fit of excess volume against energy. Pressure is uknown:"
        #print "Test Egb_min = %.1f mJ m-2; v_min = %.0f mA;"%(fit_ve(vgb_min), vgb_min)
        print ("%s.fit.ve & %.0f & %.0f & - & - \\\\" %
            (n[0]+'.'+n[1], fit_ve(vgb_min), vgb_min,   ))

    if type_of_plot == "fit_gb_volume2":

        for id in conv:
            energies.append(calc[id].energy_sigma0)
            init_energies.append( calc[id].list_e_sigma0[0] ) 
            volumes.append(calc[id].end.vol)
            pressures.append(calc[id].extpress )
            pressures_init.append(calc[id].extpress_init )

        power = 3
        pulay = 500

        fit_ve = fit_and_plot(volumes, init_energies,  volumes, energies, power, 
            name, "Volume ($\AA^3$)", "Energy  sigma->0 ($eV$)", 
            image_name+"_fit_ve")
        
        Vmin  = fit_ve.deriv().r[power-2] # minimum volume at the minimum energy
        Emin  = fit_ve(Vmin)

        fit_pe = fit_and_plot(pressures_init, init_energies,  pressures, energies, power, 
            name, "External pressure ($MPa$)", "Energy  sigma->0 ($eV$)", 
            image_name+"_fit_pe")

        ext_p_min  = fit_pe.deriv().r[power-2] #external pressure in the minimum; derivative of function and the value of x in minimum
        

        fit_pv = fit_and_plot(pressures_init, volumes,  pressures, volumes, 1,
            name, "External pressure ($MPa$)", "Volume of cell ($\AA^3$)", 
            image_name+"_fit_pv")


             
        atP = (" Emin = %.3f meV;  Vmin = %.0f A^3; "%( fit_pe(ext_p_min), fit_pv(ext_p_min)  )  ) + \
              (" for the minimum of energy relative to external pressure. The value of pressure is %.0f MPa; Pulay correction is %.0f MPa." % (ext_p_min+pulay, pulay) )
        
        at_zeroP = (" Emin = %.3f meV;  Vmin = %.0f A^3; " % (fit_pe(-pulay), fit_pv(-pulay) )  ) + \
                   (" the value of energy and volume at zero pressure with Pullay correction" )
        
        #print " Emin = %.3f meV;  Vmin = %.0f A^3;  for the minimum of energy relative to volume at some external pressure"%(fit_ve(Vmin), Vmin )
        #print atP
        #print at_zeroP

        print_and_log( "Compare V at -pulay and V for energy minimum", fit_pv(-pulay), Vmin)

        return fit_pe(-pulay), fit_pv(-pulay), Emin, Vmin








    if type_of_plot == "kpoint_conv":
        energies = []
        kpoints = []
        times = []

        for id in list_of_calculations:
            if "4" not in calc[id].state:
                continue
            energies.append(calc[id].potenergy)
            kpoints.append(calc[id].kspacing[2])
            times.append(calc[id].time)

            name.append( id[1] )

        plt.figure()
        plt.title(name)
        plt.plot(kpoints, energies,'bo-')
        plt.ylabel("Total energy (eV)")
        plt.xlabel("KSPACING along 3rd recip. vector ($\AA ^{-1}$)")
        plt.twinx()
        plt.plot(kpoints,times,'ro-')
        plt.ylabel("Elapsed time (min)")
        plt.savefig('images/'+str(conv[0])+'kconv')


    if type_of_plot == "contour":
        alist = [] ;        clist = []
        nn = str(calc[conv[0]].id[0])+"."+str(calc[conv[0]].id[1])
        f = open("a_c_convergence/"+nn+"/"+nn+".out","w")
        f.write("END DATASET(S)\n")
        k = 1
        for id in conv: #Find lattice parameters and corresponding energies
            a = calc[id].a
            c = calc[id].c
            if a not in alist: alist.append(a); 
            if c not in clist: clist.append(c);
            f.write( "acell%i %f %f %f Bohr\n"%(k, calc[id].a/to_ang, calc[id].a/to_ang, calc[id].c/to_ang )   )
            #print "etotal%i %f\n"%(k, calc[id].energy_sigma0/to_eV ),
            k+=1;
        X,Y = np.meshgrid(alist, clist)
        Z = np.zeros(X.shape)
        Zinv = np.zeros(X.shape)

        
        k=1
        for i in range(len(alist)):
            for j in range(len(clist)):
                for id in conv:
                    if calc[id].a == alist[i] and calc[id].c == clist[j]:
                        Z[i][j] = calc[id].energy_sigma0
                        Zinv[j][i] = calc[id].energy_sigma0
                        f.write( "etotal%i %f\n"%(k, calc[id].energy_sigma0/to_eV )   )
                        k+=1
        f.write("+Overall time at end (sec) : cpu=     976300.2  wall=     976512.8")
        f.close

        #Make two plots for different a and c
        plt.figure()
        plt.title(name)
        for i in range(len(alist)):
            plt.plot(clist, Z[i],'o-',label='a='+str(alist[i]))
        plt.legend()
        plt.ylabel("Total energy (eV)")
        plt.xlabel("c parameter ($\AA$)")
        plt.savefig('images/'+str(conv[0])+'c')

        plt.figure()
        plt.title(name)
        for j in range(len(clist)):
            plt.plot(alist, Zinv[j],'o-',label='c='+str(clist[j]))
        plt.legend()
        plt.ylabel("Total energy (eV)")
        plt.xlabel("a parameter ($\AA$)")
        plt.savefig('images/'+str(conv[0])+'a')

        #Make contour
        plt.figure()
        cf = plt.contourf(X, Y, Z, 20,cmap=plt.cm.jet)
        cbar = plt.colorbar(cf)
        cbar.ax.set_ylabel('Energy (eV)')

        plt.xlabel('$a$ ($\AA$)')
        plt.ylabel('$c/a$')

        plt.legend()
        plt.savefig('images/ru-contourf.png')
        #plt.show()


        #Make equation of state
        eos = EquationOfState(clist,Z[2])
        v0, e0, B = eos.fit()
        #print "a = ", alist[2]
        print_and_log( '''
        v0 = {0} A^3
        E0 = {1} eV
        B  = {2} eV/A^3'''.format(v0, e0, B) )
        eos.plot('images/a[2]-eos.png') 

        eos = EquationOfState(alist,Zinv[2])
        v0, e0, B = eos.fit()
        #print "c = ", clist[2]
        print_and_log( '''
        v0 = {0} A^3
        E0 = {1} eV
        B  = {2} eV/A^3'''.format(v0, e0, B) )
        eos.plot('images/c[2]-eos.png') 


    if type_of_plot == "dimer":


        x1 = [] #list of distances

        cl =  calc[list_of_calculations[0]]
        if cl.end.natom > 2:
            raise RuntimeError


        for xcart in cl.end.list_xcart:
            # x = xcart[1]
            # d = (x[0]**2 + x[1]**2 + x[2]**2)**0.5
            d = np.linalg.norm(xcart[1]-xcart[0]) #assuming there are only two atoms


            x1.append(d)

        y1 = cl.list_e_without_entr
        power = 4
        name = 'dimer'
        xlabel = 'Bond length'
        ylabel = 'Full energy'
        coeffs1 = np.polyfit(x1, y1, power)        
      
        fit_func1 = np.poly1d(coeffs1)

        x_range = np.linspace(min(x1), max(x1))
        fit_y1 = fit_func1(x_range); 
        f = fit_func1.deriv()
        min_e = fit_func1(f.r[2]).real
        print_and_log("The minimum energy per atom and optimal length of dimer are {:.3f} eV and {:.3f} A".format( min_e/2., f.r[2].real) )
        print_and_log("The atomization energy for dimer is {:.3f} eV ; The energy of atom in box is taken from the provided b_id".format(min_e - 2*cl.e_ref) )

        plt.figure()
        plt.title(name)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.plot(x1, y1, 'ro', label = 'init')
        plt.plot(x_range, fit_y1, 'r-', label = 'init_fit')
        plt.show()
    return











