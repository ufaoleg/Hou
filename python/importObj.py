import hou
import os
import re
import string

################################################################
# Shader definition -- Change it to match your shader
################################################################
# name of the shader
shader='mantrasurface' 
# parameters for diffuse color
difr='diff_colorr'
difg='diff_colorg'
difb='diff_colorb'
# parameters for specular color
specr='spec_colorr'
specg='spec_colorg'
specb='spec_colorb'
# parameter for opacity
opacity='opac_int'
#parameter for IOR
ior='ior_in'
# parameters for maps
use_diffmap='diff_colorUseTexture'
diff_map='diff_colorTexture'
use_specmap='refl_colorUseTexture'
spec_map='refl_colorTexture'
use_alphamap='opacity_colorUseTexture'
alpha_map='opacity_colorTexture'
use_bumpmap='enableBumpOrNormalTexture'
bump_map='normalTexture'

###############################################################

#input obj
file_name=hou.ui.selectFile(file_type=hou.fileType.Geometry)
file_old=file_name
file_name=string.replace(file_name,'$HIP',hou.expandString('$HIP'),1)
file_path=os.path.split(file_old)[0]

geo = hou.node('/obj').createNode('geo')
geo.node('file1').parm('file').set(file_old)
geo.moveToGoodPosition()
name=os.path.splitext(os.path.basename(file_name))[0].replace(' ','_')
if name[0].isdigit(): #Houdini does not allow to name nodes with first digit character
    name="_"+name
geo.setName(name,True) # replace space with _

mysop=geo.node('file1').createOutputNode('attribstringedit')
mysop.moveToGoodPosition()

shop=geo.createNode('shopnet')
shop.moveToGoodPosition()

# create node to relink materials to internal shopnet
mysop.parm('primattriblist').set('shop_materialpath')
mysop.parm('regex0').set(1)
mysop.parm('from0').set('/shop/')
mysop.parm('to0').set('`opfullpath("../shopnet1")+"/"`')
mysop.setDisplayFlag(True)
mysop.setRenderFlag(True)

# Create shaders

file_name=os.path.splitext(file_name)[0]+".mtl"
# if mtl file not found
if not os.path.isfile(file_name): 
    print('No mtl file, choose manually')
    file_name=hou.ui.selectFile()
error=0
last=mysop
cur_mat = None
with open(file_name, 'r') as f:
    lines = f.read().splitlines()   # Read lines
f.close()
 
for line in lines:
    line=line.lstrip()          # remove beginning spaces
    line=' '.join(line.split()) # remove double spaces
    ary = line.split(' ')
    if ary[0] == 'newmtl':
        # Grab the name of this new material
        mat_name = ary[1]   
        cur_mat = shop.createNode(shader)
        cur_mat.moveToGoodPosition()
        # check if first symbol of mat name is digit (prohibited in Houdini)
        if mat_name[0].isdigit():
            print('MAT NAME CHANGED!')
            # Create node to rename material
            mysop=last.createOutputNode('attribstringedit')
            mysop.moveToGoodPosition()
            mysop.parm('primattriblist').set('shop_materialpath')
            mysop.parm('regex0').set(1)
            mysop.parm('from0').set('shopnet1/'+mat_name)
            mysop.parm('to0').set('shopnet1/_'+mat_name)
            mysop.setDisplayFlag(True)
            mysop.setRenderFlag(True)
            last=mysop
            mat_name='_'+mat_name
        
        # check if mat name has prohibited characters
        if not re.match(r'[:\w-]*$', mat_name):
            print('MAT HAS WRONG CHARACTERS! Changed')
            mysop=last.createOutputNode('attribstringedit')
            mysop.moveToGoodPosition()
            mysop.parm('primattriblist').set('shop_materialpath')
            mysop.parm('regex0').set(1)
            mysop.parm('from0').set('shopnet1/'+mat_name)
            mysop.parm('to0').set('shopnet1/_'+'mat_changed_'+str(error))
            mysop.setDisplayFlag(True)
            mysop.setRenderFlag(True)
            last=mysop
            mat_name='_'+'mat_changed_'+str(error)
            error+=1
            
        cur_mat.setName(mat_name,True) #rename material

    if ary[0] == 'Kd':
        # Found a diffuse color.
        if len(ary) == 4:
            cur_mat.setParms({difr: float(ary[1]),difg: float(ary[2]),difb: float(ary[3])})
    if ary[0] == 'Ks':
        # Found a specular color.
        if len(ary) == 4:
            cur_mat.setParms({specr: float(ary[1]),specg: float(ary[2]),specb: float(ary[3])})

    if ary[0] == 'd':
        # Found opacity.
        cur_mat.setParms({opacity: float(ary[1])})

    if ary[0] == 'Ni':
        # Found IOR parameter
        cur_mat.setParms({ior: float(ary[1])})


    # maps
    if ary[0]== 'map_Kd' and len(ary)>1:
        cur_mat.setParms({use_diffmap:1})
        cur_mat.setParms({diff_map:file_path+'/'+ary[-1]}) # only last word in a string

    if ary[0]== 'map_Ks' and len(ary)>1:
        cur_mat.setParms({use_specmap:1})
        cur_mat.setParms({spec_map:file_path+'/'+ary[-1]})

    if ary[0]== 'map_d' and len(ary)>1:
        cur_mat.setParms({use_alphamap:1})
        cur_mat.setParms({alpha_map:file_path+'/'+ary[-1]})

    if ary[0]== 'map_bump' and len(ary)>1:
        cur_mat.setParms({use_bumpmap:1})
        cur_mat.setParms({'normalTexType':'bump'}) # For mantra shader only
        cur_mat.setParms({bump_map:file_path+'/'+ary[-1]})
