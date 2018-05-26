import hou

color1 = hou.Color((0.0, 0.0, 0.0)) # black
color2 = hou.Color((1.0, 0.0, 0.0)) # red
color3 = hou.Color((0.2, 0.2, 0.2)) # gray

node = hou.selectedNodes()[0]
geo_node_path = "/obj/" + str(node.parent())
geo_node = hou.node(geo_node_path)
geo_node.setColor(color3)
geo_node.setDisplayFlag(False)

groups = [g.name() for g in node.geometry().primGroups()]

last = node

name = ""

def create_geo_node(_name, idx):
    out_suffix = 'OUT_'
    geo_group = hou.node("/obj").createNode("geo", _name)
    pos = geo_node.position() + hou.Vector2(0,-idx)
    geo_group.setPosition(pos)
    hou.node("/obj/"+geo_group.name()+"/file1").destroy()
    merge = geo_group.createNode("object_merge", "IN")
    merge.setColor(color1)
    merge.parm("objpath1").set(geo_node_path+"/"+out_suffix+_name)
    merge.parm("xformtype").set(1)
        
for i, name in enumerate(groups, 1):
    pos = last.position() + hou.Vector2(-1,-1)
    if i == 1:
        splitNode = last.createOutputNode('split', "spl_"+name)
        splitNode.setInput(0,last,0)
    else:
        out = last.createOutputNode('null', 'OUT_'+last.parm("group").evalAsString())
        out.moveToGoodPosition()
        out.setColor(color1)
        out.setPosition(pos)
        splitNode = out.parent().createNode('split', "spl_"+name)
        splitNode.setInput(0,last,1)
    splitNode.moveToGoodPosition()
    splitNode.parm("group").set(name)
    splitNode.moveToGoodPosition()
    splitNode.parm("removegrp").set(1)
    splitNode.setDisplayFlag(True)
    splitNode.setRenderFlag(True)
    last = splitNode
    create_geo_node(name, i)
    

out = last.createOutputNode('null', 'OUT_'+name)
out.setColor(color1)
out.setPosition(last.position() + hou.Vector2(-1,-1))
