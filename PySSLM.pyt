import arcpy
from arcpy.sa import *
import sys, os
arcpy.CheckOutExtension("Spatial")


class Toolbox(object):
    def __init__(self):
        self.label = "PySSLM"
        self.alias  = "The Python Toolbox for Source Sink Landscape Model (SSLM)"

        # List of tool classes associated with this toolbox
        self.tools = [DEMFillFlowDirAcc,
                        FlowNetWork_AreaThreshold,
                        DelineateWatershed,
                        ExtractLUDEM,
                        CalculateDistanceSlope,
                        ConvertElevDistSlpLu2ASCII,
                        CalculateLorenzCurve,
                        PlotLorenzCurve,
                        CalculateLWLI] 

            

class DEMFillFlowDirAcc(object):
    def __init__(self):
        self.label       = "Step01_DEMFillFlowDirAcc"
        self.description = "This tool calls for the tools of hydrology " + \
                           "and provided an integrated tool to facilitate " + \
                           "watershed delineation."
        self.canRunInBackground = False


    def getParameterInfo(self):
        #Define parameter definitions

        # Input raster parameter
        in_dem = arcpy.Parameter(
            displayName="Input DEM Raster",
            name="in_dem",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
            
        # Input raster parameter
        ZFactor = arcpy.Parameter(
            displayName="Z Factor",
            name="ZFactor",
            datatype="GPString",
            parameterType="Required",
            direction="Input")           
            
        # Output raster parameter
        OutputFillDEM = arcpy.Parameter(
            displayName="Output Filled DEM Raster",
            name="OutputFillDEM",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
            
        # Output raster parameter
        OutputFlowDir = arcpy.Parameter(
            displayName="Output Flow Direction Raster",
            name="OutputFlowDir",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
            
        # Output raster parameter
        OutputFlowAcc = arcpy.Parameter(
            displayName="Output Flow Accumulation Raster",
            name="OutputFlowAcc",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")

            
        parameters = [in_dem,
                     ZFactor,
                     OutputFillDEM,
                     OutputFlowDir,
                     OutputFlowAcc]
        
        return parameters            
        
        
    def updateParameters(self, parameters): #optional

        import os
        in_dem = parameters[0].valueAsText
          
        # Z factor
        if (not parameters[1].altered):
            parameters[1].value=1
 
        # Output Parameter 2
        if in_dem and (not parameters[2].altered):
            if arcpy.Exists(in_dem):    
                desc = arcpy.Describe(in_dem)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[2].value=path+"\\DEMFill"
             
        # Output Parameter 1
        if in_dem and (not parameters[3].altered):
            if arcpy.Exists(in_dem):    
                desc = arcpy.Describe(in_dem)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[3].value=path+"\\D8FlowDir"             
             
        # Output Parameter 1
        if in_dem and (not parameters[4].altered):
            if arcpy.Exists(in_dem):    
                desc = arcpy.Describe(in_dem)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[4].value=path+"\\D8FlowAcc"             
             
        return  
        
        

    def updateMessages(self, parameters): #optional
        return        
        
        
        
    def execute(self, parameters, messages):

        # Define parameters	          
        DEM = parameters[0].valueAsText
        ZFactor = parameters[1].valueAsText
        OutputFillDEM = parameters[2].valueAsText
        OutputFlowDir = parameters[3].valueAsText
        OutputFlowAcc = parameters[4].valueAsText
        
        # Set environments
        arcpy.env.extent = DEM
        arcpy.env.snapRaster = DEM
        rDesc = arcpy.Describe(DEM)
        arcpy.env.cellSize = rDesc.meanCellHeight
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = arcpy.env.scratchFolder
        arcpy.env.outputCoordinateSystem = DEM
    
        if not arcpy.Exists(arcpy.env.workspace):
            arcpy.AddError("workspace does not exist!! Please set your workspace to a valid path directory in Arcmap --> Geoprocessing --> Environments --> Workspace")
            sys.exit(0)
            
        self.TerrainProcessing(
                        DEM, 
                        ZFactor, 
                        OutputFillDEM, 
                        OutputFlowDir, 
                        OutputFlowAcc)

    
    def TerrainProcessing(self, 
                        DEM, 
                        ZFactor, 
                        OutputFillDEM, 
                        OutputFlowDir, 
                        OutputFlowAcc):
    
        # Fill the cut DEM
        arcpy.AddMessage("Filling DEM")
        DEMFill = Fill(DEM)
        DEMFill.save(OutputFillDEM)
    
        arcpy.BuildPyramids_management(OutputFillDEM)
    
        # Calculate Flow Direction
        arcpy.AddMessage("Calculating D8 Flow Direction")
        D8FlowDir = FlowDirection(DEMFill, "", "")
        D8FlowDir.save(OutputFlowDir)
    
        arcpy.BuildPyramids_management(OutputFlowDir)
        
        # Calculate Flow Accumulation
        arcpy.AddMessage("Calculating Flow Accumulation")
        D8Accumulation = FlowAccumulation(D8FlowDir, "", "INTEGER")
        D8Accumulation.save(OutputFlowAcc)
    
        arcpy.BuildPyramids_management(OutputFlowAcc)
    
          
            





class FlowNetWork_AreaThreshold(object):
    def __init__(self):
        self.label       = "Step02_FlowNetworkDefinition_AreaThreshold"
        self.description = "This tool calls for the tools of hydrology " + \
                           "and provided an integrated tool to facilitate " + \
                           "watershed delineation."
        self.canRunInBackground = False


    def getParameterInfo(self):
        #Define parameter definitions

        # Input raster parameter
        in_d8flacc = arcpy.Parameter(
            displayName="Input D8 Flow Accumulation Raster",
            name="in_d8flacc",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
            
        # Input raster parameter
        in_d8fldir = arcpy.Parameter(
            displayName="Input D8 Flow Direction Raster",
            name="in_d8fldir",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
                        
        
        # Input raster parameter
        area_threshold = arcpy.Parameter(
            displayName="Area Threshold (ha)",
            name="area_threshold",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")           
            
        # Output raster parameter
        in_wsbdy = arcpy.Parameter(
            displayName="Input watershed boundary",
            name="in_wsbdy",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input")
                        
        # Output raster parameter
        out_flnetwork = arcpy.Parameter(
            displayName="Output flow network",
            name="out_flnetwork",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
            
            
        parameters = [in_d8flacc,
                     in_d8fldir,
                     area_threshold,
                     in_wsbdy,
                     out_flnetwork]
        
        return parameters            
        
        
    def updateParameters(self, parameters): #optional

        import os
        in_d8flacc = parameters[0].valueAsText
          
        # Input Parameter 1
        if in_d8flacc and (not parameters[1].altered):
            if arcpy.Exists(in_d8flacc):    
                desc = arcpy.Describe(in_d8flacc)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[1].value=path+"\\D8FlowDir"
                  
        # Output Parameter 4
        if in_d8flacc and (not parameters[4].altered):
            if arcpy.Exists(in_d8flacc):    
                desc = arcpy.Describe(in_d8flacc)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[4].value=path+"\\AreaFlowNet"
                  
        return  
        
        

    def updateMessages(self, parameters): #optional
        return        
        
        
        
    def execute(self, parameters, messages):

        # Define Parameters
        D8FlowAcc = parameters[0].valueAsText
        D8FlowDir = parameters[1].valueAsText
        AreaThreshold = parameters[2].valueAsText
        WBD = parameters[3].valueAsText
        OutFlowNet = parameters[4].valueAsText
    
        # Set environments
        arcpy.env.extent = D8FlowAcc
        arcpy.env.snapRaster = D8FlowAcc
        arcpy.env.overwriteOutput = True
        arcpy.env.outputCoordinateSystem = D8FlowAcc
        rDesc = arcpy.Describe(D8FlowAcc)
        arcpy.env.cellSize = rDesc.meanCellHeight
        arcpy.env.scratchWorkspace = arcpy.env.scratchFolder
    
        # Determine the cellsize and resolution of the input flow accumulation raster
        cellsize = float(arcpy.GetRasterProperties_management(D8FlowAcc, "CELLSIZEX").getOutput(0))
        resolution = float(cellsize * cellsize)

        if not arcpy.Exists(arcpy.env.workspace):
            arcpy.AddError("workspace does not exist!! Please set your workspace to a valid path directory in Arcmap --> Geoprocessing --> Environments --> Workspace")
            sys.exit(0)
    
        # Run Modules
        self.StreamNetByThreshold(D8FlowAcc, 
                                    D8FlowDir, 
                                    AreaThreshold, 
                                    resolution, 
                                    WBD,
                                    OutFlowNet)




    def StreamNetByThreshold(self, D8FlowAcc, 
                                    D8FlowDir, 
                                    AreaThreshold, 
                                    resolution, 
                                    WBD,
                                    OutFlowNet):
    
        # Convert area threshold from hectare (input) to meters: 1 ha = 10000 meters
        thresh_meters = float(AreaThreshold) * 10000
        number_cells = float(thresh_meters / resolution)
        arcpy.AddMessage("Area threshold of %s Ha...." % (AreaThreshold))
       
        # Threshold the flow accumulation raster using a CON statement and convert 0 background values to null
        FlowNetRas = Con(D8FlowAcc, 1, "", "VALUE >= %s" % number_cells)
    
        # Calculate Stream Order using FlowNetRas
        Order = StreamOrder(FlowNetRas, D8FlowDir, "STRAHLER")
    
        # Use the stream to feature to convert from raster to vector
        FlowNetwork = StreamToFeature(Order, D8FlowDir, OutFlowNet, "NO_SIMPLIFY")
    
        # Add StreamType field
        arcpy.AddField_management(FlowNetwork, "StreamType", "SHORT")
        arcpy.CalculateField_management(FlowNetwork, "StreamType","0","PYTHON","#")
    
        # Add Stream Order field
        arcpy.AddField_management(FlowNetwork, "STRAHLOrd", "LONG")
        arcpy.CalculateField_management(FlowNetwork, "STRAHLOrd", "!grid_code!", "PYTHON")
        arcpy.DeleteField_management(FlowNetwork, ["grid_code"])
    
        # Select only those segments that are centered in the WBD (if the WBD is provided)
        if WBD <> '':
            arcpy.MakeFeatureLayer_management(FlowNetwork, "flownet_fl")
            arcpy.SelectLayerByLocation_management("flownet_fl", "HAVE_THEIR_CENTER_IN", WBD)
            arcpy.SelectLayerByAttribute_management("flownet_fl", "SWITCH_SELECTION")
            arcpy.DeleteFeatures_management("flownet_fl")
     
        # Cleanup
        arcpy.Delete_management(FlowNetRas)
        arcpy.Delete_management(Order)
        del[FlowNetRas, Order]
    
    
    
    
    
    
    

class DelineateWatershed(object):
    def __init__(self):
        self.label       = "Step03_DelineateWatershed"
        self.description = "This tool calls for the tools of hydrology " + \
                           "and provided an integrated tool to facilitate " + \
                           "watershed delineation."
        self.canRunInBackground = False


    def getParameterInfo(self):
        #Define parameter definitions

        # Input raster parameter
        in_d8flacc = arcpy.Parameter(
            displayName="Input D8 Flow Accumulation Raster",
            name="in_d8flacc",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        # Input raster parameter
        in_d8flowdir = arcpy.Parameter(
            displayName="Input D8 flow direction Raster",
            name="in_d8flowdir",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        # Input feature parameter
        in_outlet = arcpy.Parameter(
            displayName="Input pour point/watershed outlet point shapefile",
            name="in_outlet",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
              
        
        # Input raster parameter
        snap_threshold = arcpy.Parameter(
            displayName="Snap Threshold",
            name="snap_threshold",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")           

        
        # Output raster parameter
        out_wsRas = arcpy.Parameter(
            displayName="Output Watershed Raster",
            name="out_wsRas",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
  
        parameters = [in_d8flacc,
                        in_d8flowdir,
                     in_outlet,
                     snap_threshold,
                     out_wsRas]
        
        return parameters            
        
        
    def updateParameters(self, parameters): #optional

        import os
        in_d8flacc = parameters[0].valueAsText
          
        # Output Parameter 1
        if in_d8flacc and (not parameters[1].altered):
            if arcpy.Exists(in_d8flacc):    
                desc = arcpy.Describe(in_d8flacc)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[1].value=path+"\\D8FlowDir"

        # Output Parameter 1
        if in_d8flacc and (not parameters[4].altered):
            if arcpy.Exists(in_d8flacc):    
                desc = arcpy.Describe(in_d8flacc)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[4].value=path+"\\WatershedRas"
   
        return  
        
        

    def updateMessages(self, parameters): #optional
        return        
        
        
        
    def execute(self, parameters, messages):

        # Define parameters
        inD8FlowAcc = parameters[0].valueAsText
        inD8FlowDir = parameters[1].valueAsText
        inOutlet = parameters[2].valueAsText
        snapThreshold = parameters[3].valueAsText
        outWSRas = parameters[4].valueAsText
        
        # Set environments
        arcpy.env.extent = inD8FlowAcc
        arcpy.env.snapRaster = inD8FlowAcc
        rDesc = arcpy.Describe(inD8FlowAcc)
        arcpy.env.cellSize = rDesc.meanCellHeight
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = arcpy.env.scratchFolder
        arcpy.env.outputCoordinateSystem = inD8FlowAcc
    
        if not arcpy.Exists(arcpy.env.workspace):
            arcpy.AddError("workspace does not exist!! Please set your workspace to a valid path directory in Arcmap --> Geoprocessing --> Environments --> Workspace")
            sys.exit(0)
            
        self.DelineatingWatershed(
                    inD8FlowAcc,
                    inD8FlowDir,
                    inOutlet,
                    snapThreshold,
                    outWSRas
                    )

    
    def DelineatingWatershed(self, 
                        inFlowAccum,
                        inD8FlowDir,
                        inPourPoint,
                        tolerance,
                        outWSRas):

        # First run the snap pour point tool
        pourField = "VALUE"
        
        # Execute SnapPourPoints
        outSnapPour = SnapPourPoint(inPourPoint, 
                                    inFlowAccum, 
                                    tolerance) 
        
        # Save the output 
        #outSnapPour.save("c:/sapyexamples/output/outsnpprpnt02")


        # Execute Watershed
        arcpy.AddMessage("Creating watershed!!!")
        outWatershed = Watershed(inD8FlowDir,
                                 outSnapPour)
        outWatershed.save(outWSRas)
                
        arcpy.BuildPyramids_management(outWSRas)
        
        # Cleanup
        arcpy.Delete_management(outSnapPour)
        del[outSnapPour]
    
    
    
    
    

class ExtractLUDEM(object):
    def __init__(self):
        self.label       = "Step04_ExtractLUDEM"
        self.description = "This tool clips dem and land use data to the " + \
                           "watershed area defined in the last step. They" + \
                           "were converted to ascii files. The program also" + \
                           "calculate the slope and distance from DEM and outlet"
        self.canRunInBackground = False


    def getParameterInfo(self):
        #Define parameter definitions

        # Input raster parameter
        in_wsRas = arcpy.Parameter(
            displayName="Input Delineated Watershed Raster",
            name="in_wsRas",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        # Input raster parameter
        in_demRas = arcpy.Parameter(
            displayName="Input DEM Raster",
            name="in_demRas",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        # Input feature parameter
        in_luRas = arcpy.Parameter(
            displayName="Input Landuse Raster",
            name="in_luRas",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
        
        # Output raster parameter
        out_demRas = arcpy.Parameter(
            displayName="Output DEM Raster for the Watershed area",
            name="out_demRas",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        
        # Output raster parameter
        out_luRas = arcpy.Parameter(
            displayName="Output Landuse Raster for the Watershed area",
            name="out_luRas",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")            
            
            
            
  
        parameters = [in_wsRas,
                      in_demRas,
                     in_luRas,
                     out_demRas,
                     out_luRas]
        
        return parameters            
        
        
    def updateParameters(self, parameters): #optional

        import os
        in_wsRas = parameters[0].valueAsText
          
        # Input Parameter 1: dem
        if in_wsRas and (not parameters[1].altered):
            if arcpy.Exists(in_wsRas):    
                desc = arcpy.Describe(in_wsRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[1].value=path+"\\dem"
          
        # Input Parameter 2
        if in_wsRas and (not parameters[2].altered):
            if arcpy.Exists(in_wsRas):    
                desc = arcpy.Describe(in_wsRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[2].value=path+"\\landuse"

        # Output Parameter 3
        if in_wsRas and (not parameters[3].altered):
            if arcpy.Exists(in_wsRas):    
                desc = arcpy.Describe(in_wsRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[3].value=path+"\\demWS"
   
        # Output Parameter 4
        if in_wsRas and (not parameters[4].altered):
            if arcpy.Exists(in_wsRas):    
                desc = arcpy.Describe(in_wsRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[4].value=path+"\\LanduseWS"
      
        return  
        
        

    def updateMessages(self, parameters): #optional
        return        
        
        
        
    def execute(self, parameters, messages):

        # Define parameters
        inwsRas = parameters[0].valueAsText
        indemRas = parameters[1].valueAsText
        inluRas = parameters[2].valueAsText
        outDemWs = parameters[3].valueAsText
        outLuWs = parameters[4].valueAsText
        
        # Set environments
        arcpy.env.extent = inwsRas
        arcpy.env.snapRaster = inwsRas
        rDesc = arcpy.Describe(inwsRas)
        arcpy.env.cellSize = rDesc.meanCellHeight
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = arcpy.env.scratchFolder
        arcpy.env.outputCoordinateSystem = inwsRas
    
        if not arcpy.Exists(arcpy.env.workspace):
            arcpy.AddError("workspace does not exist!! Please set your workspace to a valid path directory in Arcmap --> Geoprocessing --> Environments --> Workspace")
            sys.exit(0)
            
        self.funExtractLUDEM(
                    inwsRas,
                    indemRas,
                    inluRas,
                    outDemWs,
                    outLuWs
                    )

    
    def funExtractLUDEM(self, 
                        inWsRas,
                        indemRas,
                        inluRas,
                        outDemWs,
                        outLuWs):

        # Execute ExtractByMask
        arcpy.AddMessage("Extracting DEM!!!")
        outDemWatershed = ExtractByMask(indemRas, inWsRas)
        
        # Save the output 
        outDemWatershed.save(outDemWs)
                        
        arcpy.BuildPyramids_management(outDemWs)
        
        # Execute ExtractByMask
        arcpy.AddMessage("Extracting Landuse!!!")
        outLuWatershed = ExtractByMask(inluRas, inWsRas)
        
        # Save the output 
        outLuWatershed.save(outLuWs)
                        
        arcpy.BuildPyramids_management(outLuWs)
        


    

class CalculateDistanceSlope(object):
    def __init__(self):
        self.label       = "Step05_CalculateDistanceSlope"
        self.description = "This tool calculate distance and slope from " + \
                           "dem of the watershed area defined in the last step." + \
                           "The calculation used the path distance tool and " + \
                           "the slope tool."
        self.canRunInBackground = False


    def getParameterInfo(self):
        #Define parameter definitions

        # Input raster parameter
        in_demRas = arcpy.Parameter(
            displayName="Input DEM Raster",
            name="in_demRas",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")


        # Input feature parameter
        in_outlet = arcpy.Parameter(
            displayName="Input pour point/watershed outlet",
            name="in_outlet",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
                  
        
        # Output raster parameter
        out_DistRas = arcpy.Parameter(
            displayName="Output Distance Raster",
            name="out_DistRas",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        
        # Output raster parameter
        out_SlpRas = arcpy.Parameter(
            displayName="Output Slope Raster",
            name="out_SlpRas",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")            
            
            
            
  
        parameters = [in_demRas,
                      in_outlet,
                     out_DistRas,
                     out_SlpRas]
        
        return parameters            
        
        
    def updateParameters(self, parameters): #optional

        import os
        in_demRas = parameters[0].value
          
        # Input Parameter 1: dem
        if in_demRas and (not parameters[2].altered):
            if arcpy.Exists(in_demRas):    
                desc = arcpy.Describe(in_demRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[2].value=path+"\\DistanceWS"
          
        # Input Parameter 2
        if in_demRas and (not parameters[3].altered):
            if arcpy.Exists(in_demRas):    
                desc = arcpy.Describe(in_demRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[3].value=path+"\\SlopeWS"
      
      
      
        return  
        
        

    def updateMessages(self, parameters): #optional
        return        
        
        
        
    def execute(self, parameters, messages):

        # Define parameters
        inDemRas = parameters[0].valueAsText
        inOutlet = parameters[1].valueAsText
        outDistRas = parameters[2].valueAsText
        outSlpRas = parameters[3].valueAsText
        
        # Set environments
        arcpy.env.extent = inDemRas
        arcpy.env.snapRaster = inDemRas
        rDesc = arcpy.Describe(inDemRas)
        arcpy.env.cellSize = rDesc.meanCellHeight
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = arcpy.env.scratchFolder
        arcpy.env.outputCoordinateSystem = inDemRas
    
        if not arcpy.Exists(arcpy.env.workspace):
            arcpy.AddError("workspace does not exist!! Please set your workspace to a valid path directory in Arcmap --> Geoprocessing --> Environments --> Workspace")
            sys.exit(0)
            
        self.funCalDistSlope(
                    inDemRas,
                    inOutlet,
                    outDistRas,
                    outSlpRas
                    )

    
    def funCalDistSlope(self, 
                         inDemRas,
                    inOutlet,
                    outDistRas,
                    outSlpRas):

        
        # Set local variables
        inSource = inOutlet
        inElev = inDemRas

        # Execute PathDistance
        arcpy.AddMessage("Calculating distance!!!")
        outPathDist = PathDistance(inSource, inElev)
        
        # Execute PathDistance
        outPathDist = PathDistance(inOutlet, "", inDemRas, "", 
                           "", "", "", 
                           "", "")
        
        
        # Save the output 
        outPathDist.save(outDistRas)
                        
        arcpy.BuildPyramids_management(outDistRas)
        

        # Calculate slope
        # Set local variables
        outMeasurement = "DEGREE"

        # Execute Slope
        arcpy.AddMessage("Calculating slope!!!")
        outSlope = Slope(inDemRas, outMeasurement)
        
        # Save the output 
        outSlope.save(outSlpRas)

        arcpy.BuildPyramids_management(outSlpRas)
        

            
    

class ConvertElevDistSlpLu2ASCII(object):
    def __init__(self):
        self.label       = "Step06_ConvertElevDistSlpLu2ASCII"
        self.description = "This tool convert the dem, distance, slope, and " + \
                           "land use of the watershed area defined in the " + \
                           "last step into ASCII files for future calculation " + \
                           "in LWLI."
        self.canRunInBackground = False


    def getParameterInfo(self):
        #Define parameter definitions

        # Input raster parameter
        in_demRas = arcpy.Parameter(
            displayName="Input DEM Raster for the watershed",
            name="in_demRas",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
        
        # Output raster parameter
        in_DistRas = arcpy.Parameter(
            displayName="Input Distance Raster for the watershed",
            name="in_DistRas",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
        
        # Output raster parameter
        in_SlpRas = arcpy.Parameter(
            displayName="Input Slope Raster for the watershed",
            name="in_SlpRas",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")            
            
        # Output raster parameter
        in_LuRas = arcpy.Parameter(
            displayName="Input Landuse Raster for the watershed",
            name="in_LuRas",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input") 

                      
                        
  
        parameters = [in_demRas,
                      in_DistRas,
                      in_SlpRas,
                      in_LuRas]
        
        return parameters            
        
        
    def updateParameters(self, parameters): #optional

        import os
        in_demRas = parameters[0].valueAsText
          
        # Input Parameter 1: distance raster
        if in_demRas and (not parameters[1].altered):
            if arcpy.Exists(in_demRas):    
                desc = arcpy.Describe(in_demRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[1].value=path+"\\DistanceWS"
          
        # Input Parameter 2: slope raster
        if in_demRas and (not parameters[2].altered):
            if arcpy.Exists(in_demRas):    
                desc = arcpy.Describe(in_demRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[2].value=path+"\\SlopeWS"
          
      
        # Input Parameter 3: land use raster
        if in_demRas and (not parameters[3].altered):
            if arcpy.Exists(in_demRas):    
                desc = arcpy.Describe(in_demRas)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[3].value=path+"\\landusews"
                
             
            
        return  
        
        

    def updateMessages(self, parameters): #optional
        return        
        
        
        
    def execute(self, parameters, messages):

        # Define parameters
        inDemRas = parameters[0].valueAsText
        inDistRas = parameters[1].valueAsText
        inSlpRas = parameters[2].valueAsText
        inLuRas = parameters[3].valueAsText
        
        desc = arcpy.Describe(inDemRas)
        infile=str(desc.catalogPath) 
        path,filename = os.path.split(infile)
        
        outDemAsc=path+"\\demws.txt"
        outDistAsc=path+"\\distws.txt"
        outSlpAsc=path+"\\slopews.txt"
        outLuAsc=path+"\\luws.txt"
        
        os.remove(outDemAsc) if os.path.exists(outDemAsc) else None
        os.remove(outDistAsc) if os.path.exists(outDistAsc) else None
        os.remove(outSlpAsc) if os.path.exists(outSlpAsc) else None
        os.remove(outLuAsc) if os.path.exists(outLuAsc) else None

        # Set environments
        arcpy.env.extent = inDemRas
        arcpy.env.snapRaster = inDemRas
        rDesc = arcpy.Describe(inDemRas)
        arcpy.env.cellSize = rDesc.meanCellHeight
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = arcpy.env.scratchFolder
        arcpy.env.outputCoordinateSystem = inDemRas
    
        if not arcpy.Exists(arcpy.env.workspace):
            arcpy.AddError("workspace does not exist!! Please set your workspace to a valid path directory in Arcmap --> Geoprocessing --> Environments --> Workspace")
            sys.exit(0)
            
        self.funRast2Ascii(
                            inDemRas,
                            inDistRas,
                            inSlpRas,
                            inLuRas,
                            outDemAsc,
                            outDistAsc,
                            outSlpAsc,
                            outLuAsc
                            )

    
    def funRast2Ascii(self, 
                             inDemRas,
                            inDistRas,
                            inSlpRas,
                            inLuRas,
                            outDemAsc,
                            outDistAsc,
                            outSlpAsc,
                            outLuAsc):

        # Execute RasterToASCII
        arcpy.RasterToASCII_conversion(inDemRas, outDemAsc)
                    
        # Execute RasterToASCII
        arcpy.RasterToASCII_conversion(inDistRas, outDistAsc)
                    
        # Execute RasterToASCII
        arcpy.RasterToASCII_conversion(inSlpRas, outSlpAsc)
                    
        # Execute RasterToASCII
        arcpy.RasterToASCII_conversion(inLuRas, outLuAsc)                                        
                                   
                                   
                                   
                                   
                                        

class CalculateLorenzCurve(object):
    def __init__(self):
        self.label       = "Step07_CalculateLorenzCurve"
        self.description = "This tool takes the ascii files of elevation, " + \
                           "distance and slope as input files, generate " + \
                           "figures for LWLI and calculate the LWLI value " + \
                           "."
        self.canRunInBackground = False


    def getParameterInfo(self):
        #Define parameter definitions
            
        # Input Ascii parameter
        in_demAsc = arcpy.Parameter(
            displayName="Input DEM Ascii",
            name="in_demAsc",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")
            
        # Input text parameters
        in_SrcLunos = arcpy.Parameter(
            displayName="Input file containing list of source landuse",
            name="in_SrcLunos",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")             
                      
        # Input text parameters
        in_SinkLunos = arcpy.Parameter(
            displayName="Input file containing list of sink Landuse",
            name="in_SinkLunos",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")   

        parameters = [in_demAsc,
                     in_SrcLunos,
                     in_SinkLunos]
        
        return parameters            
        
        
    def updateParameters(self, parameters): #optional          
            
        import os
        in_demAsc = parameters[0].valueAsText
          
        # Input Parameter 1: distance asc
        if in_demAsc and (not parameters[1].altered):
            if arcpy.Exists(in_demAsc):    
                desc = arcpy.Describe(in_demAsc)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[1].value=path+"\\srclus.txt"
          
        # Input Parameter 2: slope raster
        if in_demAsc and (not parameters[2].altered):
            if arcpy.Exists(in_demAsc):    
                desc = arcpy.Describe(in_demAsc)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[2].value=path+"\\sinklus.txt"
            
            
        return  
        
        

    def updateMessages(self, parameters): #optional
        return        
        
        
        
    def execute(self, parameters, messages):

        # Define parameters
        inDemAsc = parameters[0].valueAsText
        inSrcfn = parameters[1].valueAsText
        inSinkfn = parameters[2].valueAsText
        
        
        if not os.path.exists(inSrcfn):
            arcpy.AddError("File for source land uses does not exist") 
            
        if not os.path.exists(inSinkfn):
            arcpy.AddError("File for sink land uses does not exist") 

        self.funCalculateLWLI(
                            inDemAsc,
                            inSrcfn,
                            inSinkfn)

    
    def funCalculateLWLI(self, 
                        inDemAsc,
                        inSrcfn,
                        inSinkfn):

        # From here, we need to get the modules in another class
        # Create instance of class

        # Here, I will first write all of these into a text file.
        # Then, use C++ to read them for further process.
        # After clossing, we will call the c++ program to do the
        # calculation
        import os
        
        # Then, copy the lwlicaltool to the folder and 
        # run it.
        
        arcpy.AddMessage("Computing LWLI")
        # Input Parameter 1: distance raster
        if arcpy.Exists(inDemAsc):    
            desc = arcpy.Describe(inDemAsc)
            infile=str(desc.catalogPath) 
            path,filename = os.path.split(infile)
        
        os.chdir(path)
        import subprocess  
        subprocess.Popen([r"SSLM.exe"])
        #os.system("VS16_LWLICal.exe")
        arcpy.AddMessage("Finished computing LWLI")
        




class PlotLorenzCurve(object):
    def __init__(self):
        self.label       = "Step08_PlotLorenzCurve"
        self.description = "This tool takes the output of the LwliCal tool, " + \
                           "and makes figures of Lorenz Curve from them " + \
                           " " + \
                           "."
        self.canRunInBackground = False


    def getParameterInfo(self):
        #Define parameter definitions
            
        # Input Ascii parameter
        in_elevTxt = arcpy.Parameter(
            displayName="Input elev_dataperc (outputs from step 7)",
            name="in_elevTxt",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")       

        # Input Ascii parameter
        in_slpTxt = arcpy.Parameter(
            displayName="Input slp_dataperc (outputs from step 7)",
            name="in_slpTxt",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")       

        # Input Ascii parameter
        in_distTxt = arcpy.Parameter(
            displayName="Input dist_dataperc (outputs from step 7)",
            name="in_distTxt",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")       

        # Input text parameters
        in_SrcLunos = arcpy.Parameter(
            displayName="Input file containing list of source landuse",
            name="in_SrcLunos",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")             
                      
        # Input text parameters
        in_SinkLunos = arcpy.Parameter(
            displayName="Input file containing list of sink Landuse",
            name="in_SinkLunos",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")   

            
        # Output raster parameter
        out_elevfig = arcpy.Parameter(
            displayName="Output figure file name for elevation",
            name="out_elevfig",
            datatype="GPString",
            parameterType="Required",
            direction="Output")       
            
        
        # Output raster parameter
        out_distfig = arcpy.Parameter(
            displayName="Output figure file name for distance",
            name="out_distfig",
            datatype="GPString",
            parameterType="Required",
            direction="Output")          
        
        
        # Output raster parameter
        out_slpfig = arcpy.Parameter(
            displayName="Output figure file name for slope",
            name="out_slpfig",
            datatype="GPString",
            parameterType="Required",
            direction="Output")              
            
            
        parameters = [in_elevTxt,
                        in_slpTxt,
                        in_distTxt,
                        in_SrcLunos,
                        in_SinkLunos,                     
                        out_elevfig,
                        out_distfig,
                        out_slpfig]
        
        return parameters            
        
        
    def updateParameters(self, parameters): #optional
            
        import os
        in_elevTxt = parameters[0].valueAsText
          
        # Input Parameter 1: slope value percent
        if in_elevTxt and (not parameters[1].altered):
            if arcpy.Exists(in_elevTxt):    
                desc = arcpy.Describe(in_elevTxt)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[1].value=path+"\\slp_dataperc.txt"
          
        # Input Parameter 2: distance value percent
        if in_elevTxt and (not parameters[2].altered):
            if arcpy.Exists(in_elevTxt):    
                desc = arcpy.Describe(in_elevTxt)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[2].value=path+"\\dist_dataperc.txt"
            
            
        # Input Parameter 3: source lus
        if in_elevTxt and (not parameters[3].altered):
            if arcpy.Exists(in_elevTxt):    
                desc = arcpy.Describe(in_elevTxt)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[3].value=path+"\\srclus.txt"
          
          
        # Input Parameter 4: sink lus
        if in_elevTxt and (not parameters[4].altered):
            if arcpy.Exists(in_elevTxt):    
                desc = arcpy.Describe(in_elevTxt)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[4].value=path+"\\sinklus.txt"
 
        # Output Parameter 5: elevatioin figure name
        if in_elevTxt and (not parameters[5].altered):
            if arcpy.Exists(in_elevTxt):    
                desc = arcpy.Describe(in_elevTxt)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[5].value=path+"\\lzelev.png"
          
        # Output Parameter 6: distance figure name
        if in_elevTxt and (not parameters[6].altered):
            if arcpy.Exists(in_elevTxt):    
                desc = arcpy.Describe(in_elevTxt)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[6].value=path+"\\lzdist.png"            
            
            
        # Output Parameter 7: slope figure name
        if in_elevTxt and (not parameters[7].altered):
            if arcpy.Exists(in_elevTxt):    
                desc = arcpy.Describe(in_elevTxt)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[7].value=path+"\\lzslp.png"            
                        
        return  
        
        

    def updateMessages(self, parameters): #optional
        return        
        

        
    def execute(self, parameters, messages):

        # Define parameters
        inelevTxt = parameters[0].valueAsText
        inslpTxt = parameters[1].valueAsText
        indistTxt = parameters[2].valueAsText
        insrcTxt = parameters[3].valueAsText
        insinkTxt = parameters[4].valueAsText        
        outelevfig = parameters[5].valueAsText
        outdistfig = parameters[6].valueAsText
        outslpfig = parameters[7].valueAsText        
               
        
        self.funPlotLorenzCurve(
                        inelevTxt,
                        inslpTxt,
                        indistTxt,
                        insrcTxt,
                        insinkTxt,
                        outelevfig,
                        outdistfig,
                        outslpfig)

    
    def funPlotLorenzCurve(self, 
                        inelevTxt,
                        inslpTxt,
                        indistTxt,
                        insrcTxt,
                        insinkTxt,
                        outelevfig,
                        outdistfig,
                        outslpfig):

        # From here, we need to get the modules in another class
        # Create instance of class

        # Here, the AppLorenzCurve class need to be initalized 
        # for making curves of LorenzCurve from the LWLI data.
        import os
        LCApp = AppLorenzCurve()


        # Call the function to make the plots
        LCApp.plotting(inelevTxt,outelevfig, "Elevation(m)", "Accumulated percent of\n area (%)", insinkTxt, insrcTxt)
        LCApp.plotting(indistTxt,outdistfig, "Distance(m)", "Accumulated percent of\n area (%)", insinkTxt, insrcTxt)
        LCApp.plotting(inslpTxt,outslpfig, "Slope(degree)", "Accumulated percent of\n area (%)", insinkTxt, insrcTxt)
        
        





class CalculateLWLI(object):
    def __init__(self):
        self.label       = "Step09_CalculateLWLI"
        self.description = "This tool takes output of step 7 and calculate, " + \
                           "the combined lwli from the distance, slope, and elevation " + \
                           "for all sink and source land uses" + \
                           "."
        self.canRunInBackground = False



    def getParameterInfo(self):
        #Define parameter definitions
            
        # Input lu area file
        in_luareaper = arcpy.Parameter(
            displayName="Input luareaperc.txt (outputs from step 7)",
            name="in_luareaper",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input") 

     
        # Input lurenz curve file
        in_filelz = arcpy.Parameter(
            displayName="Input LurenzCurveAreas.txt (outputs from step 7)",
            name="in_filelz",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")                   

        # Input text parameters
        in_SrcLuWeights = arcpy.Parameter(
            displayName="Input text file containing weights for source landuses",
            name="in_SrcLuWeights",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")             
                      
        # Input text parameters
        in_SinkLuWeights = arcpy.Parameter(
            displayName="Input text file containing weights for sink landuses",
            name="in_SinkLuWeights",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")   
            
        parameters = [in_luareaper,
                        in_filelz,
                        in_SrcLuWeights,
                        in_SinkLuWeights]
        
        return parameters       


    def updateParameters(self, parameters): #optional
                     
        import os
        in_filelz = parameters[0].valueAsText
          
        # Input Parameter 1: file containing area under lorenz curve
        if in_filelz and (not parameters[1].altered):
            if arcpy.Exists(in_filelz):    
                desc = arcpy.Describe(in_filelz)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[1].value=path+"\\LurenzCurveAreas.txt"
   
        # Input Parameter 2: file containing area under lorenz curve
        if in_filelz and (not parameters[2].altered):
            if arcpy.Exists(in_filelz):    
                desc = arcpy.Describe(in_filelz)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[2].value=path+"\\srclus_withweights.txt"   
   
        # Input Parameter 3: file containing area under lorenz curve
        if in_filelz and (not parameters[3].altered):
            if arcpy.Exists(in_filelz):    
                desc = arcpy.Describe(in_filelz)
                infile=str(desc.catalogPath) 
                path,filename = os.path.split(infile)
                parameters[3].value=path+"\\sinklus_withweights.txt"
                
                
                                         
        return  


    def updateMessages(self, parameters): #optional
        return        
        

        
    def execute(self, parameters, messages):
        
        # Define parameters
        inluareaper = parameters[0].valueAsText
        inlzareaper = parameters[1].valueAsText
        inSrcLuWeights = parameters[2].valueAsText
        inSinkLuWeights = parameters[3].valueAsText
              
        desc = arcpy.Describe(inluareaper)
        infile=str(desc.catalogPath) 
        path,filename = os.path.split(infile)
        
        outfLWLIs = path+"\\finallwlis.txt"
        os.remove(outfLWLIs) if os.path.exists(outfLWLIs) else None
              
        self.funCalLWLI(inluareaper,
                        inlzareaper,
                        inSrcLuWeights,
                        inSinkLuWeights,
                        outfLWLIs)


    def funCalLWLI(self, 
                        inluareaper,
                        inlzareaper,
                        inSrcLuWeights,
                        inSinkLuWeights,
                        outfLWLIs):

        # There are four files to read 
        fidluarea = open(inluareaper, "r")
        lifluarea = fidluarea.readlines()
        fidluarea.close()
        
        sinlus = {}
        srclus = {}
                        
        # Processing lines:
        del lifluarea[0:2]

        for luidx in range (len(lifluarea)):
            lifluarea[luidx] = lifluarea[luidx].split(",")
            lifluarea[luidx][-1] = lifluarea[luidx][-1][:-1]
            lifluarea[luidx][0] = lifluarea[luidx][0].split("_")
            
            if "Sink" in lifluarea[luidx][0]:
                sinlus[float(lifluarea[luidx][0][1])] = [float(lifluarea[luidx][2])]
            elif "Source" in lifluarea[luidx][0]:
                srclus[float(lifluarea[luidx][0][1])] = [float(lifluarea[luidx][2])]
                

        fidlzarea = open(inlzareaper, "r")
        liflzarea = fidlzarea.readlines()
        fidlzarea.close()
        
        # Processing lines:
        del liflzarea[0:2]

        for lzidx in range (len(liflzarea)):
            liflzarea[lzidx] = liflzarea[lzidx].split(",")
            liflzarea[lzidx][-1] = liflzarea[lzidx][-1][:-1]
            liflzarea[lzidx][0] = liflzarea[lzidx][0].split("_")
            
            if float(liflzarea[lzidx][0][1]) in sinlus.keys():
                sinlus[float(liflzarea[lzidx][0][1])].append(map(float, liflzarea[lzidx][1:]))
            elif float(liflzarea[lzidx][0][1]) in srclus.keys():
                srclus[float(liflzarea[lzidx][0][1])].append(map(float, liflzarea[lzidx][1:]))


        # Processing weightes:
        fidsrcweights = open(inSrcLuWeights, "r")
        lifsrcweights = fidsrcweights.readlines()
        fidsrcweights.close()

        fidsinkweights = open(inSinkLuWeights, "r")
        lifsinkweights = fidsinkweights.readlines()
        fidsinkweights.close()        
        
        del(lifsrcweights[0])
        del(lifsinkweights[0])
        
        for srcwid in range(len(lifsrcweights)):
            lifsrcweights[srcwid] = lifsrcweights[srcwid].split(",")
            lifsrcweights[srcwid][-1] = lifsrcweights[srcwid][-1][:-1]
            
            if float(lifsrcweights[srcwid][0]) in srclus.keys():
                srclus[float(lifsrcweights[srcwid][0])].append(lifsrcweights[srcwid][1])
            else:
                arcpy.AddError("The source land use you entered does not match the former inputs, please check!!")
                sys.exit(0)
        
        for sinkwid in range(len(lifsinkweights)):
            lifsinkweights[sinkwid] = lifsinkweights[sinkwid].split(",")
            lifsinkweights[sinkwid][-1] = lifsinkweights[sinkwid][-1][:-1]
        
            if float(lifsinkweights[sinkwid][0]) in sinlus.keys():
                sinlus[float(lifsinkweights[sinkwid][0])].append(lifsinkweights[sinkwid][1])
            else:
                arcpy.AddError("The sink land use you entered does not match the former inputs, please check!!")
                sys.exit(0)     
                


        # Then do the calculation for each lwli and combined lwli
        #srclwlis = [elev[srclu1, srclu2,...], dist[], slp[]]
        srclwlis = []
        


        for ftidx in range (3):
            templwli = []
            for srckid in srclus.keys():
                # prodwaap: product of weight, area under lorenz curve, and area per
                prodwaap = 0
                prodwaap = float(srclus[srckid][0])*float(srclus[srckid][2])*float(srclus[srckid][1][ftidx])
                templwli.append(prodwaap)
            srclwlis.append(templwli)    
            

        #sinklwlis = [elev[sinklu1, sinklu2,...], dist[], slp[]]
        sinklwlis = []
        for ftidx2 in range(3):
            # templwli2 is a list containing the lwli for three variables for each landuse
            templwli2 = []        
            for sinkid in sinlus.keys():
                # prodwaap2: product of weight, area under lorenz curve, and area per
                prodwaap2 = 0
                prodwaap2 = float(sinlus[sinkid][0])*float(sinlus[sinkid][2])*float(sinlus[sinkid][1][ftidx2])
                templwli2.append(prodwaap2)
                
            sinklwlis.append(templwli2) 

        lwlielev = 0
        lwlidist = 0
        lwlislp = 0
        
        lwlielev = sum(srclwlis[0])/(sum(srclwlis[0])+sum(sinklwlis[0]))
        lwlidist = sum(srclwlis[1])/(sum(srclwlis[1])+sum(sinklwlis[1]))
        lwlislp = sum(srclwlis[2])/(sum(srclwlis[2])+sum(sinklwlis[2]))
            
        lwlicomb = lwlielev*lwlidist/lwlislp

        # Write output files 
        os.remove(outfLWLIs) if os.path.exists(outfLWLIs) else None
        fout = open(outfLWLIs, "w")
        fout.writelines("LWLI Values\n")
        fout.writelines("LWLI for elevation\t%f\n" %(lwlielev))
        fout.writelines("LWLI for distance\t%f\n" %(lwlidist))
        fout.writelines("LWLI for slope\t%f\n" %(lwlislp))
        fout.writelines("LWLI combined\t%f\n" %(lwlicomb))
        
        fout.close()
        


class AppLorenzCurve(object):

    def readvaluepercent(self, filename):
    
        fid = open(filename, "r")
        lif = fid.readlines()
        fid.close()
        
        lslanduse = []
        lsvalue = []
        lspercent = []
        
        for lidx in range(1, len(lif), 4):
            lslanduse.append(lif[lidx].split(":")[1][:-1])
            temp = []
            lif[lidx+1] = lif[lidx+1].split(",")
            lif[lidx+1][-1] = lif[lidx+1][-1][:-1]
            temp = map(float, lif[lidx+1])
            lsvalue.append(temp)
            temp = []
            lif[lidx+3] = lif[lidx+3].split(",")
            lif[lidx+3][-1] = lif[lidx+3][-1][:-1]
            temp = map(float, lif[lidx+3])
            lspercent.append(temp)
            
        lslanduse = map(int, lslanduse)
            
        return lslanduse, lsvalue, lspercent


    def readlutxt(self, filename):
        
        fid = open(filename, "r")
        lif = fid.readlines()
        fid.close()

        for idx in range(len(lif)):
            lif[idx] = int(lif[idx][:-1])
    
        return lif
    
    


    def plotting(self, 
            fndata,
            fnoutfig,
            xlabeltext,
            ylabeltext,
            sinklus,
            srclus
            ):
        
        import matplotlib.pyplot as plt
        
        # Read the value from the text files containing the 
        # value and percentage for elevation.
        lulist, valuelist, perlist = self.readvaluepercent(fndata)
        
        srclu = self.readlutxt(srclus)
        sinklu = self.readlutxt(sinklus)

        max_value = valuelist[0][-1]
        min_value = valuelist[0][0]
        
        for eidx in range (1, len(valuelist)):
            if (valuelist[eidx][0] < min_value):
                min_value = valuelist[eidx][0]

        for eidx2 in range (1, len(valuelist)):
            if (valuelist[eidx2][-1] > max_value):
                max_value = valuelist[eidx2][-1]
        
        
        # Start plotting
        fig = plt.figure(figsize=(9,7), 
                         dpi=300)

        ax = fig.add_subplot(111)
        
        
        
        # Plot for all lines
        # Plot srclu: 
        for lidx in range(len(lulist)):
            if (lulist[lidx] in srclu):
                ax.plot(valuelist[lidx], perlist[lidx], linewidth=2.0, label=str(lulist[lidx]))
        
        # Plot sinklu: make it dash
        for lidx in range(len(lulist)):
            if (lulist[lidx] in sinklu):
                ax.plot(valuelist[lidx], perlist[lidx], linewidth=2.0, linestyle="--", label=str(lulist[lidx]))
                
        
        
        # Control legend
        legd = ax.legend(loc="center left", 
               bbox_to_anchor=[1, 0.5],
               ncol=1, 
               shadow=False, 
               title="Land use",
               fontsize = 15) 
        art = []
        art.append(legd)
        
        box = ax.get_position()
        # setposition(left, bottom, width, height)
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
        # Control label
        # set: a property batch setter
        # set_xlabel(xlabel, labelpad, **kwargs)
        ax.set_xlabel(xlabeltext, fontsize=35)
        ax.set_ylabel(ylabeltext, fontsize=35)

        # Control grids
        ax.grid()
                
        # Control ticks
        ax.set_xlim(left=min_value, 
                  right=max_value)

        ax.set_ylim(bottom=0, 
                    top=100)
        
        ax.tick_params(labelsize=25)

        

        fig.savefig(fnoutfig, additional_artists=art,bbox_inches="tight")
        
       









    # This function is not used anymore
    def plottingold(self, 
            fn_elevdt,fn_distdt,fn_slpdt,
            fig_elev, fig_dist, fig_slp):
        
        import matplotlib.pyplot as plt
	import matplotlib

        xlabelfontsize = 20
        ylabelfontsize = 20
        tickfontsize = 20
        legendfontsize = 18
        legend_properties = {'weight':'light'}
        xytickfontproperties = {'family':'sans-serif',
                                'sans-serif':['Helvetica'],
                                'weight' : 'light',
                                'size' : tickfontsize}
    	figuresize = (9,7)
	
	
        elevlu, elevval, elevperc = self.readvaluepercent(fn_elevdt)
        slplu, slpval, slpperc = self.readvaluepercent(fn_slpdt)
        distlu, distval, distperc = self.readvaluepercent(fn_distdt)
  
    	max_elev = elevval[0][-1]
        max_slp = slpval[0][-1]
        max_dist = distval[0][-1]

        min_elev = elevval[0][0]
        min_slp = slpval[0][0]
        min_dist = distval[0][0]

        for didx in range (1, len(distval)):
            if (distval[didx][0] < min_dist):
                min_dist = distval[didx][0]

        for sidx in range (1, len(slpval)):
            if (slpval[sidx][0] < min_slp):
                min_slp = slpval[sidx][0]

        for eidx in range (1, len(elevval)):
            if (elevval[eidx][0] < min_elev):
                min_elev = elevval[eidx][0]


        for didx2 in range (1, len(distval)):
            if (distval[didx2][-1] > max_dist):
                max_dist = distval[didx2][-1]

        for sidx2 in range (1, len(slpval)):
            if (slpval[sidx2][-1] > max_slp):
                max_slp = slpval[sidx2][-1]

        for eidx2 in range (1, len(elevval)):
            if (elevval[eidx2][-1] > max_elev):
                max_elev = elevval[eidx2][-1]

		
		
        fig1 = plt.figure(figsize=figuresize, 
                         dpi=300)

        ax1 = fig1.add_subplot(111)
        for lidx in range(len(elevlu)):
            ax1.plot(elevval[lidx], elevperc[lidx],
                        linewidth=0.8, label=elevlu[lidx])
                        
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])


    	ax1.legend(loc="center left", 
                   bbox_to_anchor=[1, 0.5],
                   ncol=1, 
                   shadow=False, 
                   title="Land use",
                   fontsize = legendfontsize,
                   prop=legend_properties) 
                      
        ax1.set_xlim(left=min_elev, 
                      right=max_elev)
        
        ax1.set_ylim(bottom=0, 
                 top=100
                 )
        ax1.set_xticklabels(ax1.get_xticks(), xytickfontproperties)
        ax1.set_yticklabels(ax1.get_yticks(), xytickfontproperties)
        
        ax1.set_xlabel("Elevation (m)", fontsize=xlabelfontsize)
        ax1.set_ylabel("Accumulated percent of area (%)", fontsize=ylabelfontsize)
        ax1.grid(linestyle='-', 
                linewidth=0.1)
                            
        fig1.savefig(fig_elev)  

        
        fig2 = plt.figure(figsize=figuresize, 
                         dpi=300)
        ax2 = fig2.add_subplot(111)
        for lidx in range(len(slplu)):
            ax2.plot(slpval[lidx], slpperc[lidx],
                        linewidth=0.8, label=slplu[lidx])
        ax2.set_xlim(left=min_slp, 
                      right=max_slp, 
                      emit=True,
                      auto=False)
        
        ax2.set_ylim(bottom=0, 
                 top=100, 
                 emit=True,
                 auto=False
                 )
        ax2.grid(linestyle='-', 
                linewidth=0.1)

        ax2.set_xlabel("Slope (degree)", fontsize=xlabelfontsize)
        ax2.set_ylabel("Accumulated percent of area (%)", fontsize=ylabelfontsize)
        ax2.set_xticklabels(ax2.get_xticks(), xytickfontproperties)
        ax2.set_yticklabels(ax2.get_yticks(), xytickfontproperties)
               
    	box = ax2.get_position()
    	ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    	ax2.legend(loc="center left", 
                   bbox_to_anchor=[1, 0.5],
                   ncol=1, 
                   shadow=False, 
                   title="Land use",
                   fontsize = legendfontsize,
                   prop=legend_properties)


    	
        fig2.savefig(fig_slp)  


        fig3 = plt.figure(figsize=figuresize, 
                         dpi=300)
        ax3 = fig3.add_subplot(111)
        for lidx in range(len(distlu)):
            ax3.plot(distval[lidx], distperc[lidx],
                        linewidth=0.8, label=distlu[lidx])
            
        ax3.set_xlim(left=min_dist, 
                      right=max_dist, 
                      emit=True,
                      auto=False)
        
        ax3.set_ylim(bottom=0, 
                 top=100, 
                 emit=True,
                 auto=False
                 )

        ax3.set_xlabel("Distance (m)", fontsize=xlabelfontsize)
        ax3.set_ylabel("Accumulated percent of area (%)", fontsize=ylabelfontsize)
        ax3.set_xticklabels(ax3.get_xticks(), xytickfontproperties)
        ax3.set_yticklabels(ax3.get_yticks(), xytickfontproperties)
        
        ax3.grid(linestyle='-', 
                linewidth=0.1)
        
    	box = ax3.get_position()
    	ax3.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    	ax3.legend(loc="center left", 
                   bbox_to_anchor=[1, 0.5],
                   ncol=1, 
                   shadow=False, 
                   title="Land use",
                   fontsize = legendfontsize,
                   prop=legend_properties)
    	
        fig3.savefig(fig_dist)  

        # Free memory
        del(fn_elevdt)
        del(fn_distdt)
        del(fn_slpdt)
        
        
        del(fig_elev)
        del(fig_dist)
        del(fig_slp)
        
        del(elevlu, elevval, elevperc)
        del(slplu, slpval, slpperc)
        del(distlu, distval, distperc)
        






                                                                                
