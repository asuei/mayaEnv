# encoding: utf-8
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import re
import json
from PySide2 import QtGui

dir = ''
if(dir == ''):
 dir = mel.eval('whatIs asueiHotbox')
 dir = dir.replace('Mel procedure found in: ','')
 dir = dir.replace('asueiHotbox.mel','')

def mouseCursor():
 cursorPos = QtGui.QCursor().pos()
 return [cursorPos.x(),cursorPos.y()]

def fileExIm(m):
 filePath = dir + 'asueiHotboxExportTemp.mb'
 if(m==0):
  cmds.file(filePath,f=1,typ='mayaBinary',pr=1,exportSelected=1)
  print('Export to '+filePath) ;
 if(m==1):
  cmds.file(filePath,i=True,type='mayaBinary',ignoreVersion=1,ra=1,mergeNamespacesOnClash=1,namespace=':',pr=1)

def selectionExIm(m):
 filePath = dir+'asueiHotboxExportSelection.json'
 if(m==0):
  sel = cmds.ls(selection=1)
  with open(filePath,'w') as f: json.dump(sel,f,ensure_ascii=False,indent=1)
  print(filePath)
 if(m==1):
  with open(filePath) as f: sel = json.load(f)
  cmds.select(sel,r=1)

def skinWeightExIm(m):
 filePath = dir + 'asueiHotboxExportSkinWeight.json'
 skwt = []
 if(m==1 or m==2):
  with open(filePath) as f: skwt = json.load(f)
 sl = cmds.ls(selection=1)
 if(m==2): sl = cmds.ls(selection=1,flatten=1)
 
 for i in range(len(sl)): # loop of selected objects
  obj = sl[i]
  skn = mel.eval('findRelatedSkinCluster("'+obj+'")')
  vInfo = []
  if(m==1):
   vInfo = skwt[i]
   jInf = [ x[0] for x in vInfo[0] ]
   noInf = []
   for y in jInf :
    if(cmds.objExists(y)==0): noIng.append(y)
   sas = " ".join(noInf)
   if len(noInf) > 0: cmds.error("There are no : " + sas)
   if(skn=='' and m != 2):
    skn = cmds.skinCluster(jInf,obj,toSelectedBones=1)[0]
   else:
    inf = cmds.skinCluster(skn,q=1,influence=1)
    for j in range(len(jInf)) :
     ci = inf.index(jInf[j]) if jInf[j] in inf else -1
     if(ci==-1): cmds.skinCluster(skn,e=1,addInfluence=jInf[j],weight=0)
    
  vn = cmds.polyEvaluate(obj,vertex=1)
  for j in range(vn):
   if(m==0):
    tList = cmds.skinPercent(skn,obj+'.vtx['+str(j)+']',transform=None,q=1)
    vList = cmds.skinPercent(skn,obj+'.vtx['+str(j)+']',q=1,value=1)
    vInfo.append([ (x,y) for x,y in zip(tList,vList) ])
   elif(m==1):
    vName = sl[i]+'.vtx['+str(j)+']' 
    if(cmds.objExists(vName)) : cmds.skinPercent(skn,vName,transformValue=vInfo[j])
    
  if(m==2):
   vInfo = skwt[0]
   obj = sl[i].split('.')[0]
   skn = mel.eval('findRelatedSkinCluster("'+obj+'")')
   vN = sl[i].split('[')[-1]
   vN = vN.replace(']','')
   iVn = int(vN)
   cmds.skinPercent(skn,sl[i],transformValue=vInfo[iVn])
  
  if(m==0): skwt.append(vInfo)
 if(m==0):
  with open(filePath, 'w') as f: json.dump(skwt,f,ensure_ascii=False,indent=1)
 print(filePath)
 pass

def softCluster():
 selection = cmds.ls(sl=True)
 richSel = om.MRichSelection()
 om.MGlobal.getRichSelection(richSel)
 richSelList = om.MSelectionList()
 richSel.getSelection(richSelList)
 
 cluster = cmds.cluster( rel=True )
 cmds.setAttr(cluster[1]+'.rotate',lock=1)
 cmds.setAttr(cluster[1]+'.scale',lock=1)
 cmds.setAttr(cluster[1]+'.v',keyable=0,cb=1)
 clusterSet = cmds.listConnections( cluster, type='objectSet' )
 
 for i,x in enumerate(selection) :
  path = om.MDagPath()
  component = om.MObject()
  richSelList.getDagPath(i, path, component)
  componentFn = om.MFnSingleIndexedComponent(component)
  
  for ii in range(0,componentFn.elementCount()):
   weight = componentFn.weight(ii)
   v = componentFn.element(ii)
   w = weight.influence()
   sel = x.split('.')
   pn = sel[1].split('[')[0] # point name
   vtx = (sel[0]+'.'+pn+'['+str(v)+']')
   cmds.sets(vtx, add=clusterSet[0])
   cmds.percent(cluster[0], vtx,  v=w )
  cmds.select(cluster[1])

def vertexInferencePaintWeight():
 sl = cmds.ls(sl=1,fl=1)
 sk = mel.eval('findRelatedSkinCluster("'+sl[0].split('.')[0]+'")')
 inf = cmds.skinCluster(sk,q=1,inf=1)
 infList = []
 for x in sl :
  wList = cmds.skinPercent(sk,x,q=1,v=1)
  for i,w in enumerate(wList) :
   if w > 0:
    if inf[i] not in infList :
     infList.append(inf[i])

 for x in inf :
  if x not in infList : cmds.setAttr(x+'.liw',1)
  else : cmds.setAttr(x+'.liw',0)

 cmds.select(sl[0].split('.')[0],r=1)
 mel.eval('ToolSettingsWindow')
 mel.eval('ArtPaintSkinWeightsTool') 
 tv = cmds.treeView('theSkinClusterInflList',q=1,ch='')
 for x in tv :
  if x in infList :
   cmds.treeView('theSkinClusterInflList',e=1,selectItem=[x,1])
  else:
   cmds.treeView('theSkinClusterInflList',e=1,selectItem=[x,0])

class as_namingUI :
 def __init__(self):
  if(cmds.window('win_anm',exists=1)):
   cmds.deleteUI('win_anm')
  cmds.window('win_anm',title='as Naming')

  cmds.formLayout('form_anmMain')
  cmds.button('btn_anmSN',label='Sequence Naming',width=150,height=30,command=self.sequenceNaming)
  cmds.button('btn_anmCSN',label='Correct Shape Name',width=150,height=30,command=self.correntShapeName)
  cmds.separator('sprt1',style='in')
  cmds.button('btn_anmSSS',label='input same string',width=150,height=20,command=self.sameStringBtn)
  cmds.textField('txt_anmR1',text='',width=150,height=23)
  cmds.textField('txt_anmR2',text='',width=150,height=23,enterCommand=self.searchReplace)
  cmds.button('btn_anmRB',label='Search and Replace',width=150,height=30,command=self.searchReplace)
  cmds.separator('sprt2',style='in')
  cmds.textField('txt_anmPS',text='',width=150,height=23)
  cmds.button('btn_anmAP',label='Prefix',width=75,height=30,command=self.addPrefix)
  cmds.button('btn_anmAS',label='Suffix',width=75,height=30,command=self.addSuffix)


  cmds.formLayout('form_anmMain',e=1,af=[('btn_anmSN','top',5),('btn_anmSN','left',5)])
  cmds.formLayout('form_anmMain',e=1,ac=('btn_anmCSN','top',5,'btn_anmSN'),af=('btn_anmCSN','left',5))
  cmds.formLayout('form_anmMain',e=1,af=[('sprt1','left',5),('sprt1','right',5)],ac=('sprt1','top',5,'btn_anmCSN'))
  cmds.formLayout('form_anmMain',e=1,af=('btn_anmSSS','left',5),ac=('btn_anmSSS','top',3,'sprt1'))
  cmds.formLayout('form_anmMain',e=1,af=('txt_anmR1','left',5),ac=('txt_anmR1','top',5,'btn_anmSSS'))
  cmds.formLayout('form_anmMain',e=1,af=('txt_anmR2','left',5),ac=('txt_anmR2','top',3,'txt_anmR1'))
  cmds.formLayout('form_anmMain',e=1,af=('btn_anmRB','left',5),ac=('btn_anmRB','top',3,'txt_anmR2'))
  cmds.formLayout('form_anmMain',e=1,af=[('sprt2','left',5),('sprt2','right',5)],ac=('sprt2','top',5,'btn_anmRB'))
  cmds.formLayout('form_anmMain',e=1,af=('txt_anmPS','left',5),ac=('txt_anmPS','top',5,'sprt2'))
  cmds.formLayout('form_anmMain',e=1,af=('btn_anmAP','left',5),ac=('btn_anmAP','top',3,'txt_anmPS'))
  cmds.formLayout('form_anmMain',e=1,ac=[('btn_anmAS','left',0,'btn_anmAP'),('btn_anmAS','top',3,'txt_anmPS')])
  
  cmds.window('win_anm',e=1,widthHeight=[200,30],resizeToFitChildren=1)
  cmds.showWindow('win_anm')
  self.sameStringBtn()


 def sequenceNaming(self,*a):
  sa = len(cmds.ls(selection=1))
  setList = []
  for x in cmds.ls(selection=1):
   ts = cmds.sets(x)
   setList.append(ts)
  
  lss = cmds.ls(selection=1)[0]
  if '|' in lss : lss = lss.split('|')[-1]
  num = re.findall(r'\d+',lss)
  numI = [int(i) for i in num]
  strList = re.split(r'\d+',lss)


  i = 0
  for j in range(sa):
   lx = cmds.sets(setList[j],q=1)[0]
   numP = numI[0] + i
   nn = lss.replace(num[0],str(numP))
   cmds.rename(lx,nn)
   i = i + 1
  cmds.delete(setList)


 def sameStringBtn(self,*a):
  sl = cmds.ls(selection=1)
  for i,x in enumerate(sl) :
   sx = x.split('|')[-1]
   sl[i] = sx
  sw = self.findSameString(sl)
  cmds.textField('txt_anmR1',e=1,text=sw)
   
 def searchReplace(self,*a):
  sa = len(cmds.ls(selection=1))
  tf1 = cmds.textField('txt_anmR1',q=1,text=1)
  tf2 = cmds.textField('txt_anmR2',q=1,text=1)
  ts = cmds.sets(cmds.ls(selection=1))
  for i in range(sa) :
   lx = cmds.sets(ts,q=1)[i]
   sx = lx.split('|')[-1]
   rn = sx.replace(tf1,tf2)
   cmds.rename(cmds.sets(ts,q=1)[i],rn)        
  cmds.delete(ts)


 def findSameString(self,list,*a):
  sw = ''
  for h in range(1,len(list)):
   s1 = sw
   if h == 1 : s1 = list[0]
   s2 = list[h]
   sw = ''
   for i,x in enumerate(s1) :
    for j,y in enumerate(s1[i:]) :
     fs = x + s1[i+1:j+i+1]
     if s2.find(fs) >= 0 and len(fs)>len(sw) : sw = fs
  return sw
  
 def addPrefix(self,*a):
  sa = len(cmds.ls(selection=1))
  txt = cmds.textField('txt_anmPS',q=1,text=1)
  ts = cmds.sets(cmds.ls(selection=1))
  for i in range(sa):
   lx = cmds.sets(ts,q=1)[i]
   sx = lx.split('|')[-1]
   cmds.rename(lx,sx+x)
  cmds.delete(ts)

 def addSuffix(self,*a):
  sa = len(cmds.ls(selection=1))
  txt = cmds.textField('txt_anmPS',q=1,text=1)
  ts = cmds.sets(cmds.ls(selection=1))
  for i in range(sa):
   lx = cmds.sets(ts,q=1)[i]
   sx = lx.split('|')[-1]
   cmds.rename(lx,sx+txt)
  cmds.delete(ts)
   
 def correntShapeName(self,*a):
  for x in cmds.ls(selection=1):
   s = cmds.listRelatives(x,shapes=1,noIntermediate=1,fullPath=1)
   if len(s)==1:
    cmds.rename(s[0],x.split('|')[-1]+'Shape')
  
def as_naming():
 renameTool = as_namingUI()