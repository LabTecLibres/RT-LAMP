# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 11:12:12 2020

@author: Prosimios
"""
# import general packages
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy import interpolate
from copy import deepcopy
import time
import itertools

#from matplotlib.lines import Line2D

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# to manage directories and save/load data
import glob
import pickle as pkl

# import xls manager package manager
#import openpyxl as opxl

# import optimizer
from scipy.optimize import curve_fit

class Well:
    def __init__(self, fname, exp, wpos, s_name, reporter, target, data, analysis, caths = None):
        """
        fname = filename (i.e. experiment name)
        exp = experiment name
        wpos = position in the experimental well plate  e.g. 'A1'
        s_name = sample name
        reporter = measuring machine reporter setup (it is not neccessarily the
        same reagent added to the well) which define Ex/Em wavelengths.
        target = sample target
        data = list with measurement objects
        analysis = list with proceced information, parameters and analysis objects
        caths = . list of "Well_cath" objects
            object custom cathegories wich it belongs
        """
        # should include some way to check the length of d_ypes, values and units are the same.
        
        self.fname = fname
        self.exp = exp
        self.wpos = wpos
        self.s_name = s_name
        self.reporter = reporter
        self.target = target
        self.data = data
        self.analysis = analysis
        
        if caths == None:
            self.caths = list() 
        else:
            self.caths = caths
        
    
    # hint: to add a new attibute use setattr(well_obj, new_attribute, attribute value)
    
    def description(self):
        return f"{self.wpos} from {self.exp} experiment in {self.fname} file"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"{self.wpos} from {self.exp} experiment"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))

 
class Well_cath:
    def __init__(self, name, value, description = None, spacer =  None):
        """
        
        name = cathegory name
        value = object cathegory value
        description = cathegory description
        
        """
        
        self.name = name
        self.value = value
        self.description = description
        self.spacer = spacer
    
    def description(self):
        return f"{self.name} cathegory. {self.description}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.value}' in cathegory '{self.name}'"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))
        
class Reading:
    def __init__(self, sheet, well, r_name, values, units, signal, d_types=None):
        """
        
        sheet = speadsheet name
        well = position in the well plate
        r_name = reading name  --> e.g. "Amplification data"
        d_type = what kind of measurements are in values --> their label/header/identifier.
        values = measured values --> np.array
        units = values units
        signal = signal descriptor --> e.g. "SYBR green fluorescence"
        
        """
        
        self.sheet = sheet
        self.well = well
        self.r_name = r_name
        self.values = values
        self.units = units
        self.signal = signal
        
        if d_types == None:
            self.d_types = list(values.keys())
            
        else:
            self.d_types = d_types
        
        
    
    def description(self):
        return f"'{self.r_name}' reading from well {self.well}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.r_name}' reading from well {self.well}"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))

class Parameter:
    def __init__(self, name, description, units, value, properties = None):
        """
        
        name = parameter name
        description = some text expranation about it
        value = parameter value
        units = value units
        properties = dictionary with some related or relevant infomation of the parameter
        
        """
        
        self.name = name
        self.description = description
        self.value = value
        self.units = units
        
        if properties == None:
            self.properties = dict()
        else:
            self.properties = properties

    
    def description(self):
        return f"{self.name} parameter. {self.description}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"{self.name} has a value of {self.value} {self.units}"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))

class Well_set:
    def __init__(self, wells, name, fname, description, dsets=None, clfs = None, fgs = None ):
        """
        wells = list
            list of Well objects included in the set
        name = str
            name of the set
        description = str
            long description of the set
        fname = string
            filename origin of the data
        dset = list
            list of Data_set objects asociated to the Well_set
        clfs = list
            list of Classification objects asociated
        fgs = list
            list of figures asociated
        
        """
        
        self.name = name
        self.wells = wells
        self.fname = fname
        self.description = description
        
        if dsets == None:
            self.dsets = list()
        else:
            self.dsets = dsets
            
        if clfs == None:
            self.clfs = list()
        else:
            self.clfs = clfs
            
        if fgs == None:
            self.fgs = list()
        else:
            self.fgs = fgs
        
        if fname == None:
            
            fnames = list()
            
            for well in wells:
                try:
                    fnames.append(well.fname)
                except:
                    pass
            self.fname = nr_list(fnames, False)
    
    def description(self):
        return f"'{self.name}' well_set. {self.description}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.name}' well_set with {len(self.wells)} wells"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))
    
    def remove_clf(self, clf_idx = -1):
        """
        use this method to remove classification from well_set and
        well_caths from proper wells
        
        Parameters
        ----------
        clf_idx: int
            index of the classification to remove
        
        """
        clf = self.clfs[clf_idx]
        
        for cath in clf.groups.keys():
            
            for well in clf.groups[cath]:
                
                for i in range(0,len(well.caths)):
                    
                    if cath == well.caths[i]:
                        
                        del well.caths[i]
                        break
                        
        del self.clfs[clf_idx]  
    

class Database:
    def __init__(self, name, folder, filename, list_names, description = ''):
        """
        name = database descriptional name
        folder = folder where database is stored
        filename = filename of the database
        list_names = names of lists where objects will be stored
        description = text with description of the database
        
        """
        
        self.name = name
        self.folder = folder
        self.filename = filename
        self.list_names = list_names
        self.description = description
        
        ## create an "elements" dictionary to store database components
        elements = dict()
        for name in list_names:
            elements[name]= list()
        
        self.elements = elements
    
    def description(self):
        return f"'{self.name}' database. Stored in {self.filename}\n{self.description}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"{self.name} database"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))
        
    def add_element(self, element, list_name):
        # to add elements to the database
        # list_name = name of the element to fill in the elements list
        # element = element to be added (typically an empty list or list of objects)
        
        #e.g. database.add_element(list(), 'new_list_name')

        self.elements[list_name] = element
        self.list_names.append(list_name)
        print('\n',list_name, ' was added to the database\n')
    
    def append_objs(self, list_name, obj_list):
        """
        list_name : str
            name of the list where to add the objects in obj_list
        obj_list: list
            list with the objects to append
        """
        for obj in obj_list:
            if obj not in self.elements[list_name]:
                self.elements[list_name].append(obj)
            else:
                print(str(obj),'was previously in',str(list_name)+'.','Not added again')
    
    def save(self, folder = None, filename = None):
        """
        to save the database object as a pickle
        """
    
        # if no folder is indicated, then is stored in the object indicated folder
        if folder == None:
            folder = self.folder
        
        # if no filename is indicated, then is stored in the object indicated folder
        if filename == None:
            filename = self.filename
       
        ## Check if there is a previous version in the folder  ##
        f_type = '.pkl'
        db_file = filename + f_type
        
        folder_files = glob.glob1(folder,"*"+f_type)
        
        if db_file in folder_files:
            
            print('\nthere is a previous version of "',db_file,'" file')
            
            update = input('\ndo you want to update it? (y/n): ')
            
            while not (update  == 'y' or update == 'n'):
                    print('\n invalud input')
                    update = input('\ndo you want to update it? (y/n): ')
            if update == 'y':
                save_obj(self, filename, folder)
                
                print('\nfile "',db_file,'" was updated')   #db_file is "filename.pkl"
            
            else:
                print('\nsave file "',db_file,'" was canceled')
                
        ####  if there is no previous versión, create a new file ####
        else:
            print('\nthere wasn´t a previous version of "',db_file,'" file')
            
            save_obj(self, filename, folder)
                
            print('\nfile "',db_file,'" was created')   #db_file is "filename.pkl"



class Figure:
    def __init__(self, dset, clf, series, colors, title, x_text, y_text, ax_tsize, 
                 x_lim, y_lim, lgd_text, lgd_lines, log_scale, 
                 lgd_anchor=[1.01, 1.03], lgd_loc = 'upper left', thr_line = None):
        """
        series and colors have to be in the same/desired order
        
        data_set = data_set object used in the figure
        clf = classification object used in the figure
        series = data series list
        colors = colors of the lines plotted
        title = plot  title
        x_text = text of the x axis
        y_text = text of the y axis
        ax_tsize =  axis text size
        x_lim = x axis limits
        y_lim = y axis limits
        lgd_text= legend text
        lgd_lines = legend lines
        log_scale = True or False
        lgd_loc = legend location
        lgd_anchor = legend bbox_to_anchor to futher positionate the legend
        thr_line = threshold line value
        
        
        """
        # should include some way to check the length of d_ypes, values and units are the same.
        
        self.dset = dset
        self.clf = clf
        self.series = series
        self.colors = colors
        self.title = title
        self.x_text = x_text
        self.y_text = y_text
        self.ax_tsize = ax_tsize
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.lgd_text= lgd_text
        self.lgd_lines = lgd_lines
        self.log_scale = log_scale
        self.lgd_loc = lgd_loc
        self.lgd_anchor = lgd_anchor
        self.thr_line = thr_line
    
    def description(self):
        return f"'{self.title}' figure based on "\
        f"{str(self.clf)} and dataset {str(self.dset)}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.title}' figure"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))


class Data_serie:
    def __init__(self, x, y, well, name = None):
        """
        x = x axis data
        y = y axis data
        well = well object asociated
        name = well or dataserie name
        
        """
        
        self.x = x
        self.y = y        
        self.well = well
        if name == None:
            self.name = well.s_name
        else:
            self.name = name
    
    def description(self):
        return f"'{self.name}' dataserie from well '{self.well.s_name}'"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.name}' dataserie"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))


class Data_set:
    def __init__(self ,name, series, x_name='x', y_name='y', x_units='', 
                 y_units='', y_max=0, threshold=0):
        """
        name = name of the dataset
        series = dictionary or list with the data_serie objects included in the data_set
        x_name = name of x_series (e.g. Time)
        y_name = name of y_series (e.g. fluorescence)
        x_units = units of the x series
        y_units = units of the y series
        y_max = maximum "y value" of the dataseries
        threshold = dataset threshold line value
        
        """
                
        self.name = name
        self.series = series
        self.x_name = x_name
        self.y_name = y_name
        self.x_units = x_units
        self.y_units = y_units
        self.y_max = y_max
        self.threshold = threshold
        
    
    def description(self):
        return f"'{self.name}' dataset which include {len(self.series)}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.name}' dataset"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))  
        
class Classification:
    def __init__(self, name, classes, wells, groups):#, w_caths):
        """
        Classifitcation instances have wells organized in groups defined by
        their own well_cath attribute.
        
        name = classification name
        classes = list with all the Well_cath objects in the classification
        wells = List
            Well objects included in the classification
        groups = dict
            dictionary with groups of wells based on classification criteria
        #w_caths = List 
        #    Well_cath object assigned to each well
        
        """
        
        self.name = name
        self.classes = classes
        self.wells = wells
        self.groups = groups
        #self.w_caths = w_caths
        
        ## attributes for plotting ##
        caths_label = dict()
        caths_color = dict()
        
        num_groups = len(groups)
        
        colors = plt.get_cmap('jet')(np.linspace(0, 1, num_groups))
        caths = list(groups.keys())
        
        for i in range(0, num_groups):
            cath = caths[i]
            
            caths_label[cath] = str(cath.value)
            caths_color[cath] = colors[i]
                
        self.labels = caths_label
        self.colors = caths_color
        
    
    def description(self):
        return f"'{self.name}', which classify {len(self.wells)} wells in "\
    f"{len(self.classes)} classes"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.name}' classification"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))


class Enzyme:
    def __init__(self, name, coded_name = None, concentration = None, units = None, 
                 U_uL = None, dil_factor = None , lote = None, description = None):
        """
        
        name = enzyme name
        coded_name = coded name 
        concentration = concentration
        units = concentration units
        U_uL = enzyme activity units per uL
        dil_factor = dilution factor from lote stock
        lote = fabrication lote
        description = further description
        """
        
        self.name = name
        self.coded_name = coded_name
        self.concentration = concentration
        self.units = units
        self.U_uL = U_uL
        self.dil_factor = dil_factor
        self.lote = lote
        self.description = description
    
    def description(self):
        return f"'{self.name}' enzyme. {self.description}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.name}' at {self.concentration} {self.units}"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))
    
    def assign_U(self, reference ):
        """
        To compute and assign enzyme Units per uL based on reference
        
        Parameters
        ----------
        
        reference: Enzyme Object
        
        """
        
        r_U = reference.U_uL   # Units per uL
        r_con =  reference.concentration   # mass per uL
        e_con = self.concentration   # mass per uL
        
        # compute and assign the value
        e_U = r_U * e_con/r_con 
        
        self.U_uL = e_U
    
    
        
class Reaction:
    def __init__(self, name, volume, components = None, vols = None, 
                 concentrations = None, units = None, description = ''):
        """
        
        name = reaction recipe coded name
        volume = total volume in uL
        components = reaction components. dictionary of objects
        vols = volumen addded of each component. dictionary
        concentrations = concentration of each component in the reaction. dictionary
        units = concentration units
        description = further description
        """
        # Create the dictinaries inside the obj instance not in the definition
        if components == None:
            components = dict()
        
        if vols == None:
            vols = dict()
        
        if concentrations == None:
            concentrations = dict()
        
        if units == None:
            units = dict()
        
        self.name = name
        self.volume= volume        
        self.components = components
        self.vols = vols
        self.concentrations = concentrations
        self.units = units
        self.description = description
    
    def description(self):
        return f"'{self.name}' reaction. {self.description}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"{self.name}"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))
    
    def add_component(self, component, vol, concentration = 0, unit = None,
                      c_name = None):
        #component: component object
        # added volume  [uL]
        
        try:
            c_name = component.name
            c_units = component.units
            c_con = component.concentration
        
        except:
            if c_name  == None:
                c_name = str(component)
            
            c_units = unit
            c_con = concentration

        try:
            self.concentrations[c_name] = c_con*vol/self.volume
        except:
            self.concentrations[c_name] = 0
        
        self.components[c_name] = component
        self.vols[c_name] = vol
        self.units[c_name] = c_units
    
    def add_enzyme(self, enzyme, vol, unit_U = 'U/uL'):
        #component: component object
        # added volume  [uL]
        
        e_con = enzyme.concentration
        unit_con = enzyme.units
        e_U = enzyme.U_uL
        e_name = enzyme.name
        
        try:
            e_con = e_con*vol/self.volume
        except:
            e_con = None
            
        try:
            e_U = e_U*vol/self.volume
        except:
            e_U = None
        
        self.concentrations[e_name] = [e_con,e_U]
        self.units[e_name] = [unit_con, unit_U]
        
        self.components[e_name] = enzyme
        self.vols[e_name] = vol
        
    def remove_component(self, component_name):
        #component_name: string
        #    name of the component to be removed    
        
        comp_names = self.components.keys()
        
        if component_name in comp_names:
            
            del self.components[component_name]
            del self.concentrations[component_name]
            del self.vols[component_name]
            del self.units[component_name]
            print(component_name, 'removed successfully')
        
        else:
            print('There is no',component_name,'component')
        
        

class Component:
    def __init__(self, name, concentration, units, sub_comps = None , sub_cons = None,
                 sub_units = None, description = ''):
        """
        
        name = component name
        concentration = concentration
        units = concentration units
        sub_comps = sub components. dictionary of objects (components
        sub_cons = dictionary {sub_comp.name : cons value} 
            concentration of each sub-component in the component. 
        sub_units = dictionary {sub_comp.name : units value} 
            measurement units of each sub-component in the component.
        description = further description
        """
        
        # Create the dictinaries inside the obj instance not in the definition
        if sub_comps == None:
            sub_comps = dict()

        if sub_cons == None:
            sub_cons = dict()
        
        if sub_units == None:
            sub_units = dict()
        
        
        self.name = name
        self.concentration = concentration
        self.units = units
        self.sub_comps = sub_comps
        self.sub_cons = sub_cons
        self.sub_units = sub_units
        self.description = description
    
    def description(self):
        return f"'{self.name}'. {self.description}"
        
    def __str__(self):
        #to print some information instead of just the object memory location
        return f"'{self.name}' at {self.concentration} {self.units}"
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))
    
    def add_subcom(self, sub_comp, sub_con, sub_unit, sc_name = None):
        """
        sub_comp: Component object or string
        sc_name: string 
            in case it is not an object or not has the name attribute
        """
        try:
            sc_name = sub_comp.name
        
        except:
            if sc_name == None:
                sc_name = str(sub_comp)
            
        self.sub_comps[sc_name] = sub_comp
        self.sub_cons[sc_name] = sub_con
        self.sub_units[sc_name] = sub_unit
        
    def remove_subcom(self, sc_name):
        #sc_name: string
        #    name of the sub-component to be removed    
        
        sc_names = self.sub_comps.keys()
        
        if sc_name in sc_names:
            
            del self.sub_comps[sc_name]
            del self.sub_cons[sc_name]
            del self.sub_units[sc_name] 
            
            print(sc_name, 'removed successfully')
        
        else:
            print('There is no',sc_name,'sub-component')
        
def inspect(obj):
    """
    To display all the attributes included in the object and its values
    
    Parameters
    ----------
    
    obj: object
    
    Return
    ------
    dictionary of object attributes
    """
    
    return(obj.__dict__)

def attr_names(obj):
    """
    To get the attibutes names included in the object
    
    Parameters
    ----------
    
    obj: object
    
    Return
    ------
    list of object attribute names
    """
    
    keys = obj.__dict__.keys()
    
    return(list(keys))
    
def copy_obj(obj, template):
    """
    It copy all the attributes of template objects and its values to obj.
    be carefull, if the copied values are custom objects they aren´t lirerally copies 
    but just referenced. 
    --> any modification of that values in the copied object 
    will modify the original ones.
    As deepcopy is used, python regular object will be proper independe copies.
    
    """
    
    attrs = template.__dict__.keys()
    
    for attr in attrs:
        value = getattr(template, attr)
        v_copy = deepcopy(value)
            
        setattr(obj, attr, v_copy)

def reaction_from_template(template, name, description = ''):
    """
    it creates a new reaction based on a template reaction.
    The objects included from the template are shared --> be carfull
    with the modifications to them.
    
    Parameters
    ----------
    template: Reaction object
        reaction object whose attributes are copied into the new_reaction
    
    name: string
        name attribute value of the new_reaction
    
    description: string
        description attribute value of the new_reaction
    
    Returns
    -------
    new_reaction: Reaction object
        reaction object created from template
    
    """
    new_reaction = Reaction('', '')
    copy_obj(new_reaction, template)   # --> copy a base reaction

    # modify name and description
    new_reaction.name = name
    new_reaction.description = description

    return(new_reaction)

        
def print_list(xlist, attr = None):
    """
    it display the enumerated list components or a desired attribute value of those components
    
    Parameters
    ---------
    xlist : list
        List element to be enumerated
    attr: string
        attr name to be display
    
    """
    
    for i, component in enumerate(xlist):
        value = str(component)
        
        if attr != None:
            value = str(getattr(component, attr))
        
        print('[' + str(i) + ']', value )
        
def create_dataset(well_set, limits = [0,None], dset_name = None, append = True):
    """
    it creates and append a data_set to input well_set.
    With "limits" parameter you are able to not use the whole readings but
    just a portion of them (e.g. just the first ten values of each reading)
    
    Parameters
    ----------
    well_set : Well_set object
        Well set used to create the Data_set and where 
        the data_set will be append
    
    limits: list
        list with the limits of the reading values to be included
        in each Data_serie. [lim_inf, lim_sup]
    
    dset_name: str
        data_set name
        
    append: Boolean
        if True the created Data_set is append to Well_set
    """
   
    wells = well_set.wells
    
    ########### input the desired data, x, y to create the data set ##########
    
    ref_well = wells[0] # take the first well as reference
    
    print('choose the data to use: \n')
    for pair in enumerate(ref_well.data):
        print('[',pair[0],']', pair[1].r_name)
    
    time.sleep(.03)  # to avoid chaotic dispay
    data_idx = int(input('\ninput the number: '))
    print('\n"',ref_well.data[data_idx].r_name,'" was selected')

    print('\ncurrent series are: \n')
    for pair in enumerate(ref_well.data[data_idx].d_types):
        print('[',pair[0],']', pair[1])
    time.sleep(.03)
    data_x_idx = int(input('\nchoose x data index: '))
    data_y_idx = int(input('\nchoose y data index: '))
    
    #############################################################################
    # use them to define some values
        
    data_name = ref_well.data[data_idx].r_name
    x_name = ref_well.data[data_idx].d_types[data_x_idx]
    y_name = ref_well.data[data_idx].d_types[data_y_idx]
    
    if dset_name == None:
        #dset_name = input('enter a name for the dataset: ')
        dset_name = str(data_name) + ' '+str(x_name)+' vs '+str(y_name)
    
    if ref_well.data[data_idx].units != '':
        x_units = ref_well.data[data_idx].units[x_name]
        y_units = ref_well.data[data_idx].units[y_name]
    else:
        x_units = ''
        y_units = ''
    
    ### create data serie obects ###
    data_series = dict()      #dictionary to store them
    
    for well in wells:
        
        for idx in range(0,len(well.data)):
            if data_name == well.data[idx].r_name:
                data_id = idx
                
        x_values = well.data[data_id].values[x_name]
        y_values = well.data[data_id].values[y_name]
        
        if limits[0] != None:
            x_values = x_values[limits[0]:]
            y_values = y_values[limits[0]:]
        
        if limits[1] != None:
            x_values = x_values[:limits[1]]
            y_values = y_values[:limits[1]]            
        
        data_series[well] = Data_serie(x_values, y_values, well)
        
    ## create the Data_set
    dset = Data_set(dset_name, data_series, x_name, y_name, x_units, y_units)
    
    if append:
        well_set.dsets.append(dset)
        print('\n"'+str(dset_name)+'" was added to well_set' )
    else:
        return(dset)

def create_classification(well_set, wells, w_cath_values, clf_name,
                          append = True, display = True, spacer = None):
    #Classification(name, classes, wells_id, wells, groups)
    """
    to create classification objects
    it assumes class_values and wells are same lenght and are in the desired order. 
    i.e. cathegory_objects[i] is assigned to wells[i]
    
    wells = list of well objects to assign a classification value
    w_cath_values = List
        cathegory value of each well in wells. 
    class_name = classification descriptive name
    append = boolean
        if True: append classification to well set. Otherwise just return its value.
    display: boolean
        if True: display some information about the classification
    
    """
    ## first of all, check if wells are part of well_set ##
    for well in wells:
        if well not in well_set.wells:
            return
    
    # create non-redundant cathegory object (i.e. one per cathegory value)
    nr_caths_objs = create_cathegories(clf_name, w_cath_values, spacer = spacer) 
    
    class_groups = {}   #{cath_obj: [wells]}
    w_caths = []        # used to append Well_cath to each well at the end
    
    for cath, well in zip(w_cath_values , wells):
        #create the dictionary with list of elements in each cathegory
        for cath_obj in nr_caths_objs:
            if cath_obj.value == cath:
                
                w_caths.append(cath_obj)
                
                #to create each cath list just one time
                if cath_obj not in list(class_groups.keys()):  
        
                    class_groups[cath_obj] = []
                
                #append the well to the classification list
                class_groups[cath_obj].append(well) 
                
    # create the classification #
    classification = Classification(clf_name, nr_caths_objs, wells, class_groups)#, w_caths)
    
    #### just to display some useful information about the classification object
    if display == True:
        print('\nwells in classification groups:\n')
        for c_obj in nr_caths_objs:
            
            group = class_groups[c_obj]
            cath_value = c_obj.value
            
            w_pos_list = []
            
            for well in group:
                w_pos_list.append(well.wpos)
            
            print('[',str(cath_value),'] --> ', str(w_pos_list)) 
    
    ### append or return the value ###
    if append == True:
        # append the classification to well_set
        well_set.clfs.append(classification)
        print("\n'"+str(classification.name)+"' classification "\
        "was append to '"+str(well_set.name)+"' well_set")
        
        # append cathegory object to the proper well object
        for cath_obj, well in zip(w_caths , wells):
            well.caths.append(cath_obj)
        
    else:
        return(classification)

def create_cathegories(class_name, cathegories, description = None, spacer = None):
    #Well_cath(name, value, description = None):
    """
    to create well cathegories objects which afterwards assign to the proper wells.
    
    class_name = classification descriptive name. e.g. "Enzymes concentration"
    cathegories = list of cathegories to create. List . e.g.[0,0.5,1]
    description = long description of the classification if desired.
    spacer = str
        string or character used to join classification names
    
    """
    if type(cathegories) != list:
        cathegories = [cathegories]
    
    nr_cathegories = nr_list(cathegories, display=False)  #to be sure not generate duplicates
    
    cath_objs = []
    for cath in nr_cathegories:
        new_cath = Well_cath(class_name, cath, description, spacer)
        
        cath_objs.append(new_cath)
    
    print('\n'+str(len(cath_objs)),'Well_cath objects where created\n')
    
    return(cath_objs)

def join_clfs(well_set, wells, clfs_idx, clf_name, append =True, spacer = '&'):

    """
    This function join two classifications with AND logic
    it is alloed for a well not be part of a clfs[idx].
    in that case its joined classification won´t include a value for it.
    
    Parameters
    ----------
    well_set: Well_set object
        well_set object used to create the classification
    wells: list of Well objects
        Well object subject to be classified. Thay have to be a sub-set
        of well_set.wells
    clfs_idx: list
        list with the index position in well_set.clfs of the classifications to be mixed
    clf_name: string
        name of the the new joined classification
    append: Boolean
        if True: append classifiation to Well_set and Well_caths to proper wells
    spacer: char or string
        spacer used to join the chategories values.
    
    """
    
    w_cath_values = []
    
    for well in wells:
        caths_join_value = ''
        
        for idx in clfs_idx:      
            caths = well_set.clfs[idx].classes
            
            # search which cathegory is in well and join its value
            for cath in caths:
                if cath in well.caths:
                    
                    if caths_join_value == '':
                        caths_join_value = str(cath.value)
                    else:
                        caths_join_value += spacer +str(cath.value)
        
        # append the joined value
        w_cath_values.append(caths_join_value)
                    
    create_classification(well_set, wells, w_cath_values, clf_name,
                          append = append, spacer = spacer)     

def clf_labels(clf, replace_pairs = None, r_times = all):
    """
    To check and define the "labels" attribute of a Classification object
    
    Parameter
    ---------
    clf: Classification object
        classification object from well_set.clfs list
    
    replace_pairs: list
        it list contain replace values to modify the labels.
        e.g.  replace_list = [['a', 'e'],['2','1']]
        will replace all 'a' with 'e' and all '2' with '1' for 
        each label.
    r_times: list of integers
        it contain the times each replace of replace_pairs is done.
        e.g. if r_times = [2,3]
        'a' replace 'e' at most 2 times and '2' replace '1' at most 1 time.
        
    Return
    ------
    list_labels: list
        the list of labels after finished the check and/or definition
    """
    groups = clf.groups
    group_number = len(groups)
    
    print('\nThere are',group_number,'labels to define:\n')
    
    try:
        labels = clf.labels
    except:
        labels = dict()
        for key in groups.keys():
            labels[key] = ''
    
    list_labels = list()
    
    for key in groups.keys():
        
        current = str(labels[key])
        print('\nGroup: ',str(key.value))
        
        if replace_pairs != None:
            
            for i in range(len(replace_pairs)):
                
                pair = replace_pairs[i]
                
                if r_times != all:
                    
                    try:
                        times = r_times[i]
                        current = current.replace(pair[0],pair[1], times)
                    except:
                        print('r_times is shorter than pairs. All replaces will be performed for the remaining pairs')
                        current = current.replace(pair[0],pair[1])
                else:
                    current = current.replace(pair[0],pair[1])
            
            print('\ncurrent label (after replace):',current)
            time.sleep(.03)
            new = input('Press enter to confirm the replaced label or input a new label: \n')
        
        else:
            print('\ncurrent label:',current)
            time.sleep(.03)
            new = input('Press enter to keep it or input new one: \n')
        
        if new != '':
            labels[key] = new
        else:
            labels[key] = current
        print('---------------------------------------------------')
        
        list_labels.append(str(labels[key]))
        
    clf.labels = labels
    
    return(list_labels)    

def get_current_labels(clf):
    
    """
    To check and define the "labels" attribute of a Classification object
    
    Parameter
    ---------
    clf: Classification object
        classification object from well_set.clfs list
    
    Return
    ------
    labels: list
        the list of labels after finished the check and/or definition
    """
    keys = list(clf.labels.keys())
    
    labels = list()
    for key in keys:
        label = clf.labels[key]
        labels.append(label)
    
    return(labels)
    
def assign_caths_to_wells(cathegory_objects, wells):
    """
    it assumes cathegory_values and wells are same lenght and are in the desired order. 
    i.e. cathegory_objects[i] is assigned to wells[i]
    
    cathegory_objects: cathegory objects of each well. List of objects
    wells: wells objects to assign the cathegory values. List of objects
    
    """
    if type(cathegory_objects) != list:
        cathegory_objects = [cathegory_objects]
        
    if type(wells) != list:
        wells = [wells]  
        
    for cath, well in zip(cathegory_objects, wells):
        
        # check if that cathegory is previously defined
        previous = False
        
        for w_cath in well.caths:
            if w_cath:     # check it's not empty
                #print(cath.value)
                #print(w_cath.value)
                if cath.value == w_cath.value and cath.name == w_cath.name:
                    previous = True
        
        if previous == False:
            
            well.caths.append(cath)

def well_param_assignation(param_obj, well, ask = False):
    """
    Function to assign a parameter object to a well object.
    if there is previous version of the parameter it is replaced
    previous version availability is determined by param.name comparison.
    
    param_obj = Parameter object to be assigned
    
    well = Well object where parameter will be assigned
    
    ask = Boolean.
        What to do in case there is a previous version if the parameter
            False: parameter will be directly replaced
            True: ask for user confimation before replace
            
    """
    ## check if there is a previous version and replace it
    assigned = False
    if well.analysis:
        for i in range(0,len(well.analysis)):
            param_i = well.analysis[i]
            if param_obj.name == param_i.name:
                
                if ask == True:
                    
                    print('\nThere is a previous version of '+str(param_obj.name))
                    replace = input('\nIt will be replaced. Please confirm (y/n): ')
                    
                    while not (replace  == 'y' or replace == 'n'):
                        print('\n invalud input')
                        replace = input('\nIt will be replaced. Please confirm (y/n): ')
                    
                    if replace == 'y':
                        well.analysis[i] = param_obj # --> well assignation
                        assigned = True
                        print("Parameter assigned")
                        break
                    else:
                        # old version is keep and the new one is lost
                        assigned = True
                        print("Old version parameter was keep and the new discarded")
                        break
                
                else:
                    #replace withput ask confirmation
                    well.analysis[i] = param_obj # --> well assignation
                    assigned = True
                    break

    if assigned == False:
        well.analysis.append(param_obj) # --> well assignation

def dset_assignation(wset, n_dset, attr = 'name', ask = False):
    """
    Function to assign a Data_set object to a Well_set object.
    if there is previous version n_dset it is replaced
    previous version availability is determined by param.attr comparison.
    
    Parameters
    ----------
    
    wset: Well_set object
        Well_set where n_dset will be assigned
    
    n_dset: 
        Data_set object to append/assign
        
    attr: string
        Data_set attributte to perform the comparison with 
        previous versions
    
    ask = Boolean.
        What to do in case there is a previous version if the Data_set
            False: Data_set will be directly replaced
            True: ask for user confimation before replace
    """
    
    prev = False
    
    n_dset_attr = getattr(n_dset,attr)
    
    ## seach previos if there is a previous version of n_dset
    dsets = wset.dsets
    for i in range(0,len(dsets)):
        
        dset_attr = getattr(dsets[i],attr)
                
        if dset_attr == n_dset_attr:
            
            
            if ask == True:

                print('\nThere is a previous version of "'+str(n_dset_attr)+'"')
                replace = input('\nIt will be replaced. Please confirm (y/n): ')

                while not (replace  == 'y' or replace == 'n'):
                    print('\n invalid input')
                    replace = input('\nIt will be replaced. Please confirm (y/n): ')

                if replace == 'y':
                    wset.dsets[i] = n_dset
                    prev = True
                    print("Dataset replaced/actualized")
                    break
                
                else:
                    # old version is keep and the new one is lost
                    prev = True
                    print("Old version was keep and the new discarded")
                    break

            else:
                #replace without ask confirmation
                wset.dsets[i] = n_dset 
                print('Dataset "'+str(n_dset_attr)+'"'+' replaced/actualized')
                prev = True
                break

    if prev == False:
        wset.dsets.append(n_dset)
        
        try:
            print('Dataset "'+str(n_dset_attr)+'"'+' assigned in position',i+1)
        
        except:
            print('Dataset "'+str(n_dset_attr)+'"'+' assigned in position 0')
           

def copy_figure(figure):
    """
    to copy a Figure object
    """
    f = figure
    
    n_lgd_lines = []
    n_lgd_text = []
    
    for i in range(0,len(f.lgd_lines)):
        n_lgd_lines.append(f.lgd_lines[i])
        n_lgd_text.append(f.lgd_text[i])
        
    new_figure = Figure(f.dset, f.clf, f.series, f.colors, f.title, f.x_text, 
                        f.y_text, f.ax_tsize, f.x_lim, f.y_lim, n_lgd_text, 
                        n_lgd_lines, f.log_scale, f.lgd_anchor, f.lgd_loc,
                        f.thr_line)

    return(new_figure)
    
def display_figure(figure, filename = False):
    #figure:(dset, clf, series, colors, title, x_text, y_text, ax_tsize, x_lim, y_lim, lgd_text, lgd_lines, log_scale, thr_line )
    
    plt.figure()
    series = figure.series
    f_size = figure.ax_tsize
    y_axis_text = figure.y_text 
    
    for i in range(0, len(series)):
        # --> is important to do the for this way to keep the serie and color pairs as selected
        plt.plot(series[i].x, series[i].y, color = figure.colors[i])
    
    print(str(len(series)),' lines were plotted\n')
    
    lgd_lines = figure.lgd_lines
    lgd_text = figure.lgd_text
    
    if figure.thr_line != None:
        
        lth = plt.axhline(figure.thr_line,color='k', ls ='--' )
        
        lgd_lines.append(lth)
        lgd_text.append('threshold')
    
    if figure.log_scale == True:
        
        plt.yscale('log')
        y_axis_text = 'log('+y_axis_text+')'
        
        if filename != False:
            filename = filename+'_log'

    
    lgd = plt.legend(lgd_lines,lgd_text, loc = figure.lgd_loc, bbox_to_anchor=figure.lgd_anchor)
   
    plt.xlabel(figure.x_text, fontsize=f_size)
    plt.ylabel(y_axis_text, fontsize=f_size)
    plt.title(figure.title,fontsize=f_size+3)
    
    if figure.x_lim != None:
        plt.xlim(figure.x_lim)
    
    if figure.y_lim != None:
        plt.ylim(figure.y_lim)
    
    if filename != False:
        
        fig = plt.gcf()
        save_fig(filename, fig, lgd)
    
    plt.show()
    

def display_sheet(ws_number, sheet_list, wb):
    ws_name = sheet_list[ws_number]
    print(ws_name+'\n')

    print('[row number]',' cells \n')
    for i,row in enumerate(wb[ws_name].values):  
        print('['+str(i+1)+']',row)
        
def get_rows(wb,sheet_name,r_init,r_end = 'r_init'):
    #return a ddictionary with each row as an element of the dictionary
    
    rows_dic = {}
    
    if r_end == 'r_init':
        r_end = r_init
        
    
    current = r_init
    for row in wb[sheet_name].iter_rows(min_row=r_init,max_row=r_end):
        
        rows_dic[current] =[]
        for cell in row:
            rows_dic[current] .append(cell.value)
                
        print('row ',str(current),' :\n\n',rows_dic[current])
        current +=1
        
    return(rows_dic)  # {row_number: row values}

def reset_wells_data(wells):
    ## to reset the wells data
    for well in wells:
        well.data = list()

def nr_list(a_list, display = True):
    """
    a_list = any list
    display = if True the non redundant list is printed
    """
    nr_list = []
    for element in a_list:
        
        if element not in nr_list:
            nr_list.append(element)
            
    if display == True:
        print('non redundant list: \n')
        for pair in enumerate(nr_list):
            print(str(pair[0])+": '"+str(pair[1])+"'")
        
    return(nr_list)

def get_attribute_labels(obj_list, att_names, att_id = ['wpos','fname'] , union_str = ' , '):
    """
    this function gives you a list with mixed values of the attibutes indicated in att_names
    for each object on obj_list.
    e.g. if att_names = ['att1','att2'], then the output will be 
        a list with 'att1_value , att2_value' of each object.
    
    obj_list = list with the objects to create the labels
    att_id = identificator attributes of the objects. By default in wells is filenam + well plate location
    att_names = list with attribute names to mix and create the labels
    union_str = string with which concatenate selected label values of each object
    
    """
    if type(att_id) != list:
        att_id = [att_id]
    
    if type(att_names) != list:
        att_names = [att_names]
    
    label_list = []
    id_list = []
    
    for obj in obj_list:
        att_values = obj.get_attrs(att_names)
        concatenated = union_str.join(att_values)
        label_list.append(concatenated)
        
        id_value = obj.get_attrs(att_id)
        id_list.append(id_value)
    
    nr_labels = nr_list(label_list, display = True)
    
    return(label_list, nr_labels, id_list)

def select_objects(obj_list, att_name, att_values, not_in = False):
    """
    select the objects from obj_list which are "att_value" on attribute "att_name"
    if not_in  = True --> select the object which aren´t "att_value" on attribute "att_name"
    
    if att_value is list, then select the objects using OR logic over that att_values.
    
    if you want to select objects based on two att_names:
        - for AND logic selection, run this function with the second att_name 
          over the output list obtained with the first att_name 
        - for OR logic selection, run the function for each att_name over the 
          well_list. Then use nr_list function over them.
    
    well_list = list of well objects
    att_name = attribute name to select the wells
    att_values = attibute values to select the wells
    not_in = Boolean
        to perform positive or negative selection
    
    """    
    if type(att_name) != list:
        att_name = [att_name]
    
    if type(att_values) != list:
        att_values = [att_values]
    
    selected_objs = []
    for obj in obj_list:
        obj_value = obj.get_attrs(att_name)[0]
        
        if not_in == False:

            for att_value in att_values:
                if att_value in obj_value:      # if att_value is part or equal to obj_value
                    selected_objs.append(obj)
        else:
            select = True
            for att_value in att_values:
                if att_value in obj_value:   # if any att_value is part or equal to obj_value
                    select = False           # --> not select the object
                    
            if select == True:
                selected_objs.append(obj)
    
    print(str(len(selected_objs)),'objects were selected based on',str(att_name),'attribute\n')
    
    return(selected_objs)

def f_10exp_lineal(x, params, inverse = False):
    
    """
    compute the exponential -linear exponent- function value with given parameters

    Parameters
    ----------
        x: int or vector
            independent variable values
        params: list
            it shpuld contain next paramters:
            a: double

            b: double
                slope parameter

            n: double 
                normalization paramater

    Returns
    -------
    evaluated exponential with linear exponent function with the given parameters for the given x
    """
    a = params[0]
    b = params[1]
    n = params[2]
    
    if inverse  == False:
        fx = n*10**(a*x+b)
    
    if inverse == True:
        fx = (np.log10(x/n)-b)/a      #inverse function
    
    return(fx)


def explore_thr(thr, data_set, function = f_10exp_lineal, 
               attr_name='exponential', lp_name='Amplification response region',
               clf = None, save = False, ct_label = 'T', int_mode = 'quadratic'):

    """
    It displays the selected threshold value and it associated Threshold_Time(Tt) 
    or Cycle_Threshold (Ct) to evaluate it in detail and decide if it is fine.
    
    Displayed figures are stored as data_set attribute (data_set.thr_figures)
    if save == True, then figures are also exported as pdf in the workspace.
    
    function = function
        function used to approximate the data behaviour and compute Ct.
        * It has to include it's inverse definition to compute Ct.

    attr_name = List or str
        attr name which has the well parameters for function  

    lp_names = List or str
        parameters name of limits of fitted function that will be search in well.param 
        e.g. 'Amplification response region'
    
    clf: Classifcation object
        Classification used in plot titles
    
    save: boolean
        if True, figure is stored
    
    ct_label: string
        Cycle('C') or Time('T') threshold label
    
    int_mode : str
        interpolation kind in interpolate.interp1d
        (e.g.‘linear’, ‘nearest’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, 
        ‘previous’, ‘next’)
        
    
    """
    
    series = data_set.series
    wells = list(series.keys())
    
    fwells_params = getattr(data_set, attr_name)
    
    
    Cts = dict()       #{well: Tt or Ct value}
    figures = dict()   #{well: [matplotlib figure object, legend]}
    
    for well in wells:
        
        x = series[well].x
        y = series[well].y
        
        fig = plt.figure()
        pd, = plt.plot(x, y, 'bo', label = 'data serie' )
        
        lgd_lines = [pd]
        
        #search the required well parameter values
        for param in well.analysis:
            if param.name == lp_name:
                f_lims = param.value
      
        f_params = fwells_params[well].value
        
        
        if f_params != None:
            
            Ct = function(thr, f_params, inverse = True)
            
            Cts[well] = Ct     
            
            if Ct > x[f_lims[1]]:
                x_fit = np.linspace(x[f_lims[0]-1],Ct+x[0],50)
            
            else:
                x_fit = np.linspace(x[f_lims[0]-1],x[f_lims[1]]+x[0],50)
    
            fx_fit = function(x_fit, f_params)
    
            pf, = plt.plot(x_fit,fx_fit, 'k-', label = 'exponential fit')
            pi, = plt.plot(x[f_lims[0]],y[f_lims[0]],'go', label = 'exp region init')
            pe, = plt.plot(x[f_lims[1]],y[f_lims[1]],'yo', label = 'exp region end')
            
            lgd_lines.append(pf)
            lgd_lines.append(pi)
            lgd_lines.append(pe)
            
        else: #in case there is nt exponential fitting
            
            # Peform and plot an interpolation
            f_amp = interpolate.interp1d(x, y, kind = int_mode)
            x_itp = np.linspace(min(x),max(x),10*len(x))
            y_itp = f_amp(x_itp)
            
            pi, = plt.plot(x_itp, y_itp, 'k-', label = 'interpolation')
            lgd_lines.append(pi)
            
            # Get the "Ct" value
            
            cross = False  #become True if thr cross the serie
            
            # find the neighbour of Ct
            yt_1 = 0
            yt_2 = 0
            
            for yi in y_itp:
                
                if yi > thr:
                    yt_2 = yi
                    cross = True
                    break
                
                yt_1 = yi
            
            if cross == True:
                # Refinate the neighbour and assign Ct
                resolution  = 1000
                
                x_thr = np.linspace(yt_1,yt_2,resolution)
                y_thr = f_amp(x_thr)
                
                Ct = 0
                
                for i in range(0,resolution):
                    yi = y_thr[i]
                    
                    if yi > thr:
                        break
                    
                    Ct = yi    #use the inferior nearest element
            else:
                Ct = None
            
            

        ph = plt.axhline(thr , color='k', ls ='--', label = 'Threshold')
        lgd_lines.append(ph)
        
        if Ct != None:
            
            pct = plt.axvline(Ct, color='r', ls ='--', label = '$'+ct_label+'_{_t}$')
        
            lgd_lines.append(pct)
        
        if clf != None:
            
            for cls in clf.classes:
                if cls in well.caths:
                    title = cls.value
                    #title = clf.labels[cls]
                    spacer = cls.spacer
                    
                    if spacer != None:
                        title = title.replace(spacer,' , ')
                    title = title + ' - (well ' + str(well.wpos) +')'
                        
        else:
            title = str(well.s_name) + str(well.wpos)

        plt.title(title)
        plt.xlabel(str(data_set.x_name) + ' ['+str(data_set.x_units)+']')
        plt.ylabel(data_set.y_name)
        
        
        ax_lgd = [1 , 1]
        #axpos = plt.gca().get_position(original=False)
        #ax_lgd = [1 , axpos.y0-0.3]
        #ax_lgd = [axpos.x0 + axpos.width , axpos.y0 + axpos.height]
        
        lgd = plt.legend(handles = lgd_lines, loc='upper left',
                         bbox_to_anchor=ax_lgd)
                         #bbox_to_anchor=ax_lgd, ncol=len(lgd_lines) )#[1.01, 0.9])   
        
        figures[well] = [fig,lgd]   # add the figure and legend to the dictionary
        
        if save:
            print('Figure saved!')
            
            fname = str(well.s_name)+'('+str(well.wpos)+')'+"_thr"
            save_fig(fname, fig, lgd)

        plt.show()
        
        print(ct_label+'t value is: '+str(Ct))
    
    setattr(data_set,'thr_figures', figures)
    
    return(Cts, figures)

def assign_Ct(thr, well, function = f_10exp_lineal, fp_name=['a','b','N']):
    """
    To compute and assign the threshold value to a well
    
    Parameters
    ----------
    
    thr = double
        Threshold value
    
    well = Well object
        Object to assign the Ct parameter
    
    function = function
        function to compute the Ct
    
    fp_name = string or list
        required function parameter name
    
    """
    
    ## Compute the Ct value
        
    for param in well.analysis:

        if param.name == fp_name:
            param_value = param.value
    
    Ct = function(thr, param_value, inverse = True)  #use the inverse function
    
    ## Create the parameter object
    p_name = 'Ct'
    p_description = 'Cycle threshold parameter. Intersection between \
    threshold line and signal fited exponential function'
    
    Ct_parameter = Parameter(p_name, p_description, units = '', value= Ct, properties='') 
    
    ## assign it to the well object ##
    well_param_assignation(Ct_parameter, well, ask = False)
    
def f_linear(x, a, b, *args):
    """
    compute the linear function value with given parameters
    
    Parameters
    ----------
        x: int or vector
            independent variable values
                
        a: double
            slope parameter
        
        b: double
           y-intercept parameter  
           
        
    Returns
    -------
        evaluated linear fucntion with the given parameters for the given x
    """
    
    return(a * x + b)

def f_sigma(t, a, b, c, *args):
    """
    Compute the sigmoide function value using the given input values
    
    Parameters
    ----------
        t: vector
            independent variable ( "x axis", suposed to be time) 
        
        a: double
            maximum value parameter
        
        b: double
            function parameter (inflection point)
            
        c: double
            delay parameter

        
    Returns
    -------
    function evaluation
    
    """
    
    return((a /(1+np.exp(-(t+b)*c))))
    #return((a /(1+np.exp(-(t+b)*c)))+d)

def R_squared(xdata,ydata,f, *popt):
    """
    Compute the R-squared (Coefficient of determination)
    goodness of fit parameter
    
    Parameters
    ----------
        xdata: vector
            independent variable ( "x axis")  
        
        ydata: vector
            dependent variable experimental values ("y axis")
        
        f: function (callable)
            function to evaluate
            
        *popt: list
            list of paramater values to input in f

        
    Returns
    -------
         r_s: float
             R squared parameter value
    
    """
    #compute the residuals
    residuals = ydata- f(xdata, *popt)
    
    # perform the sums
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((ydata-np.mean(ydata))**2)
    
    #compute the R^2 parameter
    r_s = 1 - (ss_res / ss_tot)
    
    return(r_s)    


def function_fit(xdata, ydata, init=0, end=':', func=f_linear, p_start=[0.25,-1], 
                 param_bounds=([-np.inf,-np.inf],[np.inf,np.inf]), display = True):
    """
    Fit a given function to given data
    
    Parameters
    ----------
        xdata: vector
            independent variable ( "x axis") 
        
        ydata: vector
            dependent variable values("y axis")
        
        init: double
            point on the time vector to init the fitting
            
        end: double
            point on the time vector to end the fitting
        
        cv: vector
            contain the ID of the colonies to analyse
        
        func: function
            function to be fitted
        
        param_bounds: array of vectors
            lower and upper bounds of each parameters
            para_bounds=([lower bounds],[upper bounds])
        
    Returns
    -------
        x_fx: list
            [x[init:end], f(x[init:end])]
             
         z: vector
            fitted parameters
        
        R2: float
            R-squared goodness of fit parameter
    
    """
    
    if end == ':':
        x_values = xdata[init:]
        y_values = ydata[init:]
    else:
        x_values = xdata[init:end]
        y_values = ydata[init:end]
        
    z, _ = curve_fit(func, x_values, y_values,p0= p_start, bounds=param_bounds)
    print('fitted '+str(func)+' parameter values ' + str(z))
    
    evalF = func(x_values,*z)
    
    R2 = R_squared(x_values,y_values,func, *z)
    
    # plot the results if desired
    if display == True:
        plt.plot(xdata, ydata, '.',x_values, evalF, '-')
        plt.title('fitting')
        plt.show()
        
        print('R^2 =',R2)
        
    
    x_fx = [x_values, evalF]  # x[init:end] and f(x[init:end]) values.
    
    return(x_fx, z, R2)
    
    
def exponential_region(data_set, 
                   p_name = 'Amplification response region', 
                   p_description = 'x vector index of exponential response region of the well amplification data',
                   derivative = 'forward',
                   save = False):
    #Data_set(name, group_names, wells, series, x_name, y_name, x_units, y_units, y_max, threshold)
    """
    This function let you identify the exponential region of each dataset togheter 
    the maximum signal value
    Using this information retrieves an aproximation to the whole Well_set threshold limits.
    
    Parameters
    ----------
    data_set = Data_set object with list of values series inside it
                and all the related information
                e.g. data_set.series[0] is a data serie.
    
    p_name = str 
        name with which save the response region limits Parameter object in each well
    
    p_description = str
        description Parameter object created
    
    derivative = second derivate mode. Integer
                could be {'forward','central','backward'}
    save: Boolean
        if True, each figure is saved in the workspace
        
    Return
    ------
    thr_limits : list
        It has [min_threshold, max_threshold], were those values are the max
        ans min admisible thresholds
        
    rr_limits: list
        each element is a list with the vector index of the limits points
        of response region. [init_exponential, end_exponential, init_max]
    
    """
    def response_reg_plot(x, y, ddx, ddy, p1, p2, p3, title, data_set, save = False):
        
        fig = plt.figure()
        plt.figure(figsize=(15,3))
        #### amplification plot #####
        
        fig1 = plt.subplot(121)
        plt.title(title)
        plt.ylabel('n'+str(data_set.y_name))
        
        xlabel = str(data_set.x_name)
        
        if data_set.x_units != '':
            xlabel = xlabel + ' ['+ str(data_set.x_units) + ']'
        
        plt.xlabel(xlabel)
        
        
        ## plot the functions ##
        l1, = plt.plot(x,y,'bo', label = 'serie')
        l2, = plt.plot(ddx ,ddy,'r-', label = '2nd derivative')
        
        lgd_lines = [l1,l2]    # to build the legend        
        
        ## plot the limits ##
        if p1[0] != -1  and p2[0] != -1 :
            
            xG = x[p1[0]]
            
            xY = x[p2[0]]
            
            # as ddy is shorther, it's necessary to be sure it's on range
            if p1[1] >= len(ddy):
                yG = ddy[-1]
            else:
                yG = ddy[p1[1]]  
            
            
            if p2[1] >= len(ddy):
                yY = ddy[-1]
            else:
                yY = ddy[p2[1]]
            
            plt.plot(xG,yG,'go')
            lG = plt.axvline(xG,color='g', ls ='--', label = 'init' )
            
            plt.plot(xY,yY,'yo')
            lY =plt.axvline(xY,color='y', ls ='--', label = 'end' )
            
            ## threshold line ##
            yp1 = y[p1[0]]
            lt = plt.axhline(yp1, color='k', ls ='--', label = 'min thresh' )
            
            lgd_lines.append(lG)
            lgd_lines.append(lY)
            lgd_lines.append(lt)
        
        ## maximum signal linear fit line ##  
        x_step = (x[1]-x[0])
        
        if p3 == -1:
            # when user input -1 --> y maximum value is used
            
            m_fit = [np.max(y)]
            p3 = np.argmax(y)

            x_m_fit = [ x[p3]-x_step/2 , x[p3] , x[p3]+x_step/2 ]
            y_m_fit =  m_fit[0] * np.ones(len(x_m_fit))
            
        else:

            len_remaining = len(x) - (p3) ## how many points remain for this fitting
                    
            if len_remaining > 1:
                
                max_slope = 0   # to force it be a flat line
                
                m_fm, m_fit, R2 = function_fit(np.asarray(x), y, init = p3, end =':', 
                              func = lambda x, b: f_linear(x, max_slope, b), 
                              p_start=[0.5],param_bounds=([-np.inf],[1.5]), 
                              display = False)
                                
                x_m_fit = m_fm[0]
                y_m_fit = m_fm[1]
            
            else:
                # len_remaining == 1
                
                m_fit = [y[-1]]
                x_m_fit = [ x[p3]-x_step/2 , x[p3] , x[p3]+x_step/2 ]
                y_m_fit = m_fit[0] * np.ones(len(x_m_fit))
        
        mf, = plt.plot(x_m_fit,y_m_fit, 'k-', label = 'fitting')
        
        ### Log plot ###
        plt.subplot(122)
        
        log10y = np.log10(y)
        
        plt.plot(x, log10y,'bo', label = 'serie')
        
        # other plot settings
        plt.title('Logarithmic ' + str(title))
        plt.ylabel('log10('+'n'+str(data_set.y_name)+')')
        plt.xlabel(xlabel)
        
        #plt.plot(x,y,'bo', label = 'serie')
        #plt.axhline(yp1, color='k', ls ='--', label = 'min thresh' )
        
        if p1[0] != -1 and p2[0] != -1:
            
            plt.axvline(xG,color='g', ls ='--', label = 'init' )
            plt.axvline(xY,color='y', ls ='--', label = 'end' )
            
            ### fit a line to the log(response region) ###
            print('exponential fit')
            
            exp_0 = p1[0]
            
            #replace "nan" values with a number 1 order of magnitud lower than min
            log10y[np.isnan(log10y)]= np.nanmin(log10y)-1
             
            
            l_fit_log, pl_log, R2 = function_fit(x, log10y,init = exp_0, end =p2[0]+1, p_start= [0.5,-2], 
                             param_bounds=([0,-np.inf],[np.inf,0]), display = False)
            
            # define the limits to display it #
            init = p1[0]-2
            if init < 0:
                init = 0
            
            end = p2[0]+3
            if end > len(x):
                end = len(x)
            
            # create the line #
            x_line = x[init:end]
            #print(x_line)
            
            l_log = f_linear(x_line, pl_log[0], pl_log[1])
            
            # plot it
            plt.plot(x_line, l_log, 'k-')
            
            ####
            
            # plot trhehold 
            plt.axhline(log10y[p1[0]], color='k', ls ='--', label = 'min thresh' )
                    
        
            ## exponential region fitting display ##
            exp_params = [pl_log[0], pl_log[1], 1]
            
            if end == len(x):
                exp_x_vals = x_line
            else:
                exp_x_vals = x_line[0:-1]
                
            exp_fit = f_10exp_lineal(exp_x_vals, exp_params)
            ef, = fig1.plot(exp_x_vals,exp_fit, 'k-', label = 'fitting')
            
            lgd_lines.append(ef)
        
        else:
            lgd_lines.append(mf)
            pl_log = None      # No exponential parameters
        
        ## create the figure legend ##
        lgd = fig1.legend(handles = lgd_lines, loc='upper left', 
                         bbox_to_anchor=(0.4, -0.25), ncol=len(lgd_lines))   
        
        
        if save:
            print('Figure saved!')
            
            fname = str(well.s_name)+'('+str(well.wpos)+')'+"_exp"
            save_fig(fname, fig, lgd)
        
        plt.show()
        
        if p1[0] != -1 and p2[0] != -1:
            print('\n* init (green) = [',xG,',',yG,']')
            print('* end (yellow) = [',xY,',',yY,']')
            print('* maximum region beggining : x =',x[p3])
            print('R^2 value (exp fitting) =', R2)
        
        else:
            print('* maximum region beggining : x =',x[p3])
        
        return(m_fit[0], pl_log)  #return fited parameters of interest
    
    ########################################
    
    ########################################
    ### initiate the elements to return ###
    
    rr_limits = []  # list of vector point index of response region limits
    thr_limits = []   # list threshold limits of each well
    
    # to define the whole set threshold limits
    #thr_min = 0         
    #thr_max =np.inf
    
    # to build the dataset attributes
    max_params = dict()
    exp_params = dict()
    wthr_params = dict()
    
    # initalize the point indexs of response region limits #
    p1 = []
    p2 = []
    
    # compute the maximum signal value in the dataset --> used for normalization
    
    wells = data_set.series.keys()
    
    y_max_all = max([max(data_set.series[well].y) for well in wells ])   
    
    ##############################
    ### start dataset analysis ###
    for well in wells:
        
        serie = data_set.series[well]
        x = np.asarray(serie.x)
        y = np.asarray(serie.y)
        
        
        delay = 0  # variable to correct the x range for the derivatives
        
        if derivative == 'forward':    
            delay = 0
            
        elif derivative == 'central':
            delay = 1
            
        elif derivative == 'backward': 
            delay = 2
        
        else:
            # in case of other input,default (forward) is used
            delay = 0
        
        ddy= (y[0:-2]+y[2:]-2*y[1:-1])/4   # second derivative
        ddx = x[0+delay:-2+delay]          # x range corrected
        
        ## normalization to ]-inf,1]  ##
        
        #norm_val = y.max()    # -> normlized by the maximum of each serie
        norm_val = y_max_all   # -> normlized by the maximum of all series in data_set
        ny = y/norm_val   
        
        #nddy = ddy/ddy.max()
        ddymax = max(ddy.max(),abs(ddy.min()))  # --> take the maximum absolute value
        nddy = ddy/ddymax
        
        # then use the 2nd derivative as approximation

        # second derivative min and max indexs
        p1_ddy = np.where(ddy== ddy.max())[0][0]        # ddy maximum point
        p2_ddy = np.where(ddy== ddy[p1_ddy:].min())[0][0]  # ddy minimum point after the maximum

        # serie data min and max index
        p1_y = p1_ddy + delay   # the derivative value is used to correct the index.
        p2_y = p2_ddy + delay

        p3 = p2_y + 2      #  default plateu region beggining
        while p3 >= len(x):  # check to be inside boundaries
            p3 = p3 - 1
        
        ## check if there is a previous versión of the parameters ##
        if serie.well.analysis:
            for parameter in serie.well.analysis:
                if parameter.name == p_name:
                    
                    print('\nThere is a stored '+str(p_name)+'\n')
                    print('\n** if you change it, this version will be replaced **\n')
                    
                    p1s_y = parameter.value[0]
                    p2s_y = parameter.value[1]
                    p3s = parameter.value[2]
                    
                    #check to be inside superior boundary
                    if p1s_y <= len(x):
                        p1_y = p1s_y
                        
                        # correct the index because 2nd derivative range is shorter
                        p1_ddy = p1_y - delay
                    
                    else:
                        print('Stored P1 value out of boundaries. New value was computed')
                    
                    if p2s_y <= len(x):
                        p2_y = p2s_y
                        
                        # correct the index because 2nd derivative range is shorter
                        p2_ddy = p2_y - delay
                    
                    else:
                        print('Stored P2 value out of boundaries. New value was computed')
                    
                    if p3s <= len(x):
                        p3 = p3s
                    
                    else:
                        print('Stored P1 value out of boundaries. New value was computed')
        
        # plotting setting
        xp = x
        yp = ny
        ddxp = ddx
        ddyp = nddy
        p_title = serie.name+'_'+ well.wpos
        
        p1 = [p1_y, p1_ddy] 
        p2 = [p2_y, p2_ddy]
        
                
        LF_params = response_reg_plot(xp, yp, ddxp, ddyp, p1, p2, p3, p_title, data_set)
        
        ##confirm the result and iterate
        
        if p1[0] != -1  and p2[0] != -1:
            print('\nAre the min and max values appropiate to the exponential region?')
            print('(NE: No Exponential region)')
            time.sleep(.1)
            confirm = input('(y/n/NE): ')
        
        else:
            print('There is no exponential region. Is it correct?')
            time.sleep(.1)
            confirm = input('(y/n): ')

        while not (confirm == 'y' or confirm == 'Y' or confirm == 'NE'):             

            plt.close()
            
            valid = False
            while valid == False:
                user_p1 = int(input('enter new x position of green line: '))#(current x ='+str(x_ymax) +' ): '))
                user_p2 = int(input('enter new x position of yellow line: '))# (current x ='+str(x_ymin) +' ): '))
                
                if user_p2 > user_p1:
                    try:
                        u_p1_y = np.where(xp == user_p1)[0][0]
                        u_p2_y = np.where(xp == user_p2)[0][0]
                        
                        valid = True
                        
                    except:
                        print('\nvalue(s) out of range, posible values are:\n')
                        print(xp)
                        print('\n')
                else:
                    print('\nYellow line have to be > Green line.\n')
                

            p1 = [u_p1_y, u_p1_y - delay] 
            p2 = [u_p2_y, u_p2_y - delay]

            LF_params = response_reg_plot(xp, yp, ddxp, ddyp, p1, p2, p3, p_title, data_set)

            print('\nare the new values appropiate?')
            confirm = input('(y/n/NE): ')
    
        if confirm == 'NE':
            
            p1[0] = -1  
            p2[0] = -1
            
            LF_params = response_reg_plot(xp, yp, ddxp, ddyp, p1, p2, p3, p_title, data_set)
            
            print('No exponential region is defined')
        
        ##confirm the result of maximum region and iterate
        
        print('\nIs the start of maximum region appropiate?')
        time.sleep(.1)
        confirm = input('(y/n): ')

        while not (confirm == 'y' or confirm == 'Y'):             

            plt.close()
            
            valid = False
            while valid == False:
                
                user_p3 = int(input('enter new x start position: '))#(current x ='+str(x_ymax) +' ): '))

                
                if user_p3 == -1:
                    
                    p3 = user_p3
                    valid = True
                    
                else:
                    try:
                        p3 = np.where(xp == user_p3)[0][0]
                        valid = True

                    except:
                        print('\nvalues out of range, posible values are:\n')
                        print(xp)
                        print('\n')

            LF_params = response_reg_plot(xp, yp, ddxp, ddyp, p1, p2, p3, p_title, data_set)

            print('\nis the new value appropiate?')
            confirm = input('(y/n): ')
        
        ###### linear fits parameters assignation ####
        
        m_s = LF_params[0]
        max_signal = [m_s, m_s*norm_val]
        
        try:
            exp_linear = [LF_params[1][0], LF_params[1][1], norm_val]
        
        except:
            exp_linear = LF_params[1]
        
        ## create the parameter objects
        maxS_name = "max signal"
        maxS_descrip = "maximum signal value [normalized, original]"
        maxS_p = Parameter(maxS_name, maxS_descrip, units = '', value=max_signal, properties='')
        
        exp_name = ['a','b','N']
        exp_descrip = "linear exponent parameters 'a','b', and the normalization parameter 'N'. \
        f(x) = N*10^(a*x+b)"
        exp_p = Parameter(exp_name, exp_descrip, units = '', value=exp_linear, properties='')
        
        ## add them to the dictionary
        max_params[well] = maxS_p
        exp_params[well] = exp_p


        ## Assign them
        well_param_assignation(maxS_p, serie.well, ask = False)
        well_param_assignation(exp_p, serie.well, ask = False)
        
        ###################################
        ### Assign the determined range values as "parameter" in 'analysis' attribute of well object

        p_value = [p1[0],p2[0],p3]  # vector index of response region points
        
        rr_parameter = Parameter(p_name, p_description, units = '', value=p_value, properties='') 
        
        well_param_assignation(rr_parameter, serie.well, ask = False)

        rr_limits.append(p_value) # create a list with the parameters

        ###################################
        ## evaluate the threshold limits
        if p1[0] != -1  and p2[0] != -1:
            y_rr_min = y[p1[0]]        #get the value of the function in the initial rr point
            y_rr_max = y[p2[0]]        #get the value of the function in the final rr point
        
        else:
            y_rr_min = np.amin(y)       
            y_rr_max = np.inf
        
        well_thrs = [y_rr_min, y_rr_max]
        ############
        thr_limits.append(well_thrs)
        
        # make it a parameter to assign to dataset
        wthr_name = "well threshold limits"
        wthr_descrip = "well threshold limits [thr_min, thr_max]"
        wthr_p = Parameter(wthr_name, wthr_descrip, units = '', value=well_thrs, properties='')
        wthr_params[well] = wthr_p 
    
    # assign the data_set attibutes
    setattr(data_set, 'max_signal', max_params)  # strore it as a data_set attribute 
    setattr(data_set, 'exponential', exp_params)  # strore it as a data_set attribute
    setattr(data_set, 'wthr_lims', wthr_params)  # strore it as a data_set attribute 
    setattr(data_set, 'y_max', y_max_all)  # store it as a data_set attribute

    return(thr_limits, rr_limits) 

def save_obj(obj, name, folder ):
    """
    To save a .pkl object in a desired folder

    Parameters
    ----------
    obj : python object
        python object to be saved.
        (e.g. dictionay, list, etc)

    name : string
        name with which save the object
        
    folder: string
        folder name where to save the object
    
    Returns
    -------
    
    
    Examples
    --------
    save_obj(my_obj, 'my_file', 'my_folder')
    store my_obj as my_file.pkl in folder 'my_folder'. if my_folder is in the worspace it doesn't need to be abs_path.
    
    """
    if folder[-1] != '/':
        folder = folder + '/'
        
    with open(folder+ name + '.pkl', 'wb') as f:
        pkl.dump(obj, f, pkl.HIGHEST_PROTOCOL)


def load_obj(name, folder ):
    
    """
    To load a .pkl object from a desired folder

    Parameters
    ----------
    name : string
       name of the object to be loaded
        
    folder: string
        name of the folder where the object is.
    
    Returns
    -------
    
    returns the .pkl object to be loaded

    """
    if folder[-1] != '/':
        folder = folder + '/'
    
    with open(folder + name + '.pkl', 'rb') as f:

        return(pkl.load(f))

def load_or_create_database(db_folder, db_filename, db_name = None, db_list_name = 'default', db_description = ''):
    """
    db_folder = folder where the database is stored 
    db_filename = database file name
    db_name = name of the database
    db_list_name = list with the names of the element list to include in the database 
    db_description = text with a description of the database
    
    """    
    
    ###################################################
    ## Create a database in case it is not in folder ##
    f_type = '.pkl'
    db_file = db_filename + f_type
    
    folder_files = glob.glob1(db_folder,"*"+f_type)
    
    if db_file not in folder_files:
        
        print(db_file,'is not in ', db_folder)
        confirmation = input('\ndo you want to create "' + str(db_file)+ '"? (y/n): ')

        while not (confirmation == 'y' or confirmation == 'n'):
            print('\n invalud input')
            confirmation = input('\n do you want to create "' + str(db_file)+ '"? (y/n): ')

        if confirmation == 'y':

            if db_name == None:
                db_name = input('enter a descriptional name for the database')
            
            if db_list_name == 'default':
        
                db_list_name = ['wells', 'well_sets','figures']
            
            print('\nthis database lists will be included: \n')

            for list_name in enumerate(db_list_name):
                print(list_name)
            
            ### add new list names
            new_yn = input('\ndo you want to add a new list name? (y/n): ')

            while not (new_yn == 'y' or new_yn == 'n'):
                    print('\n invalud input')
                    new_yn = input('\ndo you want to add a new list name? (y/n): ')
        
            if new_yn  == 'y': 
                new_names = input('\n enter the new names separated by "," : ')

                for nn in new_names.split(','):
                    db_list_name.append(nn)

                print('\ncurrent database lists names: \n')

                for list_name in enumerate(db_list_name):
                        print(list_name)
                    
            ### delete some list name(s)
            del_yn = input('\ndo you want to delete a list name? (y/n): ')

            while not (del_yn == 'y' or del_yn == 'n'):
                print('\n invalud input')
                del_yn = input('\ndo you want to delete a list name? (y/n): ')
            
            if del_yn  == 'y': 
                range_len_names = range(0,len(db_list_name))
                idxs = [i for i in range_len_names]  # current list indexs
                
                del_input = input('\n input the numbers separated by "," : ').split(',')
                del_idx = [int(i) for i in del_input]  

                check =  [i for i in del_idx if i in idxs]

                while not (del_idx == check ):
                    print('invalid names indexs')
                    del_input = input('\n input the numbers separated by "," : ').split(',')
                    del_idx = [int(i) for i in del_input]
                     
                    check =  [i for i in del_idx if i in idxs]

                remove_names = [db_list_name[i] for i in range_len_names if i in del_idx]
                
                for r_name in remove_names:
                    db_list_name.remove(r_name)

                print('\ncurrent database lists names: \n')

                for list_name in enumerate(db_list_name):
                        print(list_name)
            
            database = Database(db_name, db_folder, db_filename, db_list_name, db_description)
            save_obj(database, db_filename, db_folder )
            
            print('\nDatabase "',db_file,'" was created')   #db_file is "db_filename.pkl"
            
            return(database)
    ###########################################
    ## Load database in case it is in folder ##
    
    else:
        
        print('\nDatabase "',db_file,'" is currently in the folder')
        
        load = input('\ndo you want to load it? (y/n): ')
        
        while not (load == 'y' or load == 'n'):
                print('\n invalud input')
                load = input('\ndo you want to load it? (y/n): ')
        
        if load == 'y':
            
            database = load_obj(db_filename, db_folder )
            
            print('\nDatabase "',db_file,'" was succefully loaded')
            
            return(database)




# from here I sure they are for units analysis

def get_well_param(well, param_name):
    """
    to get the value of a parameter from well.analysis list
    
    well = Well object
        well from where obtain the value
    param_name = str
        name of the parameter in well.analysis
    
    """
    for i in range(0, len(well.analysis)):
        param = well.analysis[i]
        if param.name == param_name:
            return(well.analysis[i].value)

def get_well_reading(well, reading_name, serie_name = None):
    """
    to get the a Reading from well.data list or an
    specific serie of that reading if serie_name is given.
    
    Parameters
    ----------
    well: Well object
        well from where obtain the value
    
    reading_name: str
        name of the Reading (Reading.r_name) in well.analysis
        
    serie_name: str
        "d_types" or reading serie name
    
    Return
    ------
    If serie_name == None:
    
    reading: Reading object
        reading object from well.data with given reading_name
    
    Else:
    values: list
        values from well.data.values[serie_name]
    units:
        units asociated to selected serie
        well.data.units[serie_name]
    
    """
    for data in well.data:
        if data.r_name == reading_name:
            
            if serie_name == None:
                return(data)
            
            else:
                try:
                    values = data.values[serie_name]
                    units = data.units[serie_name]
                    return(values, units)
                except:
                    print('\n',str(serie_name), 'cannot be found in',reading_name)
                    return(None)
    
    print('\n',reading_name, 'cannot be found')

def find_dataset(datasets, ds_name):
    """
    return the data_set with self.name  = ds_name
    """
    
    for i in range(0, len(datasets)):
        if ds_name == datasets[i].name:
            ds_num = i
            
    return(datasets[ds_num])  


def f_reciprocal(x, a, b, c, inverse = False):
    """
    compute the reciprocal function value with given parameters
    
    Obs: It should be re-defined using args*. it est:
        f_reciprocal(x, params*, inverse = False)
        a = params[0]
        b = params[1]
        c = params[2]
        
        --> check implications in other functions.
    
    Parameters
    ----------
        x: int or vector
            independent variable values
                
        a: double
            numerator parameter
        
        b: double
           exponent parameter. b = [1, inf]
        
        c: double
           y asymptotic parameter
        
        inverse: Boolean
            if True --> inverse function is computed
           
        
    Returns
    -------
        evaluated reciprocal function with the given parameters for the given x
    """
    
    if inverse  == False:
        fx = a*(x**(-b))+c
    
    if inverse == True:
        fx = (a/(x-c))**(1/b)
        
    return(fx)
 
def fit_concentration(d_set,d_serie_key, function= f_reciprocal):
    """
    It fit "function" to d_set[d_serie_key] values
    
    Parameters
    ----------
    d_serie_key: object, int or string
        As series could be a dict()  or list(), it could be 
        a key object, string or int.
        
    Return
    ------
    pfit: list
        fitting parameter values
    
    R2: float
        R squared goodness of fit value
    
    fig: plt.figure object
        Displayed figure
    
    """
    serie = d_set.series[d_serie_key]
    x = serie.x
    y = serie.y
    
    x_fx, p_fit, R2 = function_fit(x, y,init = 0, func = function, p_start= [1,2,0], 
                         param_bounds=([0,0.1,0],[np.inf,np.inf,np.inf]), display = False)
    
    x_fit = np.linspace(x[0],x[-1])
    y_fit = function(x_fit, p_fit[0],p_fit[1],p_fit[2])
    
    fig = plt.figure()
    plt.plot(x,y,'bo', label = serie.name)
    plt.plot(x_fit,y_fit, 'k-', label = 'fitting')
    plt.xlabel(d_set.x_name+' '+d_set.x_units)
    plt.ylabel(d_set.y_name+' '+d_set.y_units)
    plt.title(serie.name)
    plt.show()
    
    return(p_fit,R2, fig)


def compute_conc(wells, serie,  p_values, att_name = None):
    """
    serie: Data_serie or Data_set object
        in has the fitting function and parameters in its attributes
        (f_fit and p_fit)
        
    p_values: list
        Ct or Tt values
    
    att_name: string
        name of the well attribute to assign the computed
        concentration value

    
    """
    conc_list = list()
    
    pf = serie.p_fit
    ff = serie.f_fit
    
    for i in range(0,len(wells)):
        well = wells[i]
        Tt = p_values[i]     
        
        concentration = ff(Tt, pf[0], pf[1], pf[2], inverse = True)
        
        conc_list.append(concentration)
        
        print(well.s_name, 'is', concentration)
        
        #assign the value to the proper well
        if att_name != None:
            setattr(well, att_name, concentration)
    
    return(conc_list)


def plot_concentration(serie, cons, Tts, serie_label = None, 
                       cons_label = 'Bst2.0',add_fit = True):
    """
    to plot computed enzyme concentrations
    
    Parameters
    ----------
    serie: Data_serie object
        data serie with the values to plot in blue dots
        
    cons: list numbers
        list of concentration values
    Tts: list of numbers
        list of Tt or Ct values
    serie_label: str
        blue dots serie plot label
    cons_label: str
        red dots serie plot label
    add_fit: boolean
        if True fitting is included in the plot
        
    Return
    ------
    fig: Figure
        created figure plot
    
    """
    
    x = serie.x
    y = serie.y
        
    fig = plt.figure()
    if serie_label == None:
        serie_label = serie.name
        
    plt.plot(x,y,'bo', label = serie_label)
    plt.plot(cons, Tts, 'ro', label = cons_label)
    
    if add_fit == True:
        
        x_init = min(min(cons),min(x))
        x_end = max(max(cons), max(x))
        
        x_fit = np.linspace(x_init, x_end)
        
        ff = serie.f_fit
        pf = serie.p_fit
        y_fit = ff(x_fit, pf[0],pf[1],pf[2])
        
        plt.plot(x_fit,y_fit, 'k--', label = 'fitting')
    
    plt.title(serie.name)
    plt.legend()
    
    return(fig)

    
def bst_OF(x, a, b, c, bst_max, f_Tt, 
           p_Tt, Tt_max, f_nS):
    """
    BstLF Objective Funtion to determinate its optimum concentration value
    
    obs: it should be updated using a more general defintion... p1,p2,p3
    make it too specific to functions with just 3 parameters.
    
    """
    p1 =p_Tt[0]
    p2 =p_Tt[1]
    p3 =p_Tt[2]
    
    nBst = x*(bst_max**-1)
    #print(nBst)
    nTt = (f_Tt(x,p1,p2,p3)-p3)*(Tt_max**-1)
    #print(nCt)
    nS = f_nS(x)
    #print(nS)
    
    fo = a * nBst + b * nTt + c * nS
    
    return(fo,nBst,nTt,nS)


def param_data_serie(clf, yp_name, x_att_name, ds_name, p_pos = 0):
    #(wells, yp_name, x_att_name ='Bst_concentration', ds_name):
    """
    This function creates a Data_serie object composed of an attribute data 
    in the x serie and a parameter data in the y serie.
    
    clf: classification object
        classification object to be used 
    
    yp_name : str
        name of the parameter (from "well.analysis") to be used in the y axys 
   
    x_att_name: str
        well attribute name to be used in the x axys
        
    ds_name : dataset name
    
    p_pos : int
        desired parameter value position in the parameter.value list (if it is
        a list)
    
    
    """
    x_list = list()
    y_list = list()
    
    for well in clf.wells:
        
        for param in well.analysis:
                if param.name == yp_name:
                    
                    y = param.value
                    
                    if type(y) == list:
                        y = y[int(p_pos)]
                    
                    break

        
        x = getattr(well, x_att_name)
            
        x_list.append(x)
        y_list.append(y)
        
    
    g_names = list(clf.groups.keys())
    
    data_serie = Data_serie(x_list, y_list, ds_name, g_names, clf.wells, clf.wells_id)
    return(data_serie)
    


def fit_Ct_Bst(d_set, s_keys = all, s_attr_name= 'series', 
               function= f_reciprocal, dots = True, colors = None): #, x_fit_plot = None):
    """
    perform one fitting for all the indicated series
    if you want to get the fitting of each serie --> run each separatelly
    
    Parameters:
    d_set: Data_set object
        Data_set to obtain the series and some plotting information
        
    s_attr_name: string
        name of the Data_set attribute which contain the series
    
    function: callable function object
        function to perform the fitting
    
    dots: Boolean
        if True, series values are included as dots (scatter plot)
        
    colors: list
        list of colors in the same order as s_keys
        
    x_fit_plot = x_fit plottoing limits 
    """
    
    series = getattr(d_set, s_attr_name)
    
    
    if s_keys == all:
        s_keys = list(series.keys())
    
    else:
        if type(s_keys) != list:
            s_keys = list(s_keys)
    
    
    plt.figure()    
    
    x = list()
    y = list()
    
    
    for i in range(0, len(s_keys)):
        
        serie = series[s_keys[i]]
        sx = serie.x
        sy = serie.y
        
        if dots == True:
            if colors == None:
                try:
                    color = serie.color
                    plt.plot(sx, sy, ls = '', marker = 'o', label = serie.name,
                             color = color)
                except:    
                    plt.plot(sx, sy, ls = '', marker = 'o', label = serie.name)
            else:
                plt.plot(sx, sy, ls = '', marker = 'o', label = serie.name,
                             color = colors[i])
        
        for i in range(0,len(sx)):
            
            x.append(sx[i])
            y.append(sy[i])

    x_fx, p_fit, R2 = function_fit(x, y,init = 0, func = function, p_start= [1,2,0], 
                         param_bounds=([0,0.1,0],[np.inf,np.inf,np.inf]), display = False)
    
    x_fit = np.linspace(min(x),max(x))
    y_fit = function(x_fit, p_fit[0],p_fit[1],p_fit[2])
    

        
    plt.plot(x_fit,y_fit, 'k--', label = 'fitting')
    plt.xlabel(d_set.x_name + str(d_set.x_units))
    plt.ylabel(d_set.y_name)
    
    return(p_fit)
    

## function to complete some properties and informatio
def attr_to_new(obj,key,attr,na_name, na_value, ask = True):
    """
    it search key in attr value and creates a new attr with the indicated value
    It is used to complete the object information or translate coded information
    into well defined attributes.
    
    Parameters:
    obj: object
    
    key: str, int, 
        indicator element to seach in attr
    na_name: string
        name of the new attribute
    
    na_value: any
        value assigned to new attribute
        
    ask: boolean
        To confirm replace in case there is a previuos version of "new parameter"
    
    """
    
    attr_value = getattr(obj, attr)
    
    if key in attr_value:
        
        #  check there is not a preious version
        if ask == True:
            if na_name in obj.__dict__.keys():

                print('\nThere is a previous version of "'+str(na_name)+ '" for', str(obj))
                replace = input('\nIt will be replaced. Please confirm (y/n): ')

                while not (replace  == 'y' or replace == 'n'):
                    print('\n invalud input')
                    replace = input('\nIt will be replaced. Please confirm (y/n): ')

                if replace == 'y':
                    setattr(obj, na_name, na_value)
                    print("\nAttribute assigned")
                    
                else:
                    # old version is keep and the new one is lost
                    print("\nOld attribute version was keep and the new lost")
            else:
                setattr(obj, na_name, na_value)
                print('\n',str(na_name),'=',str(na_value), '. Assigned to', str(obj) ) 
                    
        else:
            #replace without ask confirmation
            setattr(obj, na_name, na_value)
            print('\n',str(na_name),'=',str(na_value), '. Assigned to', str(obj) )           


def create_readings(wells, sheet_df, sheet_name, headers, r_headers, c_well, data_headers, 
                    reading_name, signal_name, d_units='', display = True):
    """
    wells: list
        list of well objects to assign the readins
    
    sheet_df: data frame
        pandas data frame with the data sheets
    
    sheet_name : str
        name of the selected sheet
   
    headers: list
        list with the headers of the included readings data
    
    c_well : string
        well column header
        
    r_headers: int 
        headers row
        
    reading_name: string
        name of the reading
        
    signal_name: string
        name or description of the signal registered in the reading
    
    data_headers: list
        list with the headers of the selected data
    
    d_units: list
        list with the units of the included data. In the same order as data_headers
    display: boolean
        to display or not the performed reading creation and assignation
    
    """
    s_sheet = sheet_df[sheet_name]
    
    is_null = list(s_sheet.iloc[:, headers.index(c_well)].isnull())  # cells "null evaluation" based on c_well column
    
    well_index = {}  # it is organized as {row_number: well_name}
    
    max_row = s_sheet.shape[0] 
    row = r_headers+1 # start from the row next to headers
    
    units = {}
    
    for i in range(0,len(data_headers)):
        try:
            units[data_headers[i]] = d_units[i]
        except:
            units[data_headers[i]] = ''
    
    while row < max_row and not is_null[row]:  # until the end or until null value
        
        well_name = s_sheet.iloc[row, headers.index(c_well)]

        well_index[row] = well_name
        #go to the next row
        row+=1
        
    for well in wells:           # only create the readings for the given wells
        well_name = well.wpos
        
        values = {}                 # {header : list of values}
        for header in data_headers:
            values[header] = []
            
        for idx_row in list(well_index.keys()):
            
            if well_name == well_index[idx_row]:
                
                for header in data_headers:
                    values[header].append(s_sheet.iloc[idx_row, headers.index(header)])
        
        ## Create the Reading object:
        
        obj = Reading(sheet = sheet_name, well = well_name, r_name = reading_name, 
                values=values, units = units, signal=signal_name)
        
        ###############
        # Assign the reading to the Well as an attribute            
        
        well.data.append(obj)
        
        if display == True:
            print(reading_name,' was added to ', well_name,' in position ', len(well.data)-1)
            
        """
        # if wanna include the values as a list instead of a dictionary, replace values atribute creation with the follow:
        value_list = []
        for name in d_types_names
            value_list.append(values[name])
        Reading(sheet = sheet_name, well = well_name, r_name = reading_name, d_types=d_types_names, 
        values=value_list, units='', signal=signal_name)
        """

def melting_readings(wells, sheets_df, sheet_names, c_well, c_data, data_names, 
                    reading_name, signal_name, d_units='', display = True):
    """
    wells: list
        list of well objects to assign the readins
    
    sheets_df: data frame
        pandas data frame with the data sheets
    
    sheet_names : list
        list with the name of the selected sheets
    
    c_well : string 
        well column header
        
    c_data: int 
        column index where data if interest starts
    
    data_names: list
        list with the names of the data series
        
    reading_name: string
        name of the reading
        
    signal_name: string
        name or description of the signal registered in the reading
    
    d_units: list
        list with the units of the included data. In the same order as data_headers
    
    display: boolean
        to display or not the performed reading creation and assignation
    """
    units = {}
    
    for i in range(0,len(data_names)):
        try:
            units[data_names[i]] = d_units[i]
        except:
            units[data_names[i]] = ''
    
    row = {}
    wcol = {}
    for s_name in sheet_names:
        s_sheet = sheets_df[s_name]
        
        found = False
        for i in range(0, s_sheet.shape[0]):  # each row
            for j in range(0, s_sheet.shape[1]):  #each column
                if s_sheet.iloc[i,j] == c_well:
                    
                    row[s_name], wcol[s_name] = i , j
                    found = True
                    
        if found == False:
            print('"'+str(c_well)+ '" cannot be found')
            print('No reading was created')
            return()
    
    
    
    for well in wells:           # only create the readings for the given wells
        well_name = well.wpos
        values = dict()
        
        for s_name,d_name in zip(sheet_names,data_names):
            
            s_sheet = sheets_df[s_name]
            
            irow = row[s_name]+1
            
            while irow < s_sheet.shape[0]:  # until the end
        
                wname = s_sheet.iloc[irow, wcol[s_name] ]
                
                if well_name == wname:
                    values[d_name] = list(s_sheet.iloc[irow,c_data:])
                    
                #go to the next row
                irow+=1

        
        ## Create the Reading object:
        
        obj = Reading(sheet = sheet_names, well = well_name, r_name = reading_name, 
                values=values, units = units, signal=signal_name)
        
        ###############
        # Assign the reading to the Well as an attribute            
        
        well.data.append(obj)
        
        if display == True:
            print(reading_name,' was added to ', well_name,' in position ', len(well.data))

def add_time(wells, reading_name, cycle_key, t_per_c, t_unit, time_key = 'Time'):
    """
    This function add time serie to a reading object based on 
    the cicle data serie.
    
    Parameters
    ----------
    wells: list
        list with the well objects to be modified
    reading_name: str
        name of the reading object to be modified for each well
        (reading.r_name)
    cycle_key: str
        key of the cycle values in the reading data serie.
    t_per_c: int
        time per cyle (time elapsed between each cycle measurement)
    t_units: str
        measurement unit of the time serie
    """
    
    for well in wells:
        w_data = well.data
        
        for idx in range(0,len(w_data)):
            reading = w_data[idx] 
            if reading_name == reading.r_name:
                
                t_list = [t_per_c*cycle for cycle in reading.values[cycle_key]]
                
                well.data[idx].values[time_key] = t_list
                well.data[idx].units[time_key] = t_unit
                well.data[idx].d_types.append(time_key)
                
                print('Time serie was added to', well.s_name,'in data',str(idx))

def save_fig(fname, figure, legend = [0,0], fformat = '.pdf'):
    """
    To save figure in a file
    Parameters
    ----------
    fname: str 
        filename
    
    figure: matplotlib figure object
        figure to be stored
    
    legend: legend artist, list or None
        It is used to define the figure layout in the exported file.
        i) a input legend artist object used to define the figure layout
        ii) list of integers [i,j]. It seach and uses the j-st 
        matplotlib.legend.Legend object present in figure.axes[i]
        (it means the j-st subplot included in the figure) as reference.
        iii) None: legend it's not considered to define the figure layout.
        
    fformat: str
        format os the stored figure file
    
    """
    if legend != None:
        
        if type(legend) == list:
            try:
                i = legend[0]
                j = legend[1]
                
                f_axes = figure.axes[i]    # i-st figure axes
                
                lgd_list = [c for c in f_axes.get_children() if isinstance(c, matplotlib.legend.Legend)]
            
                legend = lgd_list[j]    # j-st legend of that axes.
            
            except:
                
                print('the input legend list doesn´t work. Legend won´t '\
                      'be considered in exported layout')
                figure.savefig(str(fname)+str(fformat), transparent=True)
                return()
                
            
        figure.savefig(str(fname)+str(fformat),bbox_extra_artists=(legend,),
                       bbox_inches='tight', transparent=True)
    
    else:
        figure.savefig(str(fname)+str(fformat), transparent=True)


def get_Tm_peak(data_set, clf = None, clf_label = True, int_mode = 'quadratic',
                tmbox_delay = -11, save = False):
    """
    get the T°m peak of each well in dataset
    if save == True --> figure is exported as a file in the workspace
    independent of the above it is always stored in
    'tm_figures' attribute
    
    Parameters
    ----------
    data_set:  Data_set object
        Data_set objet to be analysed    
    
    clf: Classifcation object
        Classification used in plot titles
    
    clf_label : boolean
        True --> classification.label is used for title
        False --> cath.value is used for title
        
    int_mode : str
        interpolation kind in interpolate.interp1d
        (e.g.‘linear’, ‘nearest’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, 
        ‘previous’, ‘next’)
    tmbox_delay: int
        tm_box delay from T°m peak position 
    
    save: boolean
        if True, figure is exported as a file
    """
    
    series = data_set.series
    wells = list(series.keys())
    
    
    Tms = dict()       #{well: Tm_peak[x,y]}
    figures = dict()   #{well: [matplotlib figure object, legend]}
    
    for well in wells:
        
        x = series[well].x
        y = series[well].y
        
        f_melt = interpolate.interp1d(x, y, kind = int_mode)
        x_itp = np.linspace(min(x),max(x),10*len(x))
        y_itp = f_melt(x_itp)
        
        max_idx = y_itp.argmax()
        tm_peak = [x_itp[max_idx], y_itp[max_idx]]
        
        Tms[well] = tm_peak
        
        
        fig = plt.figure()
        
        pm, = plt.plot(x, y, 'rx', markersize = 4, label = 'measures' )
        pi, = plt.plot(x_itp, y_itp, '-', label = 'interpolation')

        lpeak = plt.axvline(tm_peak[0], color='r', ls ='--', label = 'T°m peak')
        
        tm_text = 'T°m = ' + "{:.2f}".format(tm_peak[0]) + data_set.x_units 
        #plt.text(tm_peak[0], tm_peak[1] , tm_text,
        plt.text(tm_peak[0]+tmbox_delay, 0.96 * tm_peak[1] , tm_text, 
                 bbox=dict(facecolor='coral', alpha=0.9), fontsize= 'medium')#, fontname='Courier New') 
        
        if clf != None:
            
            for cls in clf.classes:
                if cls in well.caths:
                    
                    if clf_label:
                        title = clf.labels[cls]
                    
                    else:
                        title = cls.value
                        spacer = cls.spacer
                        
                        if spacer != None:
                            title = title.replace(spacer,' , ')
                    
                    title = title + ' - (well ' + str(well.wpos) +')'
                        
        else:
            title = str(well.s_name) + str(well.wpos)

        plt.title(title)
        plt.xlabel(str(data_set.x_name) + ' ['+str(data_set.x_units)+']')
        plt.ylabel(data_set.y_name)
        
        ax_lgd = [1 , 1]
        lgd_lines = [pm,pi,lpeak]
        
        lgd = plt.legend(handles = lgd_lines, loc='upper left',
                         bbox_to_anchor=ax_lgd)
        
        figures[well] = [fig,lgd]   # add the figure and legend to the dictionary
        
        if save:
            print('Figure saved!')
            
            fname = str(well.s_name)+'('+str(well.wpos)+')'+"_TmPeak"
            save_fig(fname, fig, lgd)

        plt.show()
        print('T°m peak :',"{:.2f}".format(tm_peak[0]), data_set.x_units)
    
    setattr(data_set,'tm_figures', figures)
    
    return(Tms)        
    
    
def define_thr(wset,dset_idx, clf_idx, ntc_value = 'NTC'):
    """
    
    Returns
    -------
    thr_lims: list
        global threshold limits [thr_min,thr_max]
        it takes in account the sample wells and non template wells.
    
    sample_thr_lims: list
        threshold limits of the sample wells [thr_min,thr_max]
        without take in account the NTC wells
    
    ntc_thr: float
        non template control wells maximum threshold
    
    """
    #ntc_value : non template control cathegory value
    dset = wset.dsets[dset_idx]
    groups = wset.clfs[clf_idx].groups
    caths = list(groups.keys())
    
    ntc_thrs = list()
    
    thr_min = 0         
    thr_max =np.inf
    
    for cath in caths:
        wells = groups[cath]
        
        if cath.value == ntc_value:
            for well in wells:
                # thr is the maximum value
                thr = dset.max_signal[well].value[1]
                
                ntc_thrs.append(thr)
        else:
            for well in wells:
                
                wthr_min = dset.wthr_lims[well].value[0]
                wthr_max = dset.wthr_lims[well].value[1]
                print(wthr_min)
                if wthr_min > thr_min:
                    thr_min = wthr_min

                if wthr_max < thr_max:
                    thr_max = wthr_max
    
    sample_thr_lims = [thr_min, thr_max]
    
    ntc_thr = max(ntc_thrs)
    
    if thr_min < ntc_thr:
        thr_min = ntc_thr
    
    thr_lims = [thr_min,thr_max]
    
    return(thr_lims, sample_thr_lims, ntc_thr )
    
def related_key(dictionary, string):
    """
    It search for a key of input dictionary that is "inside" of input string.
    It returns the first key that is found to fullfil the criteria.
    
    e.g. if string = 'Bst-D2' and one of the keys of dictionary is "D2"
    then "D2" will be returned (because it is part of string). if there are 
    two keys that fulfill the criteria just the first key found will be returned.
    
    Parameters
    ----------
    dictionary: dict
        dictionary to get the keys
    string: string
        string where keys are looked into
    
    Returns
    -------
    related_key: string
        first key that is found to fullfil the criteria of being part
        of string parameter.
    
    
    """
    keys = list(dictionary.keys())
    related_key = None
    
    for key in keys:
        if key in string:
            related_key = key
            break
    
    return(related_key)

def find_reaction(wnames, reactions, attr = 'coded_names'):
    """
    it search each name in wnames in the attr of each reaction
    in reactions.
    Just the first match is diplayed and assigned in the outout.
    
    Parameters
    ----------
    wnames: str list
        well names to be search
    
    reactions: list of Reaction objects
        reactions which make the relation
    
    attr: str
        name of the attribute where search each name
        
    Returns
    -------
    nr_relation: dict
        name reaction relation based on the match of name and
        indicated reaction attribute
    
    """
    
    nr_relation = {}
    
    for name in wnames:
        
        found = False

        for i in range(0,len(reactions)):
            
            reaction = reactions[i]
            
            try:
                rcnames = getattr(reaction,attr)

                if name in rcnames:
                    print("'"+name+"'",':',i,',' )
                    nr_relation[name] = i
                    found = True
                    break
            except:
                pass
        
        if found == False:
            print(name, 'is not registered in reaction coded names')
            nr_relation[name] = None
    return(nr_relation)

def filter_reaction_component(reactions, comp_key, concentration = False):
    """
    it filter the input reaction list based in component presence and 
    concentration (if included).
    
    Paramerters
    -----------
    reactions: list
        list of Reaction objects subject to filtering
    comp_key: str
        key of the desired component (reactions.componentes[comp_key])
    concentration: number
        the component concentration used to perform the filtering
        it has to match exactly the concentration in the reaction.
        
    Returns
    -------
    filter_reactions: list
        list of selected reaction objects
    
    indexs: list
        index of the selected reactions in the input reaction list
    """
    
    indexs = list()
    filter_reactions = list()
    filter_units = list()
    
    for i in range(0, len(reactions)):
        
        reaction = reactions[i]
        components_keys = list(reaction.components.keys())
        selected = False
        
        if comp_key in components_keys:
            
            selected = True
            
            if concentration != False:
                
                selected = False
                
                r_con = reaction.concentrations[comp_key]
                r_units = reaction.units[comp_key]
                
                try:
                    
                    for j in range(0,len(r_con)):
                        
                        con_j = r_con[j]
                        units_j = r_units[j]  
                        
                        if concentration == con_j:
                            selected = True
                            filter_units.append(units_j)
                except:
                    if concentration == r_con:
                        
                        selected = True
                        filter_units.append(r_units)
            
            if selected == True:
                
                indexs.append(i)
                filter_reactions.append(reaction)
    
    msj = 'reactions where selected based on '+ str(comp_key)
    
    if concentration != False:
        
        msj += ' and concentration '+str(concentration)
        
        nr_units = nr_list(filter_units, display = False)
        
        if len(nr_units) == 1:
            msj += ' '+str(nr_units)
        
        else:
            print('There are more than one kind of units. Check the selections')
    
    print(len(indexs),msj)
    
    return(filter_reactions, indexs)
                    

def select_wells_cath(wells, cath_name, cath_value, display = False):
    """
    perform a selection of the input Well list based on 
    a Cathegory object value. 
    Selected wells are those which cathegory.name and 
    cathegory.value are equal to cath_name and cath_value.
    
    Parameters
    ----------
    wells: list of Well objects
        list of wells subject to selection
    
    cath_name: string
        cathegory.name value to search for in the selection
    
    cath_value: indefined
        cathegory.value to search for in the selection.
        it could be a list of values
    
    display: boolean
        if True, a list with well.wpos is print.
    
    Return
    ------
    selected_wells: list
        list of selected Well objects
    
    """
    
    selected_wells = list()
    
    if type(cath_value) != list:
        cath_value = [cath_value]
    
    for well in wells:
        for cath in well.caths:
            if cath.name == cath_name:
                if cath.value in cath_value:
                    selected_wells.append(well)
    
    print(len(selected_wells),'wells were selected')
    
    if display == True:
        w_display = list()
        for well in selected_wells:
            w_display.append(well.wpos)
        print('\nSelected Wells:')
        print(w_display)
    
    return(selected_wells)
    

def well_component_conc(well, c_name):
    """
    To get the concentration and units of well.reaction component
    which its name is c_name
    
    Parameters
    ----------
    well: Well object
        Well object to look into
    
    c_name: string
        component name
    
    """
    
    react = well.reaction
    c_con = react.concentrations[c_name]
    c_units = react.units[c_name]
    
    return(c_con,c_units)        
    
def round_to_less(num_list):
    """
    it rounds a list of numbers to the decimal point
    of the number with the less decimals.
    
    Parameters
    ----------
    mun_list: list
        list of numbers to be rounded
    
    Return
    ------
    rounded: list
        input list rounded to the decimal point of the
        number with less decimals
    """
    # get the minimum number of decimals
    decimal_list = list()
    
    for num in num_list:
        try:
            decimals = len(str(num).split('.')[1])
        except:
            decimals = 0
        
        decimal_list.append(decimals)
    
    min_decimals = min(decimal_list)
    
    # perform the rounding
    rounded = list()
    
    for num in num_list:
        try:
            round_num = round(num, min_decimals)
        except:
            round_num = num
        
        rounded.append(round_num)
    
    return(rounded)

def plot_dset_series(data_set, series_attr= None, keys= None,
                     prev_fig = None, prev_lgd = None, split_name = None,
                     marker = 'o', color = None):
    """
    It plot all series of input data_set
    
    Parameters
    ----------
    data_set : Data_set object
        the series in data_set.series are plotted
    
    series_attr: str
        name of the attribute which have the dictionary
        with the series
    
    keys: list
        keys of the series to use 
        (i.e. dset.series[key] will be a used serie, with key being an
        element of keys)
        
    prev_fig: plt.figure object
        Figure object to plot new series over it
        
    prev_lgd: list
        list with legend lines of previous figure.
      
    split_name: list
        with the split caracter in the first position
        an a list of integers in the second postion, where the integers
        indicate the splited string word positions to use.
        e.g. split_name = [',',[0,2]]  will take the 1st an 3rd words
        of serie name splitted by ',' character.
    marker: str
        series marker type
        
    color: dict, boolean or single value
        (optional)
        if True, the color stored en each serie is used
        if dict, the keys have to be the same as series and then you 
        can specify the color of each one.
        if input a single value (e.g. 'r') it is used for all
        By default color = None --> colors defined by matplotlib color cycle
    
    Return
    ------
    figure: plt.figure object
        displayed plot with the series
    lgd_lines: list
        list with the figure legend lines (not the whole figure legend object)
    """
    # Input parameters options
    if series_attr == None:
        sds_series = data_set.series
    
    else: 
        sds_series = getattr(data_set,series_attr)
        
    if keys == None:
        
        serie_keys = list(sds_series.keys())
    else:
        serie_keys = keys
    
    if prev_fig == None:
        figure = plt.figure()
    else: 
        figure = prev_fig
    
    if prev_lgd == None:
        lgd_lines = list()
    else:
        lgd_lines = prev_lgd
    
    ## Go through series
    for key in serie_keys:

        serie = sds_series[key]

        ## plot the serie ##
        x = serie.x
        y = serie.y
        s_name = serie.name
        
        if split_name != None:
            s_name = split_and_join(s_name, split_name)
        
        # color defintion
        if color != None:
        
            if color == True:
                color_k = serie.color
        
            elif type(color) == dict:
                color_k = color[key]
            
            else:
                color_k = color


        if not None in x and not None in y :
            
            if color == None:
                p, = plt.plot(x, y, ls = '',marker = marker, label = s_name)
            else:
                p, = plt.plot(x, y, ls = '',marker = marker, label = s_name,
                              color = color_k)
            lgd_lines.append(p)

        else:
            print(s_name, 'cannot be plotted (It has "None" values)')


    plt.legend(handles = lgd_lines, loc='upper left',bbox_to_anchor=[1,1])
    #plt.legend(handles = lgd_lines, loc='lower center',bbox_to_anchor=[0,-0.6,1,1],mode="expand",ncol =2)

    plt.xlabel(str(data_set.x_name)+' ['+str(data_set.x_units)+']')
    plt.ylabel(str(data_set.y_name)+' '+str(data_set.y_units))
    plt.title(data_set.name)
    
    return(figure, lgd_lines)                                                                                                                                               
    
def series_mean_int_rep(dset,keys, display = True):
    """
    It compute the mean of internal serie replicates of indicated series on 
    dset.series and build new series with those values.
    Used series are indicated by keys.
    Replicates are defined by series.x with the same value.
    e.g:
    serie.x = [1,1,4,4,4,2]
    serie.y = [7,3,4,6,2,3]
    means positions 0,1 are replicares and positions 2,3,4 too.
    --> the new serie will be [mean[7,3], mean[4,6,2], mean[3]]
    
    Parameters
    ----------
    dset: Data_set object
        Dataset from where obtain the series
    keys: list
        keys of the series to use 
        (i.e. dset.series[key] will be a used serie, with key being an
        element of keys)
    display: Boolean
        if True, some information is print
        
    Return
    ------
    new_series: dict()
        dictionary with the new "mean series".
   
    """
    if display == True:
        print('-------------------------------------------')
        print('\n'+ str(dset.name))

    new_series = dict()
    
    for key in keys: ## for all the series en data_set
        
        # get the serie and values
        serie = dset.series[key]
        
        x_vals = np.asarray(serie.x)  # concentrations
        y_vals = np.asarray(serie.y)  # step values
        
        # compute the mean values for each concentration
        nr_x = nr_list(x_vals, False)
        y_mean = list()
        
        for x in nr_x:
            y_x = y_vals[x_vals == x]  # y values of that concentration
            
            y_x =np.array(y_x, dtype=np.float64) # to convert None to np.nan
            
            y = np.nanmean(y_x)    
            y_mean.append(y)
        
        
        ######################################
        #### create a Data_serie with them ###
        s_x = nr_x
        s_y = y_mean
        s_wells = serie.well 
        s_name = serie.name
        

        nserie = Data_serie(s_x, s_y, s_wells, s_name)
        
        ### assign other attributes ##
        try:
            s_norm = serie.norm_value
        except:
            s_norm = None
        try:
            s_xunits = serie.x_units
        
        except:
            s_xunits = ''
            
        nserie.norm_value = s_norm
        nserie.x_units = s_xunits
        
        # add to the storage dictionary
        new_series[s_name] = nserie
        
        
        ## print some information
        if display == True:
            print('\n'+ str(s_name))
            print('concentration:',s_x)
            print('Mean:',s_y)
            print('normalization value:',s_norm,'\n')
            print('-------------------------------------------')
    
    return(new_series)

def series_mean(dset, series_attr, keys, s_name, display = True):
    """
    It compute the mean series.y values between indicated series on 
    dset.series and build new serie with the mean values.
    Used series are indicated by keys.
    
    Parameters
    ----------
    dset: Data_set object
        Dataset from where obtain the series
    
    series_attr:
        name of the attribute that has the series
        
    keys: list
        keys of the series to use 
        (i.e. dset.series[key] will be a used serie, with key being an
        element of keys)
    s_name: str
        name to put into the new_serie (new_serie.name)
    
    display: Boolean
        if True, some information is print
        
    Return
    ------
    new_serie: Data_serie object
        Data serie with the mean serie.y values between input series.
   
    """
    if display == True:
        print('-------------------------------------------')
        print('\n'+ str(dset.name))
    
    x_vals = list()
    y_vals = list()
    s_wells = list()
    
    dset_series = getattr(dset, series_attr)
    
    for key in keys:

        serie = dset_series[key]
        
        x_vals.extend(serie.x)
        y_vals.extend(serie.y)
        
        s_wells.extend(serie.well)
        
    
    # convert to array to be able to mask them
    x_vals = np.asarray(x_vals)
    y_vals = np.asarray(y_vals)
    
    # get the non redundant values of x_vals
    nr_x = nr_list(x_vals,False)
    
    y_mean = list()
    y_std = list()
    y_n = list()
    y_sem = list()
    
    for x in nr_x:
        y_x = y_vals[x_vals == x]  # y values of that concentration
        y_x =np.array(y_x, dtype=np.float64)
        
        mean = np.nanmean(y_x)
        std = np.nanstd(y_x)
        n = np.count_nonzero(~np.isnan(y_x))
        try:
            sem = std/np.sqrt(n)
        except:
            sem = 0
            
        y_mean.append(mean)
        y_std.append(std)
        y_n.append(n)
        y_sem.append(sem)
        
    
    ######################################
    #### create a Data_serie with them ###
    s_x = nr_x
    s_y = y_mean 
    
    new_serie = Data_serie(s_x, s_y, s_wells, s_name)    
      
    ## assign attributes (statistics and keys)
    new_serie.y_std = y_std
    new_serie.y_n = y_n
    new_serie.y_sem = y_sem
    new_serie.keys = keys

    ## print some information
    if display == True:
        print('\n'+ str(s_name))
        print('concentration:',s_x)
        print('Mean:',s_y)
        print('-------------------------------------------')
    
    return(new_serie)    

def series_statistics(dsets, group_series, attr_name = 'mean_series'):
    """
    compute the statistics of dataset series
    
    Parameters
    ----------
    dsets: list
        list of Data_set objects
    
    group_series: dict
        dictionary with the index of the series of each groups.
        its keys are the new names of the groups.
    
    attr_name: str
        name of the attribute tho store the series composed of the mean of
        internal replicates of the original dset.series
    
    """
    ####################################
    for dset in dsets:
        
        dset_keys = list(dset.series.keys())
        
        ### compute the mean between internal replicates for all the series in sdset ###
        mean_series = series_mean_int_rep(dset,dset_keys)
        
        # assign series as dset attribute:
        setattr(dset,attr_name, mean_series)
        
        ### compute the mean between series groups (typically replicates) ###
        
        dset_groups = group_series[dset]
        g_keys = list(dset_groups.keys())
        
        
        dset.groups_mean = dict()
        dset.groups_series = dict()
        
        for key in g_keys:
            
            # get the keys of the series in the group
            g_idxs = dset_groups[key]
            g_skeys = [dset_keys[idx] for idx in g_idxs]  # key of the series to compute its mean
            
            gserie_name = str(key)
            
            # compute the "mean serie.y" of series in the group
            group_mean_serie = series_mean(dset, attr_name, g_skeys, gserie_name)
            
            dset.groups_mean[key] = group_mean_serie
            # store the group series keys as data_set attribute
            dset.groups_series[key] = g_keys


def ds_bar_plot(dsets, series_attr = 'groups_mean', s_idxs = all, special_xticks = None, 
                sb_labels = None, s_split = None, colors = 'tab10', error_bar = 'up',
                error_attr = 'y_sem', decimals = 1, x_factor = 1 ,tbs = 1/2, 
                capsz = 5, title = None, t_split = None, x_units = None, 
                y_units = None):
    """
    It creates a bar plot witht he input dseries. Each dset is a bar inside each
    group of bars.
    
    Parameters
    ----------
    dsets: list
        list of Data_set objects
        
    series_attr: str
        name of the attribute that has the series
    
    s_idxs: list of integers or dict of list
        list of index of used series and the order in which they are
        displayed in the plot. If it's a list, the same is used for all the
        data_sets. If it's a dict, it have to be composed of pairs like
        [data_set]: list of series
        
    special_xticks: dictionary
        dictionary were special x ticks are indicated.
        structure: special_xtick[serie_key] = xtick text
        xtick_label should be a string.
    
    colors: list or string
        colors to be used in each bar set.
        it could be the name of a colormap or a list with defined colors.
        
    error_bar: string
        one of these options: 'up' = only up bar, 'both' = upper and down bars, 
        False = None bars
        
    error_attr: str
        attribute name of each serie that include the value of its error bar
    
    sb_labels: list
        list with the label of each set of bars (its length should be equal to
        the datasets)
        
    s_split: list
        It indicate how to split and join the serie names
        1) with the split caracter in the first position
        an a list of integers in the second postion, where the integers
        indicate the splited string word positions to use.
        e.g. split_name = [',',[0,2]]  will take the 1st an 3rd words
        of serie name splitted by ',' character.
        2) It also could be a list of strings specifying exactly the name.
    
    decimals: int
        number of decimals to use in the text of xticks
    
    x_factor: numeric
        number by which multiply each of the x_values used to
        create the text of xtixks.
    tbs: decimal
        fraction if each position fill with the bars. It has to be a fraction
        of 1.  e.g. tbs = 2/3 means bars uses 2/3 of the space and 1/3 is left
        empty.
    capsz: scalar
        error bars cap size (indicated in points units)
    
    title: str
        title name
        
    t_split: list
        same as s_plit but applied to "title"
    
    x_units: str
        x units to display in the x axys
    
    y_units: str
        y units to display in the y axys
    
    Returns
    -------
    figure: plt.figure object
        The created figure
    
    """

    n_sets = len(dsets)

    ######### color setting ####
    if type(colors) == str:
        
        bar_colors =  plt.get_cmap(colors)(np.linspace(0, 1, n_sets))
    
    elif type(colors) == list:
        
        if len(colors) == n_sets:
            bar_colors = colors
        else:
            print('Indicated color list is not same length as sets')
            print('default colors will be used')
            cmap =  plt.get_cmap('tab10')
            bar_colors = [cmap(i) for i in range(0,n_sets)]
    #######################################        
    
    lgd_bars = list()
    
    figure = plt.figure()
    
    for i in range(0,n_sets):
        
        dset = dsets[i]
        mean_series = getattr(dset, series_attr)
        
        m_keys = list(mean_series.keys())
        
        
        if sb_labels == None:
            sb_label = dset.name
        else:
            sb_label = sb_labels[i]
        
        if s_split != None:
            try:
                sb_label = split_and_join(sb_label, s_split)
            except:
                pass
        
        xticks = list()
        x_text = list()
        
        x = 1
        
        if s_idxs == all:
            ds_idxs = range(0, len(m_keys))
        else:
            try:
                ds_idxs = s_idxs[dset]
            except:
                
                ds_idxs = s_idxs
            
            
        for idx in ds_idxs:
            key = m_keys[idx]
            
            y = mean_series[key].y
            sem = getattr(mean_series[key], error_attr)
            
            try:
                sp_xtick = special_xticks[key]
                x_text.append(str(sp_xtick))
            
            except:

                con = mean_series[key].x
                
                try:
                    # sort the data, using x values as reference
                    con = np.asarray(con)
                    y = np.asarray(y)
                    sem = np.asarray(sem)
                    
                    mask = np.argsort(con)   #sorting mask
                    con = con[[mask]]
                    y = y[[mask]]
                    sem = sem[[mask]]
                    
                except:
                    pass
                
                for c in con:
    
                    try:
                        c = round(c*x_factor, int(decimals))
                    except: 
                        c = 'nan'
    
                    x_text.append(str(c))
                
            
            ### plot the values

            bw = tbs/n_sets   # bar width 
            displace = bw*(i-(1/2)*(n_sets-1))
    
            for j in range(0, len(y)):
                
                ## error bar value ##
                sem_up = sem[j] 
                sem_low = 0
                
                if error_bar == False:
                    ebar = None
                if error_bar == 'up':
                    ebar = [[sem_low],[sem_up]]
                else:
                    ebar = sem_up
               
                ##################
                                
                p = plt.bar(x+displace, y[j], width=bw, yerr=ebar, 
                            capsize = capsz, color = bar_colors[i],
                            label = sb_label)
                
                xticks.append(x)
                x +=1
                
        lgd_bars.append(p)
        plt.xticks(xticks, (x_text))
    
    ### final plot definitions ##
    
    if x_units == None:
        try:
            x_units = dset.x_units
        except:
            x_units = ''
    
    if y_units == None:
        try:
            y_units = dset.y_units
        except:
            y_units = ''
    
    if title ==  None:
        title = dset.name
        
    if t_split != None:
        try:
            title = split_and_join(title, t_split)
        except:
            pass
    
    lgd = plt.legend(handles = lgd_bars, loc='upper left',bbox_to_anchor=[1,1])
    
    plt.title(title)
    plt.xlabel(str(dset.x_name)+' '+str(x_units))
    plt.ylabel(str(dset.y_name)+' '+str(y_units))
    
    return(figure, lgd)
    
def split_and_join(name, sp_vals):
    """
    it split and joint the input name (string) with the values indicated in sp_vals
    
    Parameter
    ---------
    name: string
        string to be splitted and joint
    sp_vals: list
        with the split caracter in the first position
        an a list of integers in the second postion, where the integers
        indicate the splited string word positions to use.
        e.g. split_name = [',',[0,2]]  will take the 1st an 3rd words
        of serie name splitted by ',' character.
    
    Return
    ------
        name: str
            proccesed name
    
    """
    spt_char = sp_vals[0]
    spt_pos = sp_vals[1]
    
    sptd = name.split(spt_char)

    n_name = ''
    for i in spt_pos:
        try:
            n_name += sptd[i]
        except:
            n_name += ''
    
    if n_name != '':
        name = n_name
    
    return(name)

def get_index(name_list, keyword):
    """
    to get the index of names from name_list
    who have keyword inside
    
    Parameters
    ----------
    name_list: list of strings
        list with string elements
    
    keyword: string
        string to be searched inside each element of name_list
    
    Return
    ------
    index_list: list of integers
        index of the name in name 
    """
    index_list = list()
    kw = str(keyword)
    
    for i in range(len(name_list)):
        
        name = name_list[i]
        
        if kw in name:
            index_list.append(i)
            
    return(index_list)
    
def print_group_series(g_series):
    """
    To print the groups of series included in g_series
    
    Parameters
    ----------
    
    g_series: dictionary
        It keys have to be Data_sets objects with series attribute defined.
        (Data_set.series)
        
    Return
    ------
    g_ds_keys: list
        each element of the list is a lits woth the keys of each Data_set
    
    """
    
    g_dsets = list(g_series.keys())
    g_ds_keys = list()
    
    for dset in g_dsets:
        try:
            dset_keys = list(dset.series.keys())
            g_ds_keys.append(dset_keys)
        
        except:
            print(dset.name, 'has no series')
        
        print('\n'+dset.name,' series:\n')
        for gkey in list(g_series[dset].keys()):
            print(gkey)
            dset_skeys = [dset_keys[idx] for idx in g_series[dset][gkey]]
            dset_series = [dset.series[key] for key in dset_skeys]
            print_list(dset_series)    
    
    return(g_ds_keys)


def serie_unit_convertion(dsets, factor, n_unit, s_attr, u_attr, 
                          su_attr = None):
    
    """
    it perform a scalar unit convertion over the values of serie.s_attr 
    over each serie present in dataset.series for each dataset in dsets.
    Values in serie.s_attr have to be list or np.array
    
    Parameters
    ----------
    dsets: list
        list with the datasets to be used
    
    factor: numerical
        factor to convert the values
    
    n_units: string
        new units
    
    s_attr: string
        name of the attribute to be converted in each serie
        (i.e. serie.s_attr will be used)
    u_attr: string
        units attribute name in the datasets
    
    su_attr: string
        units attribute name in series. Typically same as u_attr (in
        that case it's not necessary to input it)
    
    """
    
    # typically they should have the same name
    if su_attr == None:
        su_attr = u_attr
    
    # perform the convertion for each dataset
    for dset in dsets:
        set_keys = list(dset.series.keys())
        
        for key in set_keys:
    
            serie = dset.series[key]
            
            try:
                
                old_vals = getattr(serie, s_attr)
                
                if type(old_vals) == list:
                    new_vals = [x * factor for x in old_vals]
                
                if type(old_vals) == np.array:
                    new_vals = factor * old_vals
                
                # update the values
                setattr(serie, s_attr,new_vals)
                
                # update the serie unit attribute value
                setattr(serie, su_attr,n_unit)
                
            except:
                print('"'+serie.name+'"'+' cannot be converted')
                pass
        
        # update data_set unit attribute value
        setattr(dset,u_attr, n_unit)
    
def create_step_series(sdsets, step_p_name, step_p_descrip, step_p_units):
    """
    it compute the step series using the max and min signal datasets included 
    in sdsets, as the diference between the max and min signal dataset.
    The computed step values are assigned to each well as Parameters objects
    and used to create series by gruoping them accord max_dset.keys().
    
    it assume max_dset.keys() is equal or a sub-group of min_dset.keys()
    
    Parameters
    ----------
    sdsets: list
        step data_sets list = [min_dset, max_dset]
    
    step_p_name: string 
        step parameter name. 
    step_p_descrip: string
        step parameter description. Used at the moment of create the parameters for
        each well included in the series.
    step_p_units: string
        step parameter units
    
    This 3 previous parameters are used at the moment of create the 
    "step Parameter" object for each well included in the series.
        
    Return
    ------
    new_series: dict
        it contain the created step series for each of the groups (i.e. for
        each of the sdsets[0].keys )
    """
    
    ################################
    min_dset = sdsets[0]
    max_dset = sdsets[1]
    
    max_series = max_dset.series
    max_keys = list(max_series.keys())
    
    min_series = min_dset.series
    
    ### get the values and create series ####
    
    new_series = dict()
    
    for key in max_keys:
        # it uses max_serie as reference
        max_serie = max_series[key]
        
        s_name = max_serie.name
        s_norm = max_serie.norm_value
        
        s_well = list()
        s_x = list()
        s_y = list()
        
        wells = max_serie.well
        
        xs = max_serie.x

        try:
            min_serie = min_series[key]
            
            for i in range(0,len(wells)):
                x_i =  xs[i]
                well_i = wells[i]
                
                s_x.append(x_i)
                s_well.append(well_i)
                
            
                # compute the step
                try:
                    max_i = max_serie.y[i]
                    min_i = min_serie.y[i]
                
                    step_in = max_i - min_i
                
                except:
                    step_in = None
                
                # append the normalized value to serie.y
                s_y.append(step_in)
                
                ###########################################
                ## assign step value as a well parameter ##
                ###########################################
                # it's not actually necessary but could be useful
                try:
                    step_i = step_in * s_norm 
                
                except:
                    step_i = None
                    
                step_p = Parameter(step_p_name, step_p_descrip, 
                                       units = step_p_units,
                                       value = [step_in, step_i], properties='')
                well_param_assignation(step_p, well_i, ask = False)
                #################################################
        
            ######################################
            #### create a Data_serie with them ###
            
            serie = Data_serie(s_x, s_y, s_well, s_name)
            
            ## assign other serie attributes ##
            
            try:
                x_units = max_serie.x_units
                nr_units = nr_list(x_units, display = False)
                
                if len(nr_units) == 1:
                    serie.x_units = nr_units[0]
                else:
                    serie.x_units = x_units
            except:
                pass
            
            serie.norm_value = s_norm
        
            # add to the storage dictionary
            new_series[s_name] = serie
            
            ## print some information ##
            print('\n"'+ str(s_name)+'"')
            print(len(s_y), 'values were obtained:'+'\n')
            print('Step values:',s_y,'\n')
            print('-------------------------------------------')   
        
        except:
            print('An Error has ocurred. Problably:')
            print(str(key), 'is not present in', min_dset.name)    
        
    return(new_series)
    
def select_keys(dictionary, keyword, attr = None):
    """
    it search "keyword" in each key of the dictionary and return the 
    list of them which include it.
    if keys are not string they are converted with str() just for the matching.
    
    Patameter
    ----------
    dictionary: dict
        any dictionary with string keys (or directly converible to string)
    keyword: string
        keyword to match in each key and select them
        
    Return
    ------
    s_keys: list
        list with the selected keys of the dictionary
    """
    ##########################################################
    if attr != None:
        dictionary = getattr(dictionary, attr)
    else:
        pass
    
    d_keys = list(dictionary.keys())
    s_keys = [s_key for s_key in d_keys if keyword in str(s_key)]
    
    print('Selected Keys:\n')
    print_list(s_keys)
    
    return(s_keys)


def reactions_from_template(code_lists, enzyme_lists, list_template, list_attr,
                            list_vols, c_matrix = all, base_rname = None,  
                            base_rdesc = None, spacer = '_'):
    """
    it creates all the reactions combinations between the input components of
    enzyme_lists (at least a defined combination matrix - 'c_matrx'- is given) 
    for each template reaction given in r_template.
    It uses code_list to name each of the created reactions using a coded word
    based on the added enzymes.
    
    
    code_lists: list of string lists
        list of string lists with the coded names for the added enzymes. 
        Each list contain variations of one kind of enzyme 
        (e.g. list in position 0 could be different concentrations of
        Enzyme1, different batches, etc)
    
    enzyme_lists: list of Enzyme objects lists
        list of lists with the added Enzymes objects. 
        Each list contain variations of one kind of enzyme. 
        (e.g. list in position 0 could be different concentrations of
        Enzyme1, different batches, etc)
    
    list_template: list of Reaction objects
        the Reaction objects used as template to create new reactions.
    
    list_attr: list of strings
        list with the reaction atrribute name of each enzyme
        e.g. list_attr = ['polymerase', 'RT'] 
    
    base_rname: string
        Base name to use in all the created reactions. Special cases:
        base_rname =  None --> No base name is used
        base_rname = 'template' --> name of the template reaction is used
    
    base_rdesc: string
        base description to use in all the created reactions. Special cases:
        base_rdesc =  None --> No base description is used
        base_rdesc = 'template' --> description of the template reaction is used
        
    c_matrix: np.array with 0 or 1 values
        it indicates the combinations of enzymes used to create the reactions
        e.g. c_matrix = array([[1, 1],[1, 0]]) means the 4th combination won't
        be performed. 
        If c_matrix = all --> all combinations are done.
    
    spacer: string
        spacer character or string used at creating the new reactions in its
        name.
        
    Return
    ------
    reactions: list
        list of created Reactions objects
        
    """
    if type(c_matrix) != np.ndarray:
        if c_matrix == all:
            len_list = [len(le) for le in enzyme_lists]
            c_matrix = np.ones(len_list, dtype=int)

    reactions = list()  
    e_combs = list(itertools.product(*enzyme_lists))
    e_codes = list(itertools.product(*code_lists))
    
    for template in list_template:
        
        ### define some reaction base attributes
        base_name = ''
        if base_rname != None:
            if base_rname == 'template':
                base_name = template.name
            else:
                base_name = base_rname
        
        base_description = ''
        if base_rdesc != None:
            if base_rdesc == 'template':
                base_description = template.description
            else:
                base_description = base_rdesc
        
        ######## iterate through each combination ###

        c = 0
        
        for i in np.nditer(c_matrix):
            if i == 1:  #create only if matrix element values is 1
                
                #create the reaction        
                new_r = reaction_from_template(template, base_name, 
                                                   base_description)
                reactions.append(new_r)
                
                # add each enzyme of the combination
                e_comb = e_combs[c]
                e_code = e_codes[c]
                
                for j in range(len(e_comb)):
                    
                    e = e_comb[j]
                    code = e_code[j]
                    e_attr = list_attr[j]
                    e_vol = list_vols[j]
                    
                    ## add the enzyme
                    if e != None:
                        new_r.add_enzyme(e, e_vol)
                        
                        # complete the name and description
                        new_r.name += spacer + code
                        new_r.description += ', ' + e.name +' enzyme'
                        
                    setattr(new_r, e_attr , e)
            
            c+=1
    
    return(reactions)

def assign_well_reactions(wells, name_react_rel, reactions, r_attr = 'reaction',
                          wn_attr = 'coded_names'):
    """
    This function is used to assign a reaction from reactions to each well
    in wells unsing the relation indicated in name_react_rel dictionary.
    Reactions objects are stored in r_attr of each well object.
    
    Parameters
    ----------
    
    wells: list of Well objects
    
    name_react_rel: dict
        well.name reaction relation
        the keys are the well.names and the values are the index of the
        related Reaction object in reactions lists.
        
    r_attr: string
        Well attribute name to store the reaction
        
    wn_attr: string
        Reaction attribute name to store the related well.name
        
    """
    for well in wells:
        
        well_name = well.s_name
        
        reaction_idx = name_react_rel[well_name]
        reaction = reactions[reaction_idx]
        
        setattr(well, r_attr, reaction)
        
        try:
            included_names = reaction.coded_names
            if well_name not in included_names:
                reaction.coded_names.append(well_name)
        except:
            setattr(reaction, wn_attr, [well_name])

def sort_by_concentration(wells, components, pos = '1st', 
                          direction = 'default', display = False ):
    """
    It sorts the Well objects in wells accord the concentration of its componentes
    indicated in 'components'. The hierarchy of sorting is defined by the order in
    components (the first element has the highest hierarchy and so on).
    
    Parameters
    ----------
    
    wells: list
        list of well objects
    components: list
        list of components to perform the sort
        The hierarchy of sort is defined by the order
        in the list.
        
    pos: list
        list with the positions of the concentration to
        use in the case the component(s) have more than one
        concentration value (because the units).
        It has to be defined in the same order and length that components.
        default is to use the first value.
    
    direction: list of booleans
        it contain the direction in which perform the sort for each 
        component in componentes. 
        e.g. if 'components' has 2 elements, then 'direction' could be
        [True False] --> the first element will be sort descending
        and the second ascending
        direction = defaul --> sort all ascending
    
    display: Boolean
        if True, the result is displayed.
    
    Return
    -------
    wells: list
        list with sorted well objects
    """
    # Build a list with the lists of concentrations of each component
    comp_cons = list()
    
    for i in range(len(components)):
        
        comp = components[i]
        con_list = list()
        
        for well in wells:
            
            try:
                value = well.reaction.concentrations[comp]
            except:
                value = 0
                print(well.s_name,'has no component',comp)
            
            # if value is a list then use the selected positional value
            if type(value) == list:
                
                if pos == '1st':
                    value = value[0]
                else:
                    pos = pos[i]
                    value = value[pos]
                    
            con_list.append(value)
        
        comp_cons.append(con_list)
    
    ## perform the sorting ##
    nc = len(comp_cons)
    
    if direction == 'default':
        direction = [False for i in range(nc)]
    
    # perform inverted loop
    while nc > 0:
        
        nc -= 1
        
        c_i = comp_cons[nc]
        dir_i = direction[nc]
        
        # get the sort index
        sci = sorted(range(len(c_i)), key=lambda k: c_i[k], reverse = dir_i)
        
        #list of sorted wells
        wells = [wells[i] for i in sci ]
        
        # sort concentrations to keep a coherent well concentration relation
        for j in range(len(comp_cons)):
            c_j = comp_cons[j]
            comp_cons[j] = [c_j[i] for i in sci ]
    
    if display == True:
        
        print('\nSorted Wells:\n')
        
        for i in range(len(wells)):
            
            w = wells[i]
            wcons = list()
            
            for cons in comp_cons:
                
                wcons.append(cons[i])
            
            print(w.s_name,'-',components,'=',wcons )
    
    return(wells)
    
def create_series_from_dict(wset, clf_idx, swells, wd_con, wd_values, cidx = 0, 
                            c_units = None, v_units = None):
    """
    It creates Series objects from a list of wells and dictionaries with the
    serie values for each well. The "x" values are supposed to be concentrations
    (wd_con) and the "y" values are suposed to be any other attribute value
    (wd_values)
    
    Parameters
    ----------
    
    wset: Well_set object
        Well set wich include the Classifications to use
    
    clf_idx: int
        Classification index inside Well_set classifications list
        (wset.clfs)
    
    swells: list
        List of Well objects. They have to belong or be a sub-group of wset.
    
    wd_con: dict
        dictionary with the "x" series values for each well
        (its keys are Well objects)
        
    wd_values: dict
        dictionary with the "y" series values for each well
        (its keys are Well objects)
        
    cidx: int
        concentration index (in case concentration vector has more than one 
        dimention)
    
    c_units: dict
        dictionary with the units of wd_con values
    
    v_units: dict
        dictionary with the units of wd_values values
        
    Return
    ------
    new_series: dict
        dictionary with the created Data_series objects.
        its ornization is:   { 'serie_name': serie object}
    """
    sclf = wset.clfs[clf_idx]
    new_series = dict()
    
    for cath in sclf.classes:
        
        ## create required value storage lists
        con_list = list()
        attr_values = list()
        
        c_units_list = list()
        v_units_list = list()
        
        s_well_list = list()
        
        empty = True
        for well in sclf.groups[cath]:
            
            if well in swells:
                
                empty = False
                
                ########### get the values ################
                
                # concentration values
                con_value = wd_con[well]
                
                
                if c_units != None:
                    
                    wc_units = c_units[well]
                    c_units_list.append(wc_units)
                
                #  use just the indicated concentration index ##
                
                if type(con_value) == list:
                    
                    con_value = con_value[cidx]
                    wc_units = wc_units[cidx]
                    c_units_list[-1] = wc_units
                
                # attribute values
                attr_value = wd_values[well]
                
                if v_units != None:
                                        
                    wv_units = v_units[well]
                    v_units_list.append(wv_units)
                    
                ## append all of them ##
                
                con_list.append(con_value)
                attr_values.append(attr_value)
                
                s_well_list.append(well)
    
        if empty == False:

            print(len(con_list), 'values were obtained:'+'\n')
            print(con_list,'\n')
            
            ######################################
            #### create a Data_serie with them ###
    
            x_vals = con_list
            y_vals = attr_values
            serie_wells = s_well_list 
            serie_name = cath.value
    
            serie = Data_serie(x_vals, y_vals, serie_wells, serie_name)
            
            if c_units != None:
                serie.x_units = c_units_list
            
            if v_units != None:
                serie.x_units = v_units_list                       

            # add to the storage dictionary
            new_series[serie_name] = serie
    
    return(new_series)
    
def get_well_reaction_values(swells, ckey = None, e_attr = None, l_empty = 1,
                             empty_val = 0, empty_u = ''):
    """
    It get the values and units of the indicated component (ckey) or enzyme
    (e_attr) in each well of swells. In case some well doesn´t have the 
    component or enzyme --> empty values will be assigned.
    It return a dictionary of values and units with Wells as keys.
    
    Parameter
    ---------
    swells: list
        List of Well objects
    
    ckey: string
        component name. It has to be a key of well.reaction.components
        In case it is not present in the well --> the "empty" protocol 
        will be applied.
    
    e_attr: string
        enzyme attribute to be used instead of direct ckey. It is used to 
        get the name of the enzyme of each well (useful when enzyme names
        of the swells are not the same)
    
    l_empty: integer > 0
        len of concentration values (in case they are indicated un more than
        one unit of concentration). It is used to define the empty instances.
    
    empty_val: numeric
        values assigned to empty instances (wells which doesn't have the
        indicated component)
    
    empty_u: string
        units assigned to empty instances (wells which doesn't have the
        indicated component)
    
    Return
    ------
    The keys of both returned dictionaries are Well objects
    
    well_values: dict
        dictionary with each well reaction concentration value for the
        indicated component (ckey) or enzyme (e_attr). 
        
    well_units: dict
        dictionary with each well reaction concentration units value for the
        indicated component (ckey) or enzyme (e_attr).
    
    """
    well_values = dict()
    well_units = dict()
    
    for well in swells:
        
        wr = well.reaction
        
        if e_attr == None and ckey != None:
            
            comp_name = ckey
            
        elif e_attr != None and ckey == None:
            
            try:
                enzyme = getattr(wr, e_attr) # --> in case is not the same for all swells
                comp_name = enzyme.name
            
            except:
                comp_name = 'Not present'
            
        else:
            print('You must indicate a component key or enzyme name attribute')
            return()
            
        
        try:
            ## get the component values
            
            con, units = well_component_conc(well, comp_name)

        except:
            
            con = list()
            units = list()
            
            for i in range(l_empty):
                
                con.append(empty_val)
                units.append(empty_u)
        
        well_values[well] = con
        well_units[well] = units
        
    return(well_values, well_units)
    
def ds_bar_plot_fixTicks(dsets, series_attr = 'groups_mean', s_idxs = all, special_xticks = None, 
                sb_labels = None, s_split = None, colors = 'tab10', error_bar = 'up',
                error_attr = 'y_sem', decimals = 1, x_factor = 1 ,tbs = 1/2, 
                capsz = 5, title = None, t_split = None, x_units = None, 
                y_units = None):
    """
    It creates a bar plot witht he input dseries. Each dset is a bar inside each
    group of bars.
    
    Parameters
    ----------
    dsets: list
        list of Data_set objects
        
    series_attr: str
        name of the attribute that has the series
    
    s_idxs: list of integers or dict of list
        list of index of used series and the order in which they are
        displayed in the plot. If it's a list, the same is used for all the
        data_sets. If it's a dict, it have to be composed of pairs like
        [data_set]: list of series
        
    special_xticks: dictionary
        dictionary were special x ticks are indicated.
        structure: special_xtick[serie_key] = xtick text
        xtick_label should be a string.
    
    colors: list or string
        colors to be used in each bar set.
        it could be the name of a colormap or a list with defined colors.
        
    error_bar: string
        one of these options: 'up' = only up bar, 'both' = upper and down bars, 
        False = None bars
        
    error_attr: str
        attribute name of each serie that include the value of its error bar
    
    sb_labels: list
        list with the label of each set of bars (its length should be equal to
        the datasets)
        
    s_split: list
        It indicate how to split and join the serie names
        1) with the split caracter in the first position
        an a list of integers in the second postion, where the integers
        indicate the splited string word positions to use.
        e.g. split_name = [',',[0,2]]  will take the 1st an 3rd words
        of serie name splitted by ',' character.
        2) It also could be a list of strings specifying exactly the name.
    
    decimals: int
        number of decimals to use in the text of xticks
    
    x_factor: numeric
        number by which multiply each of the x_values used to
        create the text of xtixks.
    tbs: decimal
        fraction if each position fill with the bars. It has to be a fraction
        of 1.  e.g. tbs = 2/3 means bars uses 2/3 of the space and 1/3 is left
        empty.
    capsz: scalar
        error bars cap size (indicated in points units)
    
    title: str
        title name
        
    t_split: list
        same as s_plit but applied to "title"
    
    x_units: str
        x units to display in the x axys
    
    y_units: str
        y units to display in the y axys
    
    Returns
    -------
    figure: plt.figure object
        The created figure
    
    """

    n_sets = len(dsets)

    ######### color setting ####
    if type(colors) == str:
        
        bar_colors =  plt.get_cmap(colors)(np.linspace(0, 1, n_sets))
    
    elif type(colors) == list:
        
        if len(colors) == n_sets:
            bar_colors = colors
        else:
            print('Indicated color list is not same length as sets')
            print('default colors will be used')
            cmap =  plt.get_cmap('tab10')
            bar_colors = [cmap(i) for i in range(0,n_sets)]
    #######################################        
    
    lgd_bars = list()
    
    figure = plt.figure()
    
    ## get non redundant xtext values ##
    x_values = list()
    
    for dset in dsets:
        g_mean = dset.groups_mean
        g_keys = list(g_mean.keys())
        
        for i in range(0,len(g_keys)):
            key = g_keys[i]
            con = g_mean[key].x
            x_values.extend(con)
    x_values = nr_list(x_values, display=False)
    
    # sort it
    mask = np.argsort(x_values)   #sorting mask
    x_values = np.asarray(x_values)[[mask]]
    # format as string
    xtexts = [str(round(xval*x_factor, int(decimals))) for xval in x_values]
    
    xticks = np.arange(0,len(xtexts),1)
    ########
    
    for i in range(0,n_sets):
        
        dset = dsets[i]
        mean_series = getattr(dset, series_attr)
        
        m_keys = list(mean_series.keys())
        
        
        if sb_labels == None:
            sb_label = dset.name
        else:
            sb_label = sb_labels[i]
        
        if s_split != None:
            try:
                sb_label = split_and_join(sb_label, s_split)
            except:
                pass
        
        x_text = list()
        
        if s_idxs == all:
            ds_idxs = range(0, len(m_keys))
        else:
            try:
                ds_idxs = s_idxs[dset]
            except:
                
                ds_idxs = s_idxs
            
            
        for idx in ds_idxs:
            key = m_keys[idx]
            
            y = mean_series[key].y
            sem = getattr(mean_series[key], error_attr)
            
            try:
                sp_xtick = special_xticks[key]
                x_text.append(str(sp_xtick))
            
            except:

                con = mean_series[key].x
                
                try:
                    # sort the data, using x values as reference
                    con = np.asarray(con)
                    y = np.asarray(y)
                    sem = np.asarray(sem)
                    
                    mask = np.argsort(con)   #sorting mask
                    con = con[[mask]]
                    y = y[[mask]]
                    sem = sem[[mask]]
                    
                except:
                    pass
                
                for c in con:
    
                    try:
                        c = round(c*x_factor, int(decimals))
                    except: 
                        c = 'nan'
                        
                    x_text.append(str(c))
            
            ### plot the values

            bw = tbs/n_sets   # bar width 
            displace = bw*(i-(1/2)*(n_sets-1))
    
            for j in range(0, len(y)):
                
                # get the bar x-axis position
                xtext = x_text[j]
                x = xtexts.index(xtext)
                
                ## error bar value ##
                sem_up = sem[j] 
                sem_low = 0
                
                if error_bar == False:
                    ebar = None
                if error_bar == 'up':
                    ebar = [[sem_low],[sem_up]]
                else:
                    ebar = sem_up
               
                ##################
                                
                p = plt.bar(x+displace, y[j], width=bw, yerr=ebar, 
                            capsize = capsz, color = bar_colors[i],
                            label = sb_label)
                
        lgd_bars.append(p)
    
    plt.xticks(xticks, (xtexts))
    
    ### final plot definitions ##
    
    if x_units == None:
        try:
            x_units = dset.x_units
        except:
            x_units = ''
    
    if y_units == None:
        try:
            y_units = dset.y_units
        except:
            y_units = ''
    
    if title ==  None:
        title = dset.name
        
    if t_split != None:
        try:
            title = split_and_join(title, t_split)
        except:
            pass
    
    lgd = plt.legend(handles = lgd_bars, loc='upper left',bbox_to_anchor=[1,1])
    
    plt.title(title)
    plt.xlabel(str(dset.x_name)+' '+str(x_units))
    plt.ylabel(str(dset.y_name)+' '+str(y_units))
    
    return(figure, lgd)
    

def heatmap(x_vals, y_vals, data, title = None, annotate = True, 
             cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from data array using x_vals and y_vals as axes labels.

    Parameters
    ----------
    data: array or np.array
        An array of shape (N, M) wich the data to be display in each square
        of the heatmap
    
    y_vals: list
        list length N with the labels for the rows.
    
    x_vals: list
        list of length M with the labels for the columns.
    
    cbar_kw: dict, Optional
        
        A dictionary with arguments to `matplotlib.Figure.colorbar`.
    
    cbarlabel: string, Optional
        The label for the colorbar.
    
    **kwargs
        All other arguments are forwarded to pyplot `imshow`.
    
    Returns
    -------
    fig:
        Matplotlib Figure object
    cbar:
        ColorBar object
    
    """
    if type(data) != np.ndarray:
        data = np.asarray(data)
    
    d_shape = data.shape
    
    if d_shape[1] != len(x_vals) or d_shape[0] != len(y_vals):
        print("axes and data dimentions doesn't match")
        return()
    
    fig, ax = plt.subplots()
    
    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(x_vals)))
    ax.set_yticks(np.arange(len(y_vals)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(x_vals)
    ax.set_yticklabels(y_vals)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    if annotate == True:
        for i in range(len(y_vals)):
            for j in range(len(x_vals)):
                text = ax.text(j, i, data[i, j],
                               ha="center", va="center", color="w")
    if title != None:
        ax.set_title(str(title))
    fig.tight_layout()
    plt.show()
    
    return(fig, cbar)
    
def get_max_signal_series(swells, sclf, p_max_name = 'max signal',
                          pmax_idx= 1, npmax_idx = 0, **kwargs):
    
    """
    To obtain the maximum or minimum amplification signal values of input wells.
    Values are returned as Series build according the selected classification
    By default is asumed is organized as pmax = [normlized, not normalized]
    
    Parameters
    ----------
    swells: list
        List of well objects to be used
    
    sclf: Classification object
        desired classification to build the series
        
    p_max_name: str. Optional
        name of the parameter were maximum signal is stored
    
    pmax_idx: int. Optional
        index of not normalized pmax value.
        used to compute the normalization factor
    
    npmax_idx: int. Optional
        index of normalized pmax value.
        
    **kwargs 
        All other arguments are forwarded to 'get_well_reaction_values`. 
        
    Return
    ------
    new_series: dict
        dictionary with the created series for each classification
    """
    
    ##################################
    new_series = dict()
    
    for cath in sclf.classes:
        
        # obtain the enzyme concentration values
        con_values, con_units = get_well_reaction_values(swells, **kwargs)
        
        ## create required value storage lists
        con_list = list()
        units_list = list()
        pmax_values = list()
        pnorm_values = list()
        s_well_list = list()
        
        empty = True
        
        for well in sclf.groups[cath]:
            
            if well in swells:
                empty = False
                ########### get the values ################
                
                ## maximum ##
                try:
                    p_value= get_well_param(well, p_max_name)
                    p_max_n = p_value[npmax_idx]
                    
                    ## normalization parameter ##
                    p_max = p_value[pmax_idx]
                    p_norm = p_max/p_max_n
                
                except:
                    p_max_n = None
                    p_norm = None
                
                ## concentration ##
                con = con_values[well]
                units = con_units[well]
                
                ## append them ##
                con_list.append(con)
                units_list.append(units)
                pmax_values.append(p_max_n)
                pnorm_values.append(p_norm)
                s_well_list.append(well)
    
        if empty == False:
            
            ##  use just the mass concentration ##
            mass_con = list()
            mass_units = list()
            m_idx = 0          # 0: mass, 1: U
            
            for i in range(len(con_list)):
                con = con_list[i]
                unit = units_list[i]
                
                mass_con.append(con[m_idx])
                mass_units.append(unit[m_idx])
            
            ######################################
            #### create a Data_serie with them ###
    
            x_vals = mass_con
            y_vals = pmax_values
            serie_wells = s_well_list 
            serie_name = cath.value
    
            serie = Data_serie(x_vals, y_vals, serie_wells, serie_name)
            serie.x_units = mass_units 
            ### assign p_norm as an attribute ##
              
            #check if it is equal for all wells.
            round_pnorm = round_to_less(pnorm_values)
            #round_pnorm = rdm.round_to_less(pnorm_values)
            nr_norm = nr_list(round_pnorm , display = False)
            
            if len(nr_norm) == 1:  
                
                serie.norm_value = nr_norm[0]  #just as a single value
            
            else:
                serie.norm_value = pnorm_values # the whole list
            
            # add to the storage dictionary
            new_series[serie_name] = serie
            
            ## print some information
            print('\n'+ str(serie_name))
            print(len(mass_con), 'values were obtained:'+'\n')
            print('mass:',mass_con,'\n')
            print('Max:',pmax_values,'\n')
            print('normalization value:',serie.norm_value)
            print('-------------------------------------------')
    
    return(new_series)
    
def get_min_signal_series(dset, p_name = 'Amplification response region', 
                          p_idx = 0, read_name= 'Amplification data',
                          data_name = 'ΔRn'):
    """
    It created series using dset as template to create them.
    
    Parameter
    ---------
    
    p_name: string
        parameter name to choose the proper well.analysis  
    p_idx: int
        parameter index position in parameter.value
    read_name: str
        reading name to choose the proper well.data
    data_name: str
        data name to get values well.data[reading_index].values[data_name]
        
    Return
    ------
    new_series: dict
        dictionary with the created series for each classification
    
    """
    #######################################
    t_series = dset.series
    t_skeys = list(t_series.keys())
    
    ### get the values and create series ####
    
    new_series = dict()
    
    for key in t_skeys:
        t_serie = t_series[key]    
        s_name = t_serie.name
        s_norm = t_serie.norm_value
        
        s_well = list()
        s_x = list()
        s_y = list()
        
        wells = t_serie.well
        xs = t_serie.x
        
        for i in range(0,len(wells)):
            x_i =  xs[i]
            well_i = wells[i]
            
            s_well.append(well_i)
            s_x.append(x_i)
            
            ## get minimum value ###
            
            try:
                p_min = get_well_param(well_i, p_name)[p_idx]
                values, _ = get_well_reading(well_i, read_name, data_name)
                min_value = values[p_min]
                
                try:
                    min_nvalue = min_value/s_norm  # normalize it
                except:
                    print('it cannot be normalized')
                    min_nvalue = None
            
            except:
                min_value = None
                min_nvalue = None
            
            s_y.append(min_nvalue)
            
            ################################################
            ## assign min step signal as a well parameter ##
            ################################################
            # it's not actually necessary but could be useful
            minS_name = "min step signal"
            minS_descrip = "Signal value at the init of response region. [normalized, not normalized]"
            minS_p = Parameter(minS_name, minS_descrip, units = '[A.U]', 
                                   value =[min_nvalue, min_value], properties='')
            well_param_assignation(minS_p, well_i, ask = False)
            #################################################
    
        ######################################
        #### create a Data_serie with them ###
        
        serie = Data_serie(s_x, s_y, s_well, s_name)
        
        ## assign other serie attributes ##
        try:
            nr_units = nr_list(t_serie.x_units, display = False)
            if len(nr_units) == 1:
                serie.x_units = nr_units[0]
            else:
                serie.x_units = t_serie.x_units
        except:
            pass
        
        serie.norm_value = s_norm
    
        # add to the storage dictionary
        new_series[s_name] = serie
        
        ## print some information ##
        print('\n"'+ str(s_name)+'"')
        print(len(s_y), 'values were obtained:'+'\n')
        print('Min:',s_y,'\n')
        print('-------------------------------------------')
        
    return(new_series)
    
def log_tick_formatter(val, pos=None):
    return "{:.2e}".format(10**val)
