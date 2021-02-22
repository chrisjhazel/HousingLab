g detail to be 1 by default, may use this variable in the future
height = 12 #Set standard height for 12' for now, may use this variabel in the future


def buildingExtruder(bldgFtpt, floorNum, height):
    bldgHt = height
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
        for i in range(int(floorNum - 1)):
            arrPt = (0,0,bldgHt*(i+1))
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
        for i in range(int(floorNum - 1)):
            arrPt = (0,0,bldgHt*(i+1))
            trnsVect = rs.VectorCreate(arrPt, strPt)
            for unit in floorBlock:
                arrayBlock.append(rs.CopyObject(unit, trnsVect))
    
        
    return arrayBlock, floorOutlines

#Layout spaces per typology
#Bar typology
def layoutBar(unitList, unitDimTree, commonSpace, colorList):
    #Size the per floor area
    #Draw a line for the length of the building
    
    #Used for _detail 0 - NOT USED
    """
    bldgWid = ((bldgInfoList.unitDepth*2)+bldgInfoList.corridorWidth)
    bldgLen = (bldgInfoList.bldgArea/bldgWid)
    """
    
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
        colorTree = []
        colorSubList = []
        xPt = 0
        for j, unitNum in enumerate(unitList):
            unitDims = unitDimTree.Branch(j)
            houseBlocksSub = []
            colorSub = []
            for i in range(int(m.floor((unitNum/floorNum)/2))):
                roomPt = (xPt,0,0)
                roomPt2 = (xPt, corWidth, 0)
                houseBlocksSub.append(rs.AddRectangle(roomPt, unitDims[0], -unitDims[1]))
                houseBlocksSub.append(rs.AddRectangle(roomPt2, unitDims[0], unitDims[1]))
                colorSub.append(colorList[j])
                colorSubList.append(colorList[j])
                colorSubList.append(colorList[j])
                xPt = xPt + unitDims[0]
            bldgOutln.append(houseBlocksSub)
            colorTree.append(colorSub)
        
        #Add rectangle for Common Space
        ghPath = gh.Kernel.Data.GH_Path(i+1)
        roomPt = (xPt, -minDepth, 0)
        commonSpaceRoom = (rs.AddRectangle(roomPt, ((sum(commonSpace)/floorNum)/(2*minDepth+corWidth)), (2*minDepth+corWidth)))
        bldgOutln.append([commonSpaceRoom])
        colorTree.append([commonColor])
        colorSubList.append(commonColor)
    
    return bldgOutln, colorSubList

#Cross Typology
def layoutCross(unitList, unitDimTree, commonSpace, colorList):
    bldgWid = ((maxDepth*2)+corWidth)
    bldgLen = ((sum(areaList)/floorNum)/bldgWid)
    
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
        colorTree = []
        colorSubList = []
        
        xPt1 = (bldgLen*.25) - (bldgWid*.25)
        xPt2 = (bldgLen*.25) + (bldgWid*.75)
        yPt1 = 0
        yPt2 = bldgWid
        for j, unitNum in enumerate(unitList):
            unitDims = unitDimTree.Branch(j)
            houseBlockSub = []
            colorSub = []
            #If there are enough units to spread across all four legs
            if unitNum/floorNum > 7:
                for i in range(int((round((unitNum/floorNum)/4))/2)):
                    roomXPt1 = (xPt1, maxDepth, 0)
                    roomXPt2 = (xPt1, corWidth+maxDepth, 0)
                    roomXPt3 = (xPt2, maxDepth, 0)
                    roomXPt4 = (xPt2, corWidth+maxDepth, 0)
                    houseBlockSub.append(rs.AddRectangle(roomXPt1, -unitDims[0], -unitDims[1]))
                    houseBlockSub.append(rs.AddRectangle(roomXPt2, -unitDims[0], unitDims[1]))
                    houseBlockSub.append(rs.AddRectangle(roomXPt3, unitDims[0], -unitDims[1]))
                    houseBlockSub.append(rs.AddRectangle(roomXPt4, unitDims[0], unitDims[1]))
                    xPt1 = xPt1 - unitDims[0]
                    xPt2 = xPt2 + unitDims[0]
                    for t in range(4):
                        colorSubList.append(colorList[j])
                for y in range(int((round((unitNum/floorNum)/4))/2)):
                    roomYPt1 = (((bldgLen*.25)-(bldgWid*.25)+maxDepth), yPt1, 0)
                    roomYPt2 = ((maxDepth + corWidth + (bldgLen*.25 - bldgWid*.25)), yPt1, 0)
                    roomYPt3 = (((bldgLen*.25)-(bldgWid*.25)+maxDepth), yPt2, 0)
                    roomYPt4 = ((maxDepth + corWidth + (bldgLen*.25 - bldgWid*.25)), yPt2, 0)
                    houseBlockSub.append(rs.AddRectangle(roomYPt1, -unitDims[1], -unitDims[0]))
                    houseBlockSub.append(rs.AddRectangle(roomYPt2, unitDims[1], -unitDims[0]))
                    houseBlockSub.append(rs.AddRectangle(roomYPt3, -unitDims[1], unitDims[0]))
                    houseBlockSub.append(rs.AddRectangle(roomYPt4, unitDims[1], unitDims[0]))
                    yPt1 = yPt1 - unitDims[0]
                    yPt2 = yPt2 + unitDims[0]
                    for t in range(4):
                        colorSubList.append(colorList[j])
                bldgOutln.append(houseBlockSub)
            
            #If there are enough units to spread across two legs
            #Alternate between which leg is getting the units
            elif 2 < unitNum/floorNum < 8:
                counter = 1
                for i in range(int((round((unitNum/floorNum)/2)))):
                    if counter % 2 == 0:
                        roomXPt1 = (xPt1, maxDepth, 0)
                        roomXPt2 = (xPt1, corWidth+maxDepth, 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt1, -unitDims[0], -unitDims[1]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt2, -unitDims[0], unitDims[1]))
                        xPt1 = xPt1 - unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                    elif counter % 2 != 0:
                        roomXPt3 = (xPt2, maxDepth, 0)
                        roomXPt4 = (xPt2, corWidth+maxDepth, 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt3, unitDims[0], -unitDims[1]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt4, unitDims[0], unitDims[1]))
                        xPt2 = xPt2 + unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                    counter = counter + 1
                bldgOutln.append(houseBlockSub)
            
            #If there are only 2 units, attach to single leg
            elif unitNum/floorNum <= 2:
                roomXPt1 = (xPt1, maxDepth, 0)
                roomXPt2 = (xPt1, corWidth+maxDepth, 0)
                houseBlockSub.append(rs.AddRectangle(roomXPt1, -unitDims[0], -unitDims[1]))
                houseBlockSub.append(rs.AddRectangle(roomXPt2, -unitDims[0], unitDims[1]))
                for t in range(2):
                    colorSubList.append(colorList[j])
                xPt1 = xPt1 - unitDims[0]
                bldgOutln.append(houseBlockSub)
        
        #Add Common space
        commonSpaceRoom = []
        #Connection point
        bldgCen = ((bldgLen*.25) - (bldgWid*.25), 0, 0)
        commonSpaceRoom.append(rs.AddRectangle(bldgCen, bldgWid, bldgWid))
        #CommonSpaces along legs
        roomYPt1 = ((bldgLen*.25 - bldgWid*.25), yPt1, 0)
        roomYPt2 = ((bldgLen*.25 - bldgWid*.25), yPt2, 0)
        commonSpaceRoom.append(rs.AddRectangle(roomYPt1, bldgWid, -((sum(commonSpace)/floorNum)/(bldgWid))))
        commonSpaceRoom.append(rs.AddRectangle(roomYPt2, bldgWid, ((sum(commonSpace)/floorNum)/(bldgWid))))
        for t in range(3):
            colorSubList.append(commonColor)
        
        """
        if (bldgInfoList.commonSpace/bldgWid) < (bldgWid*1.5):
            roomYPt1 = ((bldgLen*.25 - bldgWid*.25), yPt1, 0)
            roomYPt2 = ((bldgLen*.25 - bldgWid*.25), yPt2, 0)
            commonSpace.append(rs.AddRectangle(roomYPt1, bldgWid, -((sum(commonSpace)/floorNum)/(4*minDepth+corWidth))))
            commonSpace.append(rs.AddRectangle(roomYPt2, bldgWid, ((sum(commonSpace)/floorNum)/(4*minDepth+corWidth))))
        
        if (bldgInfoList.commonSpace/bldgWid) >= (bldgWid*1.5):
            roomXPt1 = (xPt1, 0, 0)
            roomXPt2 = (xPt2, 0, 0)
            roomYPt1 = ((bldgLen*.25 - bldgWid*.25), yPt1, 0)
            roomYPt2 = ((bldgLen*.25 - bldgWid*.25), yPt2, 0)
            commonSpace.append(rs.AddRectangle(roomXPt1, -((bldgInfoList.commonSpace/4)/(bldgWid)), bldgWid))
            commonSpace.append(rs.AddRectangle(roomXPt2, ((bldgInfoList.commonSpace/4)/(bldgWid)), bldgWid))
            commonSpace.append(rs.AddRectangle(roomYPt1, bldgWid, -((bldgInfoList.commonSpace/4)/bldgWid)))
            commonSpace.append(rs.AddRectangle(roomYPt2, bldgWid, ((bldgInfoList.commonSpace/4)/bldgWid)))
        """
        
        bldgOutln.append(commonSpaceRoom)
    
    return bldgOutln, colorSubList

#L-Angle Typology
def layoutLAngle(unitList, unitDimTree, commonSpace, colorList, rat):
    bldgWid = ((maxDepth*2)+corWidth)
    bldgLen = ((sum(areaList)/floorNum)/bldgWid)
    
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
        colorSubList = []
        xPt = bldgWid
        yPt = 0
        counter = 1
        for j, unitNum in enumerate(unitList):
            unitDims = unitDimTree.Branch(j)
            houseBlockSub = []
            for i in range(int(round((unitNum/floorNum)/2))):
                if counter % rat != 0:
                    roomXPt1 = (xPt, maxDepth, 0)
                    roomXPt2 = (xPt, maxDepth+corWidth, 0)
                    houseBlockSub.append(rs.AddRectangle(roomXPt1, unitDims[0], -unitDims[1]))
                    houseBlockSub.append(rs.AddRectangle(roomXPt2, unitDims[0], unitDims[1]))
                    xPt = xPt + unitDims[0]
                    for t in range(2):
                        colorSubList.append(colorList[j])
                elif counter % rat == 0:
                    roomYPt1 = (maxDepth, yPt, 0)
                    roomYPt2 = (maxDepth+corWidth, yPt, 0)
                    houseBlockSub.append(rs.AddRectangle(roomYPt1, -unitDims[1], -unitDims[0]))
                    houseBlockSub.append(rs.AddRectangle(roomYPt2, unitDims[1], -unitDims[0]))
                    yPt = yPt - unitDims[0]
                    for t in range(2):
                        colorSubList.append(colorList[j])
                counter = counter + 1
            bldgOutln.append(houseBlockSub)
        
        #Add Common space
        commonSpaceRoom = []
        #Connection point
        commonSpaceRoom.append(rs.AddRectangle(bldgOneCen, bldgWid, bldgWid))
        #CommonSpaces along legs
        roomXPt1 = (xPt, 0, 0)
        roomYPt1 = (0, yPt, 0)
        commonSpaceRoom.append(rs.AddRectangle(roomXPt1, ((sum(commonSpace)/floorNum)/(bldgWid)), bldgWid))
        commonSpaceRoom.append(rs.AddRectangle(roomYPt1, bldgWid, -((sum(commonSpace)/floorNum)/(bldgWid))))
        for t in range(3):
            colorSubList.append(commonColor)
        
        bldgOutln.append(commonSpaceRoom)
        
    return bldgOutln, colorSubList

#U-Angle Typology
def layoutUAngle(unitList, unitDimTree, commonSpace, colorList, rat):
    bldgWid = ((maxDepth*2)+corWidth)
    bldgLen = ((sum(areaList)/floorNum)/bldgWid)
    
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
        colorSubList = []
        xPt1 = bldgWid
        xPt2 = 0
        yPt1 = 0
        yPt2 = 0
        
        counter = 0
        connectorLen = 0
        moverBlocks = []
        if rat == 2: #Wide
            for j, unitNum in enumerate(unitList):
                unitDims = unitDimTree.Branch(j)
                houseBlockSub = []
                for i in range(int(round((unitNum/floorNum)/2))):
                    if counter == 0: #Connector Leg
                        roomXPt1 = (xPt1, maxDepth, 0)
                        roomXPt2 = (xPt1, maxDepth + corWidth, 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt1, unitDims[0], -unitDims[1]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt2, unitDims[0], unitDims[1]))
                        counter = counter + 1
                        connectorLen = connectorLen + unitDims[0]
                        xPt1 = xPt1 + unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                        
                    elif counter == 1: #Near leg
                        roomYPt1 = (maxDepth, yPt1, 0)
                        roomYPt2 = ((maxDepth + corWidth), yPt1, 0)
                        houseBlockSub.append(rs.AddRectangle(roomYPt1, -unitDims[1], -unitDims[0]))
                        houseBlockSub.append(rs.AddRectangle(roomYPt2, unitDims[1], -unitDims[0]))
                        counter = counter + 1
                        yPt1 = yPt1 - unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                        
                    elif counter == 2: #Connector Leg
                        roomXPt1 = (xPt1, maxDepth, 0)
                        roomXPt2 = (xPt1, (maxDepth + corWidth), 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt1, unitDims[0], -unitDims[1]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt2, unitDims[0], unitDims[1]))
                        counter = counter + 1
                        connectorLen = connectorLen + unitDims[0]
                        xPt1 = xPt1 + unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                        
                    elif counter == 3: #Far Leg to be moved
                        roomYPt1 = (maxDepth, yPt2, 0)
                        roomYPt2 = ((maxDepth + corWidth), yPt2, 0)
                        unit1 = (rs.AddRectangle(roomYPt1, -unitDims[1], -unitDims[0]))
                        unit2 = (rs.AddRectangle(roomYPt2, unitDims[1], -unitDims[0]))
                        houseBlockSub.append(unit1)
                        houseBlockSub.append(unit2)
                        moverBlocks.append(unit1)
                        moverBlocks.append(unit2)
                        counter = 0
                        yPt2 = yPt2 - unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                        
                bldgOutln.append(houseBlockSub)
        
        if rat == 3: #Square
            for j, unitNum in enumerate(unitList):
                unitDims = unitDimTree.Branch(j)
                houseBlockSub = []
                for i in range(int(round((unitNum/floorNum)/2))):
                    if counter == 0: #Connector Leg
                        roomXPt1 = (xPt1, maxDepth, 0)
                        roomXPt2 = (xPt1, (maxDepth + corWidth), 0)
                        houseBlockSub.append(rs.AddRectangle(roomXPt1, unitDims[0], -unitDims[1]))
                        houseBlockSub.append(rs.AddRectangle(roomXPt2, unitDims[0], unitDims[1]))
                        counter = counter + 1
                        connectorLen = connectorLen + unitDims[0]
                        xPt1 = xPt1 + unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                        
                    elif counter == 1: #Near leg
                        roomYPt1 = (maxDepth, yPt1, 0)
                        roomYPt2 = ((maxDepth + corWidth), yPt1, 0)
                        houseBlockSub.append(rs.AddRectangle(roomYPt1, -unitDims[1], -unitDims[0]))
                        houseBlockSub.append(rs.AddRectangle(roomYPt2, unitDims[1], -unitDims[0]))
                        counter = counter + 1
                        yPt1 = yPt1 - unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                        
                    elif counter == 2: #Far Leg to be moved
                        roomYPt1 = (maxDepth, yPt2, 0)
                        roomYPt2 = ((maxDepth + corWidth), yPt2, 0)
                        unit1 = (rs.AddRectangle(roomYPt1, -unitDims[1], -unitDims[0]))
                        unit2 = (rs.AddRectangle(roomYPt2, unitDims[1], -unitDims[0]))
                        houseBlockSub.append(unit1)
                        houseBlockSub.append(unit2)
                        moverBlocks.append(unit1)
                        moverBlocks.append(unit2)
                        counter = 0
                        yPt2 = yPt2 - unitDims[0]
                        for t in range(2):
                            colorSubList.append(colorList[j])
                        
                bldgOutln.append(houseBlockSub)
        
        #Move the far leg blocks and rerecord the GUIDs
        for i in range(len(bldgOutln)):
            unitTypeUpdate = []
            for unit in bldgOutln[i]:
                for block in moverBlocks:
                    if unit == block:
                        unit = rs.MoveObject(unit, (xPt1, 0, 0))
                unitTypeUpdate.append(unit)
    
    #Add common space
    commonSpaceRoom = []
    commonSpaceRoom.append(rs.AddRectangle(bldgOneCen, bldgWid, bldgWid))
    commonSpaceRoom.append(rs.CopyObject(commonSpaceRoom[0], (xPt1, 0, 0)))
    
    #Common Spaces along Legs
    plane1 = (0, yPt1, 0)
    plane2 = (xPt1, yPt2, 0)
    commonSpaceRoom.append(rs.AddRectangle(plane1, bldgWid, -((sum(commonSpace)/floorNum)/(bldgWid))))
    commonSpaceRoom.append(rs.AddRectangle(plane2, bldgWid, -((sum(commonSpace)/floorNum)/(bldgWid))))
    for t in range(4):
        colorSubList.append(commonColor)
    
    bldgOutln.append(commonSpaceRoom)
    
    return bldgOutln, colorSubList

if typology == "Bar":
    bldgFtpt, colorSubList = layoutBar(unitList, unitDimTree, commonSpace, colorList)

elif typology == "Cross":
    bldgFtpt, colorSubList = layoutCross(unitList, unitDimTree, commonSpace, colorList)

elif typology == "L-Angle(1/2)":
    bldgFtpt, colorSubList = layoutLAngle(unitList, unitDimTree, commonSpace, colorList, 2)

elif typology == "L-Angle(1/3)":
    bldgFtpt, colorSubList = layoutLAngle(unitList, unitDimTree, commonSpace, colorList, 3)

elif typology == "L-Angle(1/4)":
    bldgFtpt, colorSubList = layoutLAngle(unitList, unitDimTree, commonSpace, colorList, 4)

elif typology == "U-Angle(Wide)":
    bldgFtpt, colorSubList = layoutUAngle(unitList, unitDimTree, commonSpace, colorList, 2)

elif typology == "U-Angle(Square)":
    bldgFtpt, colorSubList = layoutUAngle(unitList, unitDimTree, commonSpace, colorList, 3)

unitGeo, floorOutlines = buildingExtruder(bldgFtpt, floorNum, height)

unitColorList = colorSubList*int(floorNum)