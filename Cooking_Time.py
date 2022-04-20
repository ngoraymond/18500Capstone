#1/8 inch = .75 minutes
#1/4 inch = 1.5 minutes
#1/2 inch = 3 minutes
#3/4 inch = 4.5 minutes

#object_name can be slab, round, or blob

def Get_Time(object_name, thickness) :
    if (object_name == "slab"): 
        return thickness *  6 * 60
    elif (object_name == "round") :
        return 90
    else :
        return 360