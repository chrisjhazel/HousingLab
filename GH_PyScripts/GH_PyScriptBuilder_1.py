#This script will layout the housing blocks according to the selected building typology
#Author: Chris Hazel
#Date Started: 2019.10.23

"""
Arguments
_buildingTypology: Value List of possible building layout types
_oGSF: Outside of unit gross square footage; this value will determine additional out of unit space in the building
_amenities: A list of amenities to be designed into the building
_constructionType: Value list of construction types
housingTypeList: Object list of the housing types
bldgInfoList: Object list of the building info

Returns
bldgFtpt: Curve of the building footprint produced
arrayBlock: Each building floor arrayed along z-axis


"""

import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import ghpythonlib.components as gh
import math as m

sc.doc = ghdoc


#Determine total square footage
def buildingSizer(_oGSF, housingTypeList, bldgInfoList):
    bldgArea = 0
    
    #Find total area for rooms
    for room in housingTypeList:
        bldgArea = bldgArea + (room.roomNum * room.nsf)
    
    bldgInfoList.commonSpace = (bldgArea*_oGSF)
    if _detail == 0:
        #Add 25% for conceptual layout
        bldgInfoList.bldgArea = (bldgArea*1.25) + bldgInfoList.commonSpace
    if _detail == 1:
        bldgInfoList.bldgArea = bldgArea + bldgInfoList.commonSpace
    
    return housingTypeList, bldgInfoList

def buildingExtruder(bldgFtpt, bldgInfoList):
    bldgHt = (bldgInfoList.height)
    strPt = rs.AddPoint(0,0,0)
    extPt = (0,0,bldgHt)
    extPath = rs.AddCurve([strPt, extPt], degree = 1)
    
    #Check detail level
    if _detail == 0:
        
        #Extrude the curve(s) + capholes
        if type(bldgFtpt) == list:
            floorBlock = []
            srfObj = []
            singCrv = rs.CurveBooleanUnion(bldgFtpt)
            floorBlock = rs.ExtrudeCurve(singCrv, extPath)
            floorOutlines = singCrv
            rs.CapPlanarHoles(floorBlock)
            
        else:
            floorBlock = rs.ExtrudeCurve(bldgFtpt, extPath)
            rs.CapPlanarHoles(floorBlock)
        
        arrayBlock = [floorBlock]
        for i in range(int(bldgInfoList.floorNum - 1)):
            arrPt = (0,0,bldgInfoList.explode*(i+1))
            trnsVect = rs.VectorCreate(arrPt, strPt)
            arrayBlock.append(rs.CopyObject(floorBlock, trnsVect))
        
    if _detail == 1: #schematic design
        floorBlock = []
        floorOutlines = []
        for houseBlock in bldgFtpt:
            for crv in houseBlock:
                blockInt = (rs.ExtrudeCurve(crv, extPath))
                rs.CapPlanarHoles(blockInt)
                floorBlock.append(blockInt)
                floorOutlines.append(crv)
        
        #Copy all floorBlock data to arrayBlock
        arrayBlock = []
        for unit in floorBlock:
            arrayBlock.append(unit)
        for i in range(int(bldgInfoList.floorNum - 1)):
            arrPt = (0,0,bldgInfoList.explode*(i+1))
            trnsVect = rs.VectorCreate(arrPt, strPt)
            for unit in floorBlock:
                arrayBlock.append(rs.CopyObject(unit, trnsVect))
    
        
    return arrayBlock, floorOutlines

def clusterFork(housingTypeList, bldgInfoList):
    #This function will define clusters for the housing types
    Traditional = 4
    SemiSuite = 3
    FullSuite = 1
    Apartment = 1
    
    

#Layout spaces per typology
#Bar typology
def layoutBar(housingTypeList, bldgInfoList):
    #Size the per floor area
    #Draw a line for the length of the building
    bldgWid = ((bldgInfoList.unitDepth*2)+bldgInfoList.corridorWidth)
    bldgLen = (bldgInfoList.bldgArea/bldgWid)
    
    #Add building start point
    ptStr = (0,0,0)
    
    
    if _detail == 0:
        #Conceptual Layout
        #Draw building footprint
        bldgOutln = rs.AddRectangle(ptStr, bldgLen, bldgWid)
    
    elif _detail == 1:
        #Schematic Layout
        #Get housing type unit lengths
        bldgOutln = []
        xPt = 0
        for room in housingTypeList:
            houseBlocksSub = []
            for i in range(int(m.floor(room.roomNum/2))):
                roomPt = (xPt,0,0)
                roomPt2 = (xPt, (bldgInfoList.unitDepth+bldgInfoList.corridorWidth), 0)
                houseBlocksSub.append(rs.AddRectangle(roomPt, room.size[1], room.size[0]))
                houseBlocksSub.append(rs.AddRectangle(roomPt2, room.size[1], room.size[0]))
                xPt = xPt + room.size[1]
            bldgOutln.append(houseBlocksSub)
            room.unitGUIDs = houseBlocksSub
        
        #Add rectangle for Common Space
        roomPt = (xPt, 0, 0)
        commonSpace = (rs.AddRectangle(roomPt, (bldgInfoList.commonSpace/bldgWid), bldgWid))
        bldgOutln.append([commonSpace])
    
    return bldgOutln

#Cross Typology
def layoutCross(housingTypeList, bldgInfoList):
    bldgWid = ((bldgInfoList.unitDepth*2)+bldgInfoList.corridorWidth)
    bldgLen = (bldgInfoList.bldgArea/bldgWid)
    
    #Find building start points
    bldgOneCen = (0,0,0)
    bldgTwoCen = (((bldgLen*.25)-(bldgWid*.25)), ((bldgLen*.25)+(bldgWid*.75)),0)
    
    if _detail == 0:
        #Conceptual Design Layout
        #Draw building footprint
        bldgOutln1 = rs.AddRectangle(bldgOneCen, (bldgLen*.5)+(bldgWid*.5), bldgWid)
        bldgOutln2 = rs.AddRectangle(bldgTwoCen, bldgWid, -((bldgLen*.5)+(bldgWid*.5)))
        
        bldgOutln = [bldgOutln1, bldgOutln2]
    
    if _detail == 1:
        #Schematic Design Layout
        bldgOutln = []
        xPt1 = (bldgLen*.25) - (bldgWid*.25)
        xPt2 = (bldgLen*.25) + (bldgWid*.75)
        yPt1 = 0
        yPt2 = bldgWid
        for room in housingTypeList:
            houseBlockSub = []
            #If there are enough units to spread across all four legs
            if room.roomNum > 7:
                for i in range(int((round(room.roomNum/4))/2)):
                    roomXPt1 = (xPt1, 0, 0)
                    roomXPt2 = (xPt1, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                    roomXPt3 = (xPt2, 0, 0)
                    roomXPt4 = (xPt2, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                    houseBlockSub.append(rs.AddRectangle(roomXPt1, -room.size[1], room.size[0]))
                    houseBlockSub.append(rs.AddRectangle(roomXPt2, -room.size[1], room.size[0]))
                    houseBlockSub.append(rs.AddRectangle(roomXPt3, room.size[1], room.size[0]))
                    houseBlockSub.append(rs.AddRectangle(roomXPt4, room.size[1], room.size[0]))
                    xPt1 = xPt1 - room.size[1]
                    xPt2 = xPt2 + room.size[1]
                for y in range(int((round(room.roomNum/4))/2)):
                    roomYPt1 = ((bldgLen*.25 - bldgWid*.25), yPt1, 0)
                    roomYPt2 = ((bldgInfoList.unitDepth + bldgInfoList.corridorWidth + (bldgLen*.25 - bldgWid*.25)), yPt1, 0)
                    roomYPt3 = ((bldgLen*.25 - bldgWid*.25), yPt2, 0)
                    roomYPt4 = ((bldgInfoList.unitDepth + bldgInfoList.corridorWidth + (bldgLen*.25 - bldgWid*.25)), yPt2, 0)
                    houseBlockSub.append(rs.AddRectangle(roomYPt1, room.size[0], -room.size[1]))
                    houseBlockSub.append(rs.AddRectangle(roomYPt2, room.size[0], -room.size[1]))
                    houseBlockSub.append(rs.AddRectangle(roomYPt3, room.size[0], room.size[1]))
                    houseBlockSub.append(rs.AddRectangle(roomYPt4, room.size[0], room.size[1]))
                    yPt1 = yPt1 - room.size[1]
                    yPt2 = yPt2 + room.size[1]
                bldgOutln.append(houseBlockSub)
                room.unitGUIDs = houseBlockSub
            
            #If there are enough units to spread across two legs
            #Alternate between which leg is getting the units
            elif 2 < room.roomNum < 8:
                counter = 1
                for i in range(int((round(room.roomNum/2)))):
                    if counter % 2 == 0:
                        roomXPt1 = (xPt1, 0, 0)
                        roomXPt2 = (xPt1, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt1, -room.size[1], room.size[0]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt2, -room.size[1], room.size[0]))
                        xPt1 = xPt1 - room.size[1]
                    elif counter % 2 != 0:
                        roomXPt3 = (xPt2, 0, 0)
                        roomXPt4 = (xPt2, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt3, room.size[1], room.size[0]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt4, room.size[1], room.size[0]))
                        xPt2 = xPt2 + room.size[1]
                    counter = counter + 1
                bldgOutln.append(houseBlockSub)
                room.unitGUIDs = houseBlockSub
            
            #If there are only 2 units, attach to single leg
            elif room.roomNum <= 2:
                roomXPt1 = (xPt1, 0, 0)
                roomXPt2 = (xPt1, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                houseBlockSub.append(rs.AddRectangle(roomXPt1, -room.size[1], room.size[0]))
                houseBlockSub.append(rs.AddRectangle(roomXPt2, -room.size[1], room.size[0]))
                xPt1 = xPt1 - room.size[1]
                bldgOutln.append(houseBlockSub)
                room.unitGUIDs = houseBlockSub
        
        #Add Common space
        commonSpace = []
        #Connection point
        bldgCen = ((bldgLen*.25) - (bldgWid*.25), 0, 0)
        commonSpace.append(rs.AddRectangle(bldgCen, bldgWid, bldgWid))
        #CommonSpaces along legs
        
        if (bldgInfoList.commonSpace/bldgWid) < (bldgWid*1.5):
            roomYPt1 = ((bldgLen*.25 - bldgWid*.25), yPt1, 0)
            roomYPt2 = ((bldgLen*.25 - bldgWid*.25), yPt2, 0)
            commonSpace.append(rs.AddRectangle(roomYPt1, bldgWid, -((bldgInfoList.commonSpace/2)/bldgWid)))
            commonSpace.append(rs.AddRectangle(roomYPt2, bldgWid, ((bldgInfoList.commonSpace/2)/bldgWid)))
        
        if (bldgInfoList.commonSpace/bldgWid) >= (bldgWid*1.5):
            roomXPt1 = (xPt1, 0, 0)
            roomXPt2 = (xPt2, 0, 0)
            roomYPt1 = ((bldgLen*.25 - bldgWid*.25), yPt1, 0)
            roomYPt2 = ((bldgLen*.25 - bldgWid*.25), yPt2, 0)
            commonSpace.append(rs.AddRectangle(roomXPt1, -((bldgInfoList.commonSpace/4)/(bldgWid)), bldgWid))
            commonSpace.append(rs.AddRectangle(roomXPt2, ((bldgInfoList.commonSpace/4)/(bldgWid)), bldgWid))
            commonSpace.append(rs.AddRectangle(roomYPt1, bldgWid, -((bldgInfoList.commonSpace/4)/bldgWid)))
            commonSpace.append(rs.AddRectangle(roomYPt2, bldgWid, ((bldgInfoList.commonSpace/4)/bldgWid)))
        
        
        bldgOutln.append(commonSpace)
        bldgInfoList.commonSpaceGUIDs = commonSpace
    
    return bldgOutln

#L-Angle Typology
def layoutLAngle(housingTypeList, bldgInfoList, rat):
    bldgWid = ((bldgInfoList.unitDepth*2)+bldgInfoList.corridorWidth)
    bldgLen = (bldgInfoList.bldgArea/bldgWid)
    
    #Find building start points
    bldgOneCen = (0,0,0)
    bldgTwoCen = (0,bldgWid*.5,0)
    
    if rat == 2:
        m1 = .5
        m2 = .5
    elif rat == 3:
        m1 = .67
        m2 = .33
    elif rat == 4:
        m1 = .75
        m2 = .25
    
    if _detail == 0:
        #Conceptual Design Layout
        #Draw building footprint
        bldgOutln1 = rs.AddRectangle(bldgOneCen, ((bldgLen*m1)+(bldgWid*.5)), bldgWid)
        bldgOutln2 = rs.AddRectangle(bldgTwoCen, bldgWid, -(bldgLen*m2))
        
        bldgOutln = [bldgOutln1, bldgOutln2]
    
    if _detail == 1:
        #Schematic Design Layout
        bldgOutln = []
        xPt = bldgWid
        yPt = 0
        counter = 1
        for room in housingTypeList:
            houseBlockSub = []
            for i in range(int(round(room.roomNum)/2)):
                if counter % rat != 0:
                    roomXPt1 = (xPt, 0, 0)
                    roomXPt2 = (xPt, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                    houseBlockSub.append(rs.AddRectangle(roomXPt1, room.size[1], room.size[0]))
                    houseBlockSub.append(rs.AddRectangle(roomXPt2, room.size[1], room.size[0]))
                    xPt = xPt + room.size[1]
                elif counter % rat == 0:
                    roomYPt1 = (0, yPt, 0)
                    roomYPt2 = ((bldgInfoList.unitDepth + bldgInfoList.corridorWidth), yPt, 0)
                    houseBlockSub.append(rs.AddRectangle(roomYPt1, room.size[0], -room.size[1]))
                    houseBlockSub.append(rs.AddRectangle(roomYPt2, room.size[0], -room.size[1]))
                    yPt = yPt - room.size[1]
                counter = counter + 1
            bldgOutln.append(houseBlockSub)
            room.unitGUIDs = houseBlockSub
        
        #Add Common space
        commonSpace = []
        #Connection point
        commonSpace.append(rs.AddRectangle(bldgOneCen, bldgWid, bldgWid))
        #CommonSpaces along legs
        roomXPt1 = (xPt, 0, 0)
        roomYPt1 = (0, yPt, 0)
        commonSpace.append(rs.AddRectangle(roomXPt1, ((bldgInfoList.commonSpace/2)/bldgWid), bldgWid))
        commonSpace.append(rs.AddRectangle(roomYPt1, bldgWid, -((bldgInfoList.commonSpace/2)/bldgWid)))
        
        bldgOutln.append(commonSpace)
        bldgInfoList.commonSpaceGUIDs = commonSpace
        
    return bldgOutln

#U-Angle Typology
def layoutUAngle(houndTypeList, bldgInfoList, rat):
    bldgWid = ((bldgInfoList.unitDepth*2)+bldgInfoList.corridorWidth)
    bldgLen = (bldgInfoList.bldgArea/bldgWid)
    
    if rat == 2:
        m1 = .66
        m2 = .17
    elif rat == 3:
        m1 = .5
        m2 = .25
    elif rat == 4:
        m1 = .34
        m2 = .33
        
        
    #Find building start points
    bldgOneCen = (0,0,0)
    bldgTwoCen = (0,0,0)
    bldgThrCen = ((bldgLen*m1-(bldgWid)),0, 0)
    
    if _detail == 0:
        #Conceptual Design Layout
        #Draw building footprint
        bldgOutln1 = rs.AddRectangle(bldgOneCen, ((bldgLen*m1)), bldgWid)
        bldgOutln2 = rs.AddRectangle(bldgTwoCen, bldgWid, -(bldgLen*m2))
        bldgOutln3 = rs.AddRectangle(bldgThrCen, bldgWid, -(bldgLen*m2))
        
        bldgFtpt = [bldgOutln1, bldgOutln2, bldgOutln3]
        
    if _detail == 1:
        #Schematic Design layout
        bldgOutln = []
        xPt1 = bldgWid
        xPt2 = 0
        yPt1 = 0
        yPt2 = 0
        
        counter = 0
        connectorLen = 0
        moverBlocks = []
        if rat == 2: #Wide
            for room in housingTypeList:
                houseBlockSub = []
                for i in range(int(round(room.roomNum)/2)):
                    if counter == 0: #Connector Leg
                        roomXPt1 = (xPt1, 0, 0)
                        roomXPt2 = (xPt1, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt1, room.size[1], room.size[0]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt2, room.size[1], room.size[0]))
                        counter = counter + 1
                        connectorLen = connectorLen + room.size[1]
                        xPt1 = xPt1 + room.size[1]
                        
                    elif counter == 1: #Near leg
                        roomYPt1 = (0, yPt1, 0)
                        roomYPt2 = ((bldgInfoList.unitDepth + bldgInfoList.corridorWidth), yPt1, 0)
                        houseBlockSub.append(rs.AddRectangle(roomYPt1, room.size[0], -room.size[1]))
                        houseBlockSub.append(rs.AddRectangle(roomYPt2, room.size[0], -room.size[1]))
                        counter = counter + 1
                        yPt1 = yPt1 - room.size[1]
                        
                    elif counter == 2: #Connector Leg
                        roomXPt1 = (xPt1, 0, 0)
                        roomXPt2 = (xPt1, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt1, room.size[1], room.size[0]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt2, room.size[1], room.size[0]))
                        counter = counter + 1
                        connectorLen = connectorLen + room.size[1]
                        xPt1 = xPt1 + room.size[1]
                        
                    elif counter == 3: #Far Leg to be moved
                        roomYPt1 = (0, yPt2, 0)
                        roomYPt2 = ((bldgInfoList.unitDepth + bldgInfoList.corridorWidth), yPt2, 0)
                        unit1 = (rs.AddRectangle(roomYPt1, room.size[0], -room.size[1]))
                        unit2 = (rs.AddRectangle(roomYPt2, room.size[0], -room.size[1]))
                        houseBlockSub.append(unit1)
                        houseBlockSub.append(unit2)
                        moverBlocks.append(unit1)
                        moverBlocks.append(unit2)
                        counter = 0
                        yPt2 = yPt2 - room.size[1]
                        
                bldgOutln.append(houseBlockSub)
                room.unitGUIDs = houseBlockSub
        
        if rat == 3: #Square
            for room in housingTypeList:
                houseBlockSub = []
                for i in range(int(round(room.roomNum)/2)):
                    if counter == 0: #Connector Leg
                        roomXPt1 = (xPt1, 0, 0)
                        roomXPt2 = (xPt1, (bldgInfoList.unitDepth + bldgInfoList.corridorWidth), 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt1, room.size[1], room.size[0]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt2, room.size[1], room.size[0]))
                        counter = counter + 1
                        connectorLen = connectorLen + room.size[1]
                        xPt1 = xPt1 + room.size[1]
                        
                    elif counter == 1: #Near leg
                        roomYPt1 = (0, yPt1, 0)
                        roomYPt2 = ((bldgInfoList.unitDepth + bldgInfoList.corridorWidth), yPt1, 0)
                        houseBlockSub.append(rs.AddRectangle(roomYPt1, room.size[0], -room.size[1]))
                        houseBlockSub.append(rs.AddRectangle(roomYPt2, room.size[0], -room.size[1]))
                        counter = counter + 1
                        yPt1 = yPt1 - room.size[1]
                        
                    elif counter == 2: #Far Leg to be moved
                        roomYPt1 = (0, yPt2, 0)
                        roomYPt2 = ((bldgInfoList.unitDepth + bldgInfoList.corridorWidth), yPt2, 0)
                        unit1 = (rs.AddRectangle(roomYPt1, room.size[0], -room.size[1]))
                        unit2 = (rs.AddRectangle(roomYPt2, room.size[0], -room.size[1]))
                        houseBlockSub.append(unit1)
                        houseBlockSub.append(unit2)
                        moverBlocks.append(unit1)
                        moverBlocks.append(unit2)
                        counter = 0
                        yPt2 = yPt2 - room.size[1]
                        
                bldgOutln.append(houseBlockSub)
                room.unitGUIDs = houseBlockSub
        
        #Move the far leg blocks and rerecord the GUIDs
        for i in range(len(bldgOutln)):
            unitTypeUpdate = []
            for unit in bldgOutln[i]:
                for block in moverBlocks:
                    if unit == block:
                        unit = rs.MoveObject(unit, (xPt1, 0, 0))
                unitTypeUpdate.append(unit)
            housingTypeList[i].unitGUIDs = unitTypeUpdate
    
    #Add common space
    commonSpace = []
    commonSpace.append(rs.AddRectangle(bldgOneCen, bldgWid, bldgWid))
    commonSpace.append(rs.CopyObject(commonSpace[0], (xPt1, 0, 0)))
    
    #Common Spaces along Legs
    plane1 = (0, yPt1, 0)
    plane2 = (xPt1, yPt2, 0)
    commonSpace.append(rs.AddRectangle(plane1, bldgWid, -((bldgInfoList.commonSpace/bldgWid)/2)))
    commonSpace.append(rs.AddRectangle(plane2, bldgWid, -((bldgInfoList.commonSpace/bldgWid)/2)))
    
    bldgOutln.append(commonSpace)
    
    return bldgOutln

buildingSizer(_oGSF, housingTypeList, bldgInfoList)

if _buildingTypology == 0:
    bldgFtpt = layoutBar(housingTypeList, bldgInfoList)
    arrayBlock, floorBlock = buildingExtruder(bldgFtpt, bldgInfoList)

elif _buildingTypology == 1:
    bldgFtpt = layoutCross(housingTypeList, bldgInfoList)
    arrayBlock, floorBlock = buildingExtruder(bldgFtpt, bldgInfoList)

elif _buildingTypology == 2:
    bldgFtpt = layoutLAngle(housingTypeList, bldgInfoList, 2)
    arrayBlock, floorBlock = buildingExtruder(bldgFtpt, bldgInfoList)

elif _buildingTypology == 3:
    bldgFtpt = layoutLAngle(housingTypeList, bldgInfoList, 3)
    arrayBlock, floorBlock = buildingExtruder(bldgFtpt, bldgInfoList)

elif _buildingTypology == 4:
    bldgFtpt = layoutLAngle(housingTypeList, bldgInfoList, 4)
    arrayBlock, floorBlock = buildingExtruder(bldgFtpt, bldgInfoList)

elif _buildingTypology == 5:
    bldgFtpt = layoutUAngle(housingTypeList, bldgInfoList, 2)
    arrayBlock, floorBlock = buildingExtruder(bldgFtpt, bldgInfoList)

elif _buildingTypology == 6:
    bldgFtpt = layoutUAngle(housingTypeList, bldgInfoList, 3)
    arrayBlock, floorBlock = buildingExtruder(bldgFtpt, bldgInfoList)

elif _buildingTypology == 7:
    bldgFtpt = layoutUAngle(housingTypeList, bldgInfoList, 4)
    arrayBlock, floorBlock = buildingExtruder(bldgFtpt, bldgInfoList)