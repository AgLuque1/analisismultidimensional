# Own functions
from . import stringfunctions

# Python basics
import numpy as np
import pandas as pd

# Eda and Statistics
import seaborn as sns
import statsmodels.api as sm
import missingno as msno

# matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

"""
Function that manages all the plots generated in the machine learning app

Parameters:

plot_type: Type of plot that will be generated, it can be one of the following: missingValues, qqPlot, histogram, boxPlot, barPlot,
scatterPlot, barPlot2Cat (Bar plot filtered by all the different categories of data), rocCurve, confusionMatrix, 
standardPlot (regular matlotlib plot. One variable or two are allowed), regressionPlot (predicted values vs actual values)
data_parameters_dict: dictionary with the parameters that are used in the different plots. Those parameters depend on the plot that is going to be done:

missingValues - parameter data that contains a dataframe with the rows associated to the selected eda variable
qqPlot - parameters data (list with the data) and line (type of line that will be showed in plot)
histogram - parameters data (list with the data) and title (optional, string with the title)
boxPlot - parameters data (list with the data) and title (optional, string with the title)
barPlot - parameters data (list with the data) and title (optional, string with the title)
scatterPlot - parameters data, data2 (lists with data) and var1, var2 (names of variables that are going to be plot against)
barPlot2Cat - parameters data, data2 (lists with data) and var1, var2 (names of variables that are going to be plot against)
rocCurve - parameters title (string with the title), FPR, TPR (sorted FPR and TPR based on probabilities array order), probabilities (sorted probabilities)
confusionMatrix - parameters data (sklearn confusion matrix built with labels and predictions), xlabel and ylabel (strings with the labels of the axes)
standardPlot - parameters title (string with the title), data (list with data of the first variable), data2 (optional, list with data of the first variable), 
xlabel and ylabel (strings with the labels of the axes)
regressionPlot - parameters labels and predictions, lists that have this information

Return:

univariate_dict: string with png image of the plot

"""
def plot_ml(plot_type, data_parameters_dict):
    
    # Clear plot window
    plt.clf()
    
    if (plot_type == "missingValues"):
        
        msno.matrix(data_parameters_dict["data"], figsize=(8, 8))
        
    elif (plot_type == "qqPlot"):
        
        sm.qqplot(np.array(data_parameters_dict["data"]), line=data_parameters_dict["line"])
        
    elif (plot_type == "histogram"):
        
        g = sns.displot(data_parameters_dict["data"])

        if ("title" in data_parameters_dict):
            g.fig.subplots_adjust(top=.9, right=.9)
            g.fig.suptitle(data_parameters_dict["title"], fontdict={"weight": "bold"})
        
    elif (plot_type == "boxPlot"):

        if ("title" in data_parameters_dict):
            plt.title(data_parameters_dict["title"])
            
        sns.boxplot(x=data_parameters_dict["data"])
        
    elif (plot_type == "barPlot"):

        keys, counts = np.unique(data_parameters_dict["data"], return_counts=True)
        
        if ("title" in data_parameters_dict):
            plt.title(data_parameters_dict["title"])
            
        plt.bar(keys, counts)
        
    elif (plot_type == "scatterPlot"):
        
        # Scatter plot with regression line
        plt.plot(data_parameters_dict["data"], data_parameters_dict["data2"], 'o')
        m, b = np.polyfit(data_parameters_dict["data"], data_parameters_dict["data2"], 1) # regression line
        plt.plot(np.array(data_parameters_dict["data"]), m*np.array(data_parameters_dict["data"]) + b)
        plt.xlabel(data_parameters_dict["var"])
        plt.ylabel(data_parameters_dict["var2"])
        
    elif (plot_type == "barPlot2Cat"):
        
        # Build a dataframe with the values of both lists
        df_2cat = pd.DataFrame()
        df_2cat[data_parameters_dict["var1"]] = data_parameters_dict["data"]
        df_2cat[data_parameters_dict["var2"]] = data_parameters_dict["data2"]
        sns.histplot(binwidth=0.5, x=data_parameters_dict["var1"], hue=data_parameters_dict["var2"], data=df_2cat, stat="count", multiple="stack")
        
    elif (plot_type == "rocCurve"):
        
        plt.title(data_parameters_dict["title"])
        plt.plot(data_parameters_dict["FPR"], data_parameters_dict["TPR"])
        plt.plot([0,1],[0,1])
        plt.ylabel('TPR')
        plt.xlabel('FPR')

        # annotations
        for x,y,score in zip(data_parameters_dict["FPR"],data_parameters_dict["TPR"],(["Infinity"]+data_parameters_dict["probabilities"]+["-Infinity"])):

            if (str(type(score)) != "<class 'str'>"):
                label = "{:.5f}".format(score)
            else:
                label = "{lab}".format(lab = score)

            plt.annotate(label, # this is the text
                         (x,y), # these are the coordinates to position the label
                         textcoords="offset points", # how to position the text
                         xytext=(0,10), # distance from text to points (x,y)
                         ha='center') # horizontal alignment can be left, right or center
            
    elif (plot_type == "confusionMatrix"):
        
        sns.heatmap(data_parameters_dict["data"], annot=True).set(xlabel = data_parameters_dict["xlabel"], ylabel = data_parameters_dict["ylabel"])
        
    elif (plot_type == "standardPlot"):
        
        plt.title(data_parameters_dict["title"])
        plt.xlabel(data_parameters_dict["xlabel"])
        plt.ylabel(data_parameters_dict["ylabel"])
        
        if ("data2" in data_parameters_dict):
            plt.plot(data_parameters_dict["data"], data_parameters_dict["data2"])
            
        else:
            plt.plot(data_parameters_dict["data"])
            
    elif (plot_type == "regressionPlot"):
        
        plt.plot(list(range(len(data_parameters_dict["labels"]))), data_parameters_dict["labels"], marker='o', color='b', label="Valores reales")
        plt.plot(list(range(len(data_parameters_dict["predictions"]))), data_parameters_dict["predictions"], marker='o', color='orange', label="Valores predichos")
        plt.ylabel('Valor de regresión')
        plt.legend()
        plt.title("Gráfica de regresión, valores reales y predichos de la variable (ordenados por valor real)")
            
    # return the generated image
    return stringfunctions.get_image()