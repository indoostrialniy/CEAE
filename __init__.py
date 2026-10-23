bl_info = {
    "name": "CEAE v0.4.9",
    "author": "Paul",
    "version": (0,4,9),
    "blender": (4,0,2),
    "category": "Indoostrialniy",
    "description": "23.10.2026. This addon helps to export assets to custom engine",
}


import bpy
import os
import math
import mathutils
import numpy as np
import datetime

from array import array
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty)
from bpy.types import (Panel, Menu, Operator, PropertyGroup, AddonPreferences)
from pathlib import Path
# ~ from PIL import Image

ROUND_LEVEL = 4

runtimeCounter = 0

ALREADY_EXPORTED_RESOURCES = []

def ShowMessageBox(message = "", title = "", icon = ""):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    return


class exportLightmapClass(bpy.types.Operator):
    bl_idname = 'mesh.export_lightmap' #запуск командой mesh.output_list_of_objects
    bl_label = 'Export lightmap to file'
    bl_description = "print objects`s lightmap to file"

    #-- только при наличии материалов создаст ноды для лайтмапов
    def bindLightmap(OBJECT, self, context):
        for mat in (mat2 for mat2 in OBJECT.data.materials if OBJECT.data.materials): #-- если есть материалы, пройдемся по ним

            if context.scene.bDraftLightmaps == True:
                size = 128
            else:
                size = OBJECT["LightmapSize"] if "LightmapSize" in OBJECT.keys() else int(context.scene.eLightmapSize)*256

            #-- имя данного файла
            currentFileName = bpy.path.basename(bpy.context.blend_data.filepath)
            currentFileName = currentFileName[0:len(currentFileName)-6]

            textureName = 'lm_' + currentFileName + '_' + OBJECT.name + '_' + str(size)+ '.png' #имя для текстуры карты света

            if textureName not in (texture.name for texture in bpy.data.images): #если текстура не существует в проекте, создадим
                #print('No image [' + str(textureName) + ']. Create new!')
                bpy.ops.image.new(name = textureName, width=size, height=size, alpha = True ) #создали новую текстуру лайтмапа
                bpy.data.images[textureName].file_format = "PNG"

            if textureName not in (nodeImage.image.name for nodeImage in mat.node_tree.nodes if nodeImage.type == 'TEX_IMAGE' and nodeImage.image): # если текстура не назначена ноду изображения в материале, создадим новую ноду и назначим ей эту текстуру
                #print('No image node with texture [' + str(textureName) + '] found in material [' + str(mat.name))
                bsdf = mat.node_tree.nodes['Principled BSDF']
                lightmapNode    = mat.node_tree.nodes.new('ShaderNodeTexImage') #создадим новую ноду изображения
                lightmapNode.location.x = bsdf.location.x-350
                lightmapNode.location.y = bsdf.location.y+350
                lightmapNode.image = bpy.data.images[textureName]

            OBJECT["Lightmap"] = bpy.data.images[textureName]
            OBJECT["LightmapSize"] = int(size)


    #-- выделит только заданный объект и только при наличии материалов и яному указанию запечет
    def bakeLightmap(OBJECT, self, context):
        #print('\t\tBake obj: [' + str(OBJECT.name) +']')

        # -- явно выделим ТОЛЬКО конкретный объект
        for obj in bpy.data.objects:
            obj.select_set(False)
        bpy.context.view_layer.objects.active = None
        OBJECT.select_set(True)
        bpy.context.view_layer.objects.active = OBJECT
        # -- объект выделен

        #material = OBJECT.data.materials[0]
        #if material:
        for material in (material2 for material2 in OBJECT.data.materials if OBJECT.data.materials):#-- если есть материалы, пройдемся по ним
            # -- сняли выделение со всех нодов
            if bpy.data.materials:
                for everyMat in bpy.data.materials:
                    if everyMat.node_tree and everyMat.node_tree.nodes:
                        for everyMatNode in everyMat.node_tree.nodes:
                            everyMatNode.select = False
                        everyMat.node_tree.nodes.active = None

            #-- попробуем взять размер лайтмапа из свойства объекта. Стопудово получится, ибо bindLightmaps уже выполнилась
            size = OBJECT["LightmapSize"] if "LightmapSize" in OBJECT.keys() else int(context.scene.eLightmapSize)*256

            #-- имя данного файла
            currentFileName = bpy.path.basename(bpy.context.blend_data.filepath)
            currentFileName = currentFileName[0:len(currentFileName)-6]

            textureName = 'lm_' + currentFileName + '_' + OBJECT.name + '_' + str(size)+ '.png' #имя для текстуры карты света

            #-- нашли в материале текстурную ноду с привязанной лайтмапой. Т.е. цикл сработает лишь один раз
            for noda in ( node for node in material.node_tree.nodes if node.type == 'TEX_IMAGE' and node.image and node.image.name == textureName):
                noda.select = True
                material.node_tree.nodes.active = noda
                if context.scene.bBakeLightmaps == True:
                    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT'}, use_clear=True)
                break


    # ~ def exportLightmap(OBJECT, self, context):
        # ~ if context.scene.bExportLightmaps == True:
            # ~ if OBJECT["Lightmap"].name not in EXPORTED_ASSETS:
                # ~ slash = '/' if context.scene.operationSystem == "0" else '\\'
                # ~ texturesPath    = context.scene.projectFolder + slash + 'textures' + slash

                # ~ filename = texturesPath + slash + OBJECT["Lightmap"].name

                # ~ OBJECT["Lightmap"].save_render(filename)
                # ~ EXPORTED_ASSETS.append(OBJECT["Lightmap"].name)


    def execute(self, context):
        #EXPORTED_ASSETS.clear()
        
        OBJECT = bpy.context.active_object

        #exportLightmapClass.bindLightmap(OBJECT, self, context)
        

        # ~ for elem in bpy.context.selected_objects:

            # ~ setExporterClass.exportSoloObject(elem, self, context)

        
        #-- сконфигурируем материал для данного объекта
        # if OBJECT.data.materials:
        if OBJECT.type == 'MESH':
            print('\nObject: ' + str(OBJECT.name))

            # ~ exportMaterialClass.configureMaterial(OBJECT, '\t\t')

            # ~ exportLightmapClass.bindLightmap(OBJECT,self, context)

            # ~ exportLightmapClass.bakeLightmap(OBJECT,self, context)

            #exportLightmapClass.exportLightmap(OBJECT,self, context)


        # logFile = open(context.scene.logFolder, 'a') #откроем файл для дозаписи нового содержимого
        # logFile.write('\n\n//-----------------------------------\nNEW DATA ' + str(datetime.datetime.now()) + '\n')
        # logFile.write(str(EXPORTED_ASSETS))
        # logFile.close()

        return {'FINISHED'}




class exportCollisionBoxClass(bpy.types.Operator):
    bl_idname = 'mesh.export_collision' #запуск командой mesh.output_list_of_objects
    bl_label = 'Export collision mesh to file'
    bl_description = "print objects`s collision shell to file"
    
    def ShowMessageBox(message = "", title = "", icon = ""):
        def draw(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
        return
    
    def export_collision(self, context, collision):
        print('\n\nExporting collision [%s]'%(collision.name))

        slash = '/' if context.scene.operationSystem == "0" else '\\'
        collisionPath = context.scene.projectFolder + slash + 'meshes' + slash + collision.data.name + '.collision'

        collisionFile = open(collisionPath, 'w') #или obj.data.name?

        collisionFile.write(';'+ str(datetime.datetime.now()) + '\n;name ' + str(collision.name)+'\n')

        print('\n;this script exports CB as divided description of vertexes and polygons with normals\n')

        vertices = 0
        for v in collision.data.vertices:
            vertices += 1


        edges = 0
        for e in collision.data.edges:
            edges += 1

        polygons = 0
        for p in collision.data.polygons:
            polygons += 1

        collisionFile.write('\nvertices %i\nedges %i\npolygons %i\n'%(vertices, edges, polygons) )

        collisionFile.write('\ndata\n')


        # obj_verts = collision.data.vertices ## указали, что смотрм вершины


        collisionFile.write('\n//vertices: index + coordinates (x y z)\n')
        vertex_index = 0
        for vertex in collision.data.vertices:
            collisionFile.write('v %i %f %f %f\n'%(vertex_index, vertex.co[0] + vertex_index/1000, vertex.co[1] + vertex_index/1000, vertex.co[2]) ) #добавим смещение по Х, чтобы исключить одинаковые координаты вершин при расчете коллизий
            #collisionFile.write('v %i %f %f %f\n'%(vertex_index, vertex.co[0], vertex.co[1], vertex.co[2]) )
            vertex_index += 1

        collisionFile.write('\n//edges: index + indexes of verts (v0 v1)\n')
        edge_index = 0
        for edge in collision.data.edges:
    #        collisionFile.write(edge.vertices[0])
            collisionFile.write('e %i %i %i\n'%(edge_index, edge.vertices[0], edge.vertices[1] ) )
            edge_index += 1


        collisionFile.write('\n//polygons: index + indexes of verts (i0 i1 i2) + normal(x y z)\n')
        polygon_index = 0
        for triangle in collision.data.polygons:
            collisionFile.write('p %i %i %i %i %f %f %f\n'%(polygon_index, triangle.vertices[0], triangle.vertices[1], triangle.vertices[2], triangle.normal[0], triangle.normal[1], triangle.normal[2]))
            polygon_index += 1

#         if collision.data.polygons:
#             collisionFile.write(';polygon (p) format: xyza xyzb xyzc nxnynzd\n')
#             obj_verts = collision.data.vertices ## указали, что смотрм вершины
#             faces = 0
#             for uv_layer in collision.data.uv_layers: #перебираем текстурные слои
#                 for triangle in collision.data.polygons:
#                     #collisionFile.write( str(triangle.index)+' `triangle \n') #пишем начало строки - f
#
#                     #print(str(faces))
#                     collisionFile.write('\n')
#
#                     vv = 0
#                     collisionFile.write('p %i \n'%(faces))
#
#                     for i in triangle.vertices: # перебираем индексы вершин треугольника
#                         collisionFile.write('%f %f %f 0\n'%(round(obj_verts[i].co[0], 4), round(obj_verts[i].co[1], 4), round(obj_verts[i].co[2], 4) ))
#
#                         vv = vv+1
#                     collisionFile.write('%f %f %f 0\n'%(triangle.normal[0], triangle.normal[1], triangle.normal[2]))
#                     faces = faces +1
#
#             print('Success')
#         else:
#             #return False
#             print('Error, collision mesh has no polygons!')



        collisionFile.close()

        return collisionPath
        #----end of script
    
    
    def execute(self, context):
        aabb_box = bpy.context.active_object        # выберем объект


        if aabb_box.type == 'MESH': # and aabb_box.data.uv_layers: #проверим, что это арматура
            try:
                outputfile = exportCollisionBoxClass.export_collision(self, context, aabb_box)
                title = 'Оболочка [' + str(aabb_box.name) + '] экспортирована как [' + str(outputfile) + ']!'
                exportCollisionBoxClass.ShowMessageBox(title, 'Collision log:', 'BLENDER')
            except:
                exportCollisionBoxClass.ShowMessageBox('Ошибка! См.консоль python', 'Collision log:', 'BLENDER')
        else:
            exportCollisionBoxClass.ShowMessageBox('Ошибка! Выделен не Mesh!', 'Collision log:', 'BLENDER')
        return {'FINISHED'}
    
    

class exportArmatureClass(bpy.types.Operator):
    bl_idname = 'mesh.export_armature' #запуск командой mesh.output_list_of_objects
    bl_label = 'Export armature to file'
    bl_description = "print objects`s skeleton to file"

    number_of_digits = 4 #количество знаков после запятой

    def ShowMessageBox(message = "", title = "", icon = ""):
        def draw(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
        return

    def gME(matrix, index): #get matrix element
        c = index // 3; 	#частное от деления: 0 0 0 0 1 1 1 1 2 2 2 2 3 3 3 3
        s = index % 3;	#остаток от деления: 0 1 2 3 0 1 2 3 0 1 2 3 0 1 2 3

        return matrix[c][s]



    def BASIC_LSK_MATRICES(arm, skeletonFile):
        bpy.context.scene.frame_set(0)

        if arm.pose.bones:
            skeletonFile.write('//default bind-pose LSK matrices of all bones as quats x y z w\n')

            for bone in arm.pose.bones:

                # преобразуем ЛСК матрицу в кватернион для экономии места
                bm = bone.matrix

                # для соответствия формулы из расчетов и блендеровской матрицы, надо так
                # 00 01 02    1 2 3
                # 10 11 12    4 5 6
                # 20 21 22    7 8 9
                print(str(bone))
                qx = ( bm[2][1] - bm[1][2] ) / (4 * math.sqrt( (1+bm[0][0] + bm[1][1] + bm[2][2] )/4 )  )
                qy = ( bm[0][2] - bm[2][0] ) / (4 * math.sqrt( (1+bm[0][0] + bm[1][1] + bm[2][2] )/4 )  )
                qz = ( bm[1][0] - bm[0][1] ) / (4 * math.sqrt( (1+bm[0][0] + bm[1][1] + bm[2][2] )/4 )  )
                qw = math.sqrt( ( 1+bm[0][0] + bm[1][1] + bm[2][2] )/4 )
                skeletonFile.write('m %s %f %f %f %f\n'%(bone.name, qx, qy, qz, qw))


                # старая версия, ЛСК задается матрицей напрямую
                # skeletonFile.write('m ' + str(bone.name))
                # for a in range(16): # write in line the orientation matrix
                #     b = a//4
                #     c = a%4
                #     skeletonFile.write(' ' + str(  round(  bone.matrix[c][b], 4 )  )    )
                # skeletonFile.write('\n')


            bpy.context.scene.frame_set(0)
            return True
        else:
            return False


    def BASIC_HEADS(arm, skeletonFile):
        bpy.context.scene.frame_set(0)
        if arm.pose.bones:
            skeletonFile.write('\n\n//default bind-pose heads of all bones x y z\n')
            for bone in arm.pose.bones:#arm.pose.bones:
                head = bone.head
                quaternion = bone.rotation_quaternion

                skeletonFile.write('h '+str(bone.name)+' ')
                skeletonFile.write(str(round( 1 * head.x, 4))+' '+ str(round( 1 * head.y, 4))+' '+str(round( 1 * head.z, 4))+'\n')
                #skeletonFile.write(str(round(quaternion.x, 4))+' '+ str(round(quaternion.y, 4))+' '+str(round(quaternion.z, 4))+' '+str(round(quaternion.w, 4))+'\n')
            bpy.context.scene.frame_set(0)
            return True
        else:
            return False


    ## ПЕЧАТАЕМ ИЕРАРХИЮ
    def PRINT_BONE_IERARCHY(arm, skeletonFile):
        skeletonFile.write('\nBone_ierarchy (branch`s bones serial numbers, parents lists for every bone)\n' + str(0) + ' ' + str(1) + ' strings and rows\n')

        bone_serial = 0 #порядковый номер кости
        for bone in arm.pose.bones: #перебираем все кости

            skeletonFile.write('ie '  + str(bone_serial)+'')   #+str(bone.name)+' ') #пишем зацепер и 'b '+str(serial_number)+' '+
            parents_list = bone.parent_recursive #список родителей вплоть до главной
            for parents in parents_list:
                #file.write(str(parents.name)+'') #определили имя родителя
                bone_counter=0
                for bone2 in arm.pose.bones:    #переберем все кости, чтобы определить порядковый номер родительской кости
                    if parents.name==bone2.name:
                       skeletonFile.write(' ' + str(bone_counter)+'') #пишем порядковый номер кости в цепочке
                    bone_counter=bone_counter+1
            skeletonFile.write('\n') #' ' +str(bone.name)+
            bone_serial+=1

        skeletonFile.write('END IERARCHY PARAMS\n\n')
        return True



    def export_skeleton(self, context, skelet):
        print('\n\nExporting armature [%s]'%(skelet.name))

        slash = '/' if context.scene.operationSystem == "0" else '\\'
        skeletonPath = context.scene.projectFolder + slash + 'animations' + slash + skelet.name + '.arm'

        skeletonFile = open(skeletonPath, 'w') #или obj.data.name?

        skeletonFile.write(';'+ str(datetime.datetime.now()) + '\nname ' + str(skelet.name)+'\n')

        print('...Process...')

        if skelet.pose.bones:
            skeletonFile.write('bones '+str( len(skelet.pose.bones) )+'\n') # СЧИТАЕМ КОЛИЧЕСТВО КОСТЕЙ
            exportArmatureClass.BASIC_LSK_MATRICES(skelet, skeletonFile)
            print('LSK matrices exported!')
            exportArmatureClass.BASIC_HEADS(skelet, skeletonFile)
            print('Heads exported!')
            exportArmatureClass.PRINT_BONE_IERARCHY(skelet, skeletonFile) # напечатали список родительских костей для каждой кости
            print('Ierarchy exported!')
            skeletonFile.write('\n//Attached animations') # после этого дописать назначенные анимации
        else:
            #return False
            print('Error, armature has no bones!')



        skeletonFile.close()

        return skeletonPath
        #----end of script


    def execute(self, context):
        armature = bpy.context.active_object        # выберем объект


        if armature.type == 'ARMATURE': #проверим, что это арматура
            try:
                outputfile = exportArmatureClass.export_skeleton(self, context, armature)
                title = 'Скелет [' + str(armature.name) + '] экспортирован как [' + str(outputfile) + ']!'
                exportArmatureClass.ShowMessageBox(title, 'Armature log:', 'BLENDER')
            except:
                exportArmatureClass.ShowMessageBox('Ошибка! См.консоль python', 'Armature log:', 'BLENDER')
        else:
            exportArmatureClass.ShowMessageBox('Ошибка! Выделен не Armature!', 'Armature log:', 'BLENDER')
        return {'FINISHED'}




class exportAnimationClass(bpy.types.Operator):
    bl_idname = 'mesh.export_animation' #запуск командой mesh.output_list_of_objects
    bl_label = 'Экспортировать анимацию'
    bl_description = "Нажатие кнопки приведет к экспорту\nв рабочую папку 'Project folder'\nдля скелета 'Armature' анимации, назначенной в текущий DopeSheet "

    number_of_digits = 4 #количество знаков после запятой

    def ShowMessageBox(message = "", title = "", icon = ""):
        def draw(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
        return


    ## ???
    ##  ФУНКЦИЯ ВОЗВРАЩАЕТ КОЛИЧЕСТВО КОСТЕЙ
    def COUNT_OF_BONES(object): #функция возвращает количество костей в object
        a=0
        for b in object.data.bones:
            a=a+1
        return a

    ## ???
    def BONE_MATRICES(arm, animFile, key):
        #нужно распечатать матрицы костей в дефолтном положении



        bpy.context.scene.frame_set(0)
        #bpy.ops.pose.copy()
        #bpy.ops.pose.rot_clear()
        #bpy.ops.pose.transforms_clear()

        for bone in arm.pose.bones:

            animFile.write('m 2')
            #animFile.write(str(bone.matrix)+'\n')
            for a in range(16):
                b = a//4
                c = a%4
                animFile.write(' ' + str(  round(bone.matrix[c][b], 4)  )    )
            animFile.write(' ' + str(bone.name) + '\n')






    ###########################################################################
    ## ФУНКЦИЯ ПЕЧАТАЕТ ИЕХАРХИЮ КОСТЕЙ
    string_count=0
    row_count = 0
    bone_line={} #массив для хранения костей ветви
    # узнаем максимальную длину ветви костей, функция считает размеры массива
    ## ???
    def IERARCHY_SIZE(arm, parent, step):
        exportAnim.bone_line[0]=arm.pose.bones[0].name
        if parent.children: #если дети есть, то
            step = step+1 #делаем отступ больше
            #string_count = string_count+1
            for child in parent.children:    #цикл перечислений дочерних костей
                exportAnim.bone_line[step]=child.name
                exportAnim.IERARCHY_SIZE(arm, child, step)#, string_count)
        else: #выводим элементы
            global row_count
            if len(exportAnim.bone_line) > exportAnim.row_count:
                exportAnim.row_count = len(exportAnim.bone_line)

    ## ???
    def checkInfluence(arm, bone):
        weight = 0
        BONE = bone#bpy.context.active_object.data.bones[0]

        #print(str(BONE.name))

        #weight = 0

        if BONE.name == 'root':
            weight = 1

        if bpy.context.active_object.type == 'ARMATURE':
            mesh = bpy.context.active_object.children[0]

        if bpy.context.active_object.type == 'MESH':
            mesh = bpy.context.active_object
        #for gr in bpy.context.active_object.children[0].vertex_groups:
        for gr in mesh.vertex_groups:
            #print(gr.name)
            if gr.name == BONE.name:# and LIKbone.name != 'root':
                weight = 1
                break
        return weight

    ## ???
    ###########################################################################
    ## ПЕЧАТАЕМ ИЕРАРХИЮ
    def PRINT_BONE_IERARCHY(arm, animFile):

        exportAnim.IERARCHY_SIZE(arm, arm.pose.bones[0], 0)
        string_count = exportAnim.COUNT_OF_BONES(arm) #определили количество строк, оно совпадает с количеством костей
        animFile.write('\nBone_ierarchy (branch`s bones serial numbers, parents lists for every bone)\n' + str(exportAnim.string_count) + ' ' + str(exportAnim.row_count) + ' strings and rows\n')

        V_GROUPS = [group.name for group in arm.children[0].vertex_groups ]
        BONES = [bone.name for bone in arm.pose.bones ]

        bone_serial = 0 #порядковый номер кости
        for bone in arm.pose.bones: #перебираем все кости
            #определим, влияет ли кость на кого нибудь
            #weight = 0
            #BONE = bone#bpy.context.active_object.data.bones[0]

            #print(str(BONE.name))

            #weight = 0

            #if BONE.name == 'root':
            #    weight = 1

            #for gr in bpy.context.active_object.children[0].vertex_groups:
            #    #print(gr.name)
            #    if gr.name == BONE.name:# and LIKbone.name != 'root':
            #        weight = 1

            #if bone.name in V_GROUPS:#
            #if exportAnim.checkInfluence(arm, bone) == 1: #рабочий?
            #print(str(BONE.name) + ', weight: ' +str(weight))
            #animFile.write('ie weight '  + str(weight) + ', ' + str(bone_serial)+'')
            animFile.write('ie '  + str(bone_serial)+'')   #+str(bone.name)+' ') #пишем зацепер и 'b '+str(serial_number)+' '+
            parents_list = bone.parent_recursive #список родителей вплоть до главной
            for parents in parents_list:
                #file.write(str(parents.name)+'') #определили имя родителя
                bone_counter=0
                for bone2 in arm.pose.bones:    #переберем все кости, чтобы определить порядковый номер родительской кости
                    if parents.name==bone2.name:
                        animFile.write(' ' + str(bone_counter)+'') #пишем порядковый номер кости в цепочке
                    #if exportAnim.checkInfluence(arm, bone2) == 1:
                    bone_counter=bone_counter+1
            animFile.write('\n') #' ' +str(bone.name)+
            bone_serial+=1

        animFile.write('END IERARCHY PARAMS\n\n')

    ## ???
    ###########################################################################
    ##  ФУНКЦИЯ РИСУЕТ СТРУКТУРУ СКЕЛЕТА
    def CHECK_CHILDREN(storage, arm, parent, step):    #в функцию получаем кость и количество отступов
        if parent.children: #если дети есть, то
            step = step+5 #делаем отступ больше
            for child in parent.children:    #цикл перечислений дочерних костей
                for number in range(step):    #цикл оформления отступа - step пробелов
                    storage.write(' ')
                storage.write(''+str(child.name)+' '+str()+' ')    #пишем имя кости

                bones = [b for b in arm.pose.bones]
                serial = 0
                for inti in bones:
                    if inti.name == child.name:
                        #file.write('serial '+str(serial)+'\n')    #пишем имя кости
                        storage.write('\n')

                    serial = serial+1
                #file.write(''+str(child.location)+'\n')
                exportAnim.CHECK_CHILDREN(child, step)


    ## ???
    # ФУНКЦИЯ ПЕЧАТАЕТ СПИСОК КОСТЕЙ И ИХ ХАРАКТЕРИСТИК
    def BONE_POSES_LIST(arm, animFile, current_key, K):
        bpy.context.scene.frame_set(current_key)
        #bpy.ops.anim.keyframe_insert_by_name(type="BUILTIN_KSI_VisualLocRot")
        for bone in arm.pose.bones:
            #на этом моменте нужно запечь позу
            #bpy.ops.nla.bake(frame_start = current_key, frame_end = current_key, bake_types={'OBJECT'})

            head = bone.head# + bone.location
            tail = bone.tail


            animFile.write('b '+str(bone.name)+' ')
            #animFile.write('b '+str(bone.name)+' key: ' + str(current_key) + ' head: ')
            animFile.write(str(round( 1 * head.x, 4))+' '+ str(round( 1 * head.y, 4))+' '+str(round( 1 * head.z, 4))+' ')
            #bpy.context.scene.frame_set(current_key) #вернули текущий кадр

            location = bone.location
            quaternion = bone.rotation_quaternion
            animFile.write('' + str(round( K * location.x, 4))+' '+ str(round( K * location.y, 4))+' '+str(round( K * location.z, 4))+' ')
            #animFile.write(str(total)+' ')#+ str(total[1])+' '+str(total[2])+' ')
            #animFile.write(str(round(tail.x, 4))+' '+ str(round(tail.y, 4))+' '+str(round(tail.z, 4))+' ')
            #file.write(str(bone.rotation_quaternion)+' \n')
            #file.write(str(quaternion.x) + ' ' + str(-quaternion.z) + ' ' + str(quaternion.y) + ' ' + str(quaternion.w) + '\n')    #пишем вращение


            animFile.write(''+str(round(quaternion.w, 4)) + ' ' + str(round(quaternion.x,4)) + ' ' + str(round(quaternion.y,4)) + ' ' + str(round(quaternion.z,4)) )#+ ' tail ' + str(tail))
            animFile.write(' '+ str(round( K * tail.x, 4))+' '+ str(round( K *  tail.y, 4))+' '+str(round( K * tail.z, 4)) + ' ' + str(round( K * bone.length, 4)))
#            for a in range(16):
#                b = a//4
#                c = a%4
#                animFile.write(' ' + str(  round(bone.matrix[c][b], 4)  )    )
            animFile.write('\n')

            #file.write(str(bone.matrix)+'\n')
            

    # в эту функцию можно придти, только пройдя проверки на наличие выбранного скелета и анимации
    # функция экспортирует в файл выбранную анимацию, при необходимости запекая Visual keying
    def exportSelectedAnimation(self, context, armature, animation):

        print('\n\nExporting animation [%s] for armature [%s]'%(animation.name, armature.name ))

        slash = '/' if context.scene.operationSystem == "0" else '\\'           # для закулисного определения стиля файлового пути вводим вспомогательную переменную
        animFileName = context.scene.projectFolder + slash + 'animations' + slash + animation.name +'.anim'
        animFile = open(animFileName, 'w')   # открываем для записи файл с именем анимации


        # начало функционала для запекания
        EXISTING_LOCAL_ACTIONS = [ act for act in bpy.data.actions if act.library == None ] # запомним, какие анимации были В ЭТОМ файле до начала процедуры экспорта

        #print(EXISTING_LOCAL_ACTIONS)
        bpy.context.active_object.animation_data.action = animation  # занесем экспортируемую анимацию в DopeSheet

        start = int(animation.frame_range.x)
        end = int(animation.frame_range.y)

        frameRange = animation.frame_range.y - animation.frame_range.x + 1      # общее число кадров в анимации
        print( 'Frames: %i'%(frameRange) )

        print( 'Duration: %f'%( float(frameRange)/float(60)) )

        bpy.ops.nla.bake(frame_start=start, frame_end=end, step=10, visual_keying=True, only_selected=False, use_current_action=False, bake_types={'POSE'}) # запечем визуал в новую Action

        for act in (anim for anim in bpy.data.actions if anim.library == None and anim not in EXISTING_LOCAL_ACTIONS ): # с помощью массива определим, какая Action добавилась
            tempAction = act

        bpy.context.active_object.animation_data.action = tempAction    # назначим в DopeSheet новую запеченную анимацию

        #animation = tempAction
        # конец функционала для запекания



        armatureBonesMassive = [bone.name for bone in armature.pose.bones]           # массив каналов анимации, (групп, одноименных с костями)

        armatureBonesCount = len(armatureBonesMassive)                          # количество каналов (групп/костей)





        armatureCurvesMassive = [curve for curve in tempAction.fcurves]          # массив Ф-кривых анимации

        fcurvesCount = len(armatureCurvesMassive)                               # их количество


        print( 'Count of bones: %i'%(armatureBonesCount) )

        print( 'Count of fcurves: %i'%(fcurvesCount) )



        animFile.write('Animation [%s] for armature [%s], %s \n'%(tempAction.name, armature.name, datetime.datetime.now() )  )
        animFile.write('bones ' + str(armatureBonesCount)+'\n')
        animFile.write('frames ' + str(frameRange)+'\n')
        animFile.write('seconds %f\n'%( float(frameRange)/float(60)) )

        animFile.write('curves ' + str(fcurvesCount)+'\n')

        animFile.write('Format: BoneName->Channels-> paars (int)key- (float)value (example: loc  x [0 0.0, 30 0.18796, 59 0.0])\n')

        for bone in tempAction.groups:
            #print('\n' + str(bone.name))
            animFile.write('\nbone ' + str(bone.name) + '\n')
            for channel in tempAction.groups[bone.name].channels:   #[0].keyframe_points:
                #print('channel ' + str(channel.data_path))
                # if channel.array_index == 0:                           # определим член вектора location - x,y или z
                #     xyzw = 'x'
                # elif channel.array_index == 1:
                #     xyzw = 'y'
                # elif channel.array_index == 2:
                #     xyzw = 'w'

                if channel.data_path.find("location") != -1:        # если присутствует слово "location"
                    keys = [ str(int(k.co.x))+" " + str(round(k.co.y, ROUND_LEVEL)) for k in channel.keyframe_points]
                    #print('loc  ' + str(xyzw) + ' '  + str(keys))
                    if channel.array_index == 0:                           # определим член вектора location - x,y или z
                        xyzw = 'x'
                    elif channel.array_index == 1:
                        xyzw = 'y'
                    elif channel.array_index == 2:
                        xyzw = 'z'
                    animFile.write('loc_'+ str(xyzw) )        # левая часть строки канала
                    for paar in keys:                                   # правая часть строки
                        animFile.write(' ' + str(paar))
                    animFile.write('\n')                                # и перенос

                if channel.data_path.find("euler") != -1:           # если присутствует слово "euler"
                    keys = [ str(int(k.co.x))+" " + str(round(k.co.y*180/3.14, ROUND_LEVEL)) for k in channel.keyframe_points]
                    #print('euler ' + str(xyzw) + ' ' + str(keys))
                    if channel.array_index == 0:                           # определим член вектора location - x,y или z
                        xyzw = 'x'
                    elif channel.array_index == 1:
                        xyzw = 'y'
                    elif channel.array_index == 2:
                        xyzw = 'z'
                    animFile.write('euler_'+ str(xyzw) )       # левая часть строки канала
                    for paar in keys:                                   # правая часть строки
                        animFile.write(' ' + str(paar))
                    animFile.write('\n')                                # и перенос

                if channel.data_path.find("quaternion") != -1:      # если присутствует слово "quaternion"
                    keys = [ str(int(k.co.x))+" " + str(round(k.co.y, ROUND_LEVEL)) for k in channel.keyframe_points]

                    #keys = [ str(int(k.co.x))+ " " + str(round(k.co.y, ROUND_LEVEL)) if abs(k.co.y) > 0.0001 else str(0) for k in channel.keyframe_points]
                    #print('quat  ' + str(xyzw) + ' '  + str(keys))
                    if channel.array_index == 0:                           # определим член вектора location - x,y или z
                        xyzw = 'w'
                    elif channel.array_index == 1:
                        xyzw = 'x'
                    elif channel.array_index == 2:
                        xyzw = 'y'
                    else:
                        xyzw = 'z'
                    animFile.write('quat_'+ str(xyzw) )       # левая часть строки канала
                    for paar in keys:                                   # правая часть строки
                        animFile.write(' ' + str(paar))
                    animFile.write('\n')                                # и перенос

        print('\nOk!')
        animFile.write('\nOk!')

        animFile.close()


        bpy.data.actions.remove(tempAction) #context.scene.action_baked)

        bpy.context.active_object.animation_data.action = animation

        return animFileName
        ##----end of script

	
    def execute(self, context):

        armature = bpy.context.active_object        # выберем объект
        animation = context.scene.action            # укажем в панели плагина экспортируемую анимацию

        if armature.type == 'ARMATURE' and animation: #проверим, что это арматура и выбрана анимация
            try:
                outputfile = exportAnimationClass.exportSelectedAnimation(self, context, armature, animation)
                title = 'Анимация [' + str(animation.name) + '] экспортирована как [' + str(outputfile) + ']!'
                exportAnimationClass.ShowMessageBox(title, 'Animator log:', 'BLENDER')
            except:
                exportAnimationClass.ShowMessageBox('Ошибка! См.консоль python', 'Animator log:', 'BLENDER')
        else:
            exportAnimationClass.ShowMessageBox('Ошибка! Выделена не Armature либо не выбрана Action!', 'Animator log:', 'BLENDER')
        return {'FINISHED'}




class exportMeshClass(bpy.types.Operator):
    bl_idname = 'mesh.export_mesh' #запуск командой mesh.output_list_of_objects
    bl_label = 'Export mesh to file'
    bl_description = "print objects`s mesh to file"

    
    ## FUNC START #######################################################
    def meshTriangulated(level_object):
        triangles = 0
        quads = 0

        for polygon in level_object.data.polygons:
            if len(polygon.vertices) == 3:
                triangles += 1
            if len(polygon.vertices) == 4:
                quads += 1

        if triangles > 0 and quads == 0:
            print('%s triangulated'%(level_object.name))
            return 1
        if quads > 0 and triangles == 0:
            print('NOT triangulated')
            return 0
    ## FUNC END #########################################################


    ## FUNC START #######################################################
    def export_model(self, context, level_object):  #сюда пришел указатель на объект меша, в том числе дубликата!

        

        slash = '/' if context.scene.operationSystem == "0" else '\\'

        name_mesh = level_object.data.name

        if name_mesh[len(name_mesh)-4] == '.' :   #обрезаем точку и номер
            name_mesh = name_mesh[0:len(name_mesh)-4]
            
        if name_mesh not in ALREADY_EXPORTED_RESOURCES:
            ALREADY_EXPORTED_RESOURCES.append(name_mesh)
        else:
            return #возвращаемся из функции, ибо данна модель уже была ранее экспортирована
            
        ####if name_mesh[len(name_mesh)-2] == '_' :   #обрезаем _temp
        ####    name_mesh = name_mesh[0:len(name_mesh)-2]

        meshPath = context.scene.projectFolder + slash + 'meshes' + slash + name_mesh

        #print('\n\nFOUND'+str( ) )


        if name_mesh.find("UCX") == -1: # экспортируем меш, только если это не ААВВ-коробка (т.е. UCX не найдено в названии)
            #logFile = open(context.scene.logFolder, 'a') #откроем файл для дозаписи нового содержимого
            print('\n\nExporting mesh %s\n'%(name_mesh))


            if exportMeshClass.meshTriangulated(level_object) == 0:
                print('Model ' + str(name_mesh) + ' not triangulated, skip\n')
                return

            try:
                #slash = '/' if context.scene.operationSystem == "0" else '\\'
                meshesPath    = context.scene.projectFolder + slash + 'meshes' + slash

                if context.scene.bModelsAsText == True:
                    file_model = open(meshesPath + name_mesh + '.ltx', 'w')

                if context.scene.bModelsAsBinary == True:
                    file_model_bin = open(meshesPath + name_mesh + '.model', 'wb')
            except:
                print('exportMesh() cannot create files, check path\n')
                return


            def writeb(value):
                if context.scene.bModelsAsBinary == True:
                    float_value = array('f', [value])
                    float_value.tofile(file_model_bin)

            # def writechar(value):
            #     float_value = array('B', [value])
            #     float_value.tofile(file_model_bin)


            # СПИСОК ВЕРШИН
            max_x_co = 0; min_x_co = 0; max_y_co = 0; min_y_co = 0; max_z_co = 0; min_z_co = 0


            obj_verts = level_object.data.vertices ## указали, что смотрм вершины

            for verts in obj_verts:    #сосчитали количество вершин
                a=0
                cur_x = verts.co[0]# + object.location[0] #текущие координаты вершины
                cur_y = verts.co[1]# + object.location[1]
                cur_z = verts.co[2]# + object.location[2]
                if cur_x > max_x_co: max_x_co = cur_x;
                if cur_x < min_x_co: min_x_co = cur_x;
                if cur_y > max_y_co: max_y_co = cur_y;
                if cur_y < min_y_co: min_y_co = cur_y;
                if cur_z > max_z_co: max_z_co = cur_z;
                if cur_z < min_z_co: min_z_co = cur_z;
            #print('Dimensions:\n\tmax_x ' + str(max_x_co) + '\n\tmin_x ' + str(min_x_co) + ' \n\tmax_y ' + str(max_y_co) + '\n\tmin_y ' + str(min_y_co) + '\n\tmax_z ' + str(max_z_co) + '\n\tmin_z ' + str(min_z_co) +'\n')

            if context.scene.bModelsAsText == True:
                file_model.write(str(datetime.datetime.now())+'\n')




            for faces in level_object.data.polygons:    #сосчитали количество полигонов
                b=0

            count_of_verts = verts.index+1
            count_of_faces = faces.index+1



            writeb(count_of_faces)
            writeb(count_of_faces*3)

            if level_object.parent and level_object.parent.type=='ARMATURE': #если объект имеет родителя и родитель - кость:

                if context.scene.bModelsAsText == True:
                    file_model.write('skeleton ' + str(level_object.parent.name) + '\n')

                skeletonName = level_object.parent.name
                while len(skeletonName) < 32:
                    skeletonName += ' '
                if context.scene.bModelsAsBinary == True:
                    file_model_bin.write(skeletonName.encode('utf8'))
            else:
                if context.scene.bModelsAsBinary == True:
                    file_model_bin.write(b"noskeleton                      ")






            #для записи имении скелета выделим 32 символа - 32 байта
            #самыйдлинныйидентификаторскелета.лтх

            if context.scene.bModelsAsText == True:
                file_model.write('faces ' + str(count_of_faces)+'\n')
                file_model.write('vertices ' + str(count_of_faces*3)+'\n')

                file_model.write('\n;vertex array for glDrawArrays:\n; x y z nx ny nz u v material_index and 6 couples boneIndex-weight' + '\n')


            ####writeb(149.0)
            #
            # кусок про ААВВ-коробку
            # ~ MESHES = [mesh.name for mesh in bpy.data.meshes if mesh.name[0:4] == 'UCX_']    # определим все меши, где в названии вначале следует 'UCX_''
            # ~ print(MESHES)

            # ~ AABB_Box = 'UCX_'+str(level_object.data.name)   # сгенерируем предполагаемое имя ААВВ-коробки для заданного меша
            # ~ print('box: %s'%(AABB_Box))

            # ~ if AABB_Box in MESHES:                          # если предполагаемое имя нашлось, то ААВВ-коробка захвачена
                # ~ print('Found Collision box!')
                # ~ BOX = bpy.data.meshes[AABB_Box]
                # ~ print('BOX: ' +str(BOX))

                # ~ AABB_Vertices = 0
                # ~ aabb_verts = BOX.vertices
                # ~ for v in BOX.vertices:
                    # ~ AABB_Vertices += 1

                # ~ AABB_Polygons = 0
                # ~ aabb_polys = BOX.polygons
                # ~ for p in BOX.polygons:
                    # ~ AABB_Polygons += 1

                # ~ print('AABB verts: %i'%(AABB_Vertices))
                # ~ print('AABB polys: %i'%(AABB_Polygons))

                # ~ print('Total mem for AABB: %i'%(AABB_Polygons*3*6))

                # ~ if context.scene.bModelsAsText == True:
                    # ~ #file_model.write('\t\tx y z nx ny nz\n')
                    # ~ file_model.write('AABB %i\n'%(AABB_Polygons*3*6))
                # ~ total = AABB_Polygons*3*6

                # ~ writeb(total)   #запишем, сколько флоатов надо для ААВВ-коробки

                # ~ print('\t\tx y z nx ny nz')
                # ~ for triangle in BOX.polygons:
                    # ~ mynormal = triangle.normal
                    # ~ for vert in triangle.vertices: # перебираем индексы вершин треугольника
                        # ~ print('aabb ' + str(round( aabb_verts[vert].co[0], ROUND_LEVEL)) + ' ' + str(round( aabb_verts[vert].co[1],ROUND_LEVEL)) + ' ' + str(round( aabb_verts[vert].co[2],ROUND_LEVEL)) +' '+str(round( mynormal[0],ROUND_LEVEL)) + ' ' + str(round( mynormal[1],ROUND_LEVEL)) + ' ' + str(round( mynormal[2],ROUND_LEVEL))+ '')
                        # ~ writeb( round(  aabb_verts[vert].co[0], ROUND_LEVEL))
                        # ~ writeb( round(  aabb_verts[vert].co[1], ROUND_LEVEL))
                        # ~ writeb( round(  aabb_verts[vert].co[2], ROUND_LEVEL))
                        # ~ writeb( round( mynormal[0],ROUND_LEVEL))
                        # ~ writeb( round( mynormal[1],ROUND_LEVEL))
                        # ~ writeb( round( mynormal[2],ROUND_LEVEL))

                        # ~ if context.scene.bModelsAsText == True:
                            # ~ file_model.write('aabb ' + str(round( aabb_verts[vert].co[0], ROUND_LEVEL)) + ' ' + str(round( aabb_verts[vert].co[1],ROUND_LEVEL)) + ' ' + str(round( aabb_verts[vert].co[2],ROUND_LEVEL)) +' '+str(round( mynormal[0],ROUND_LEVEL)) + ' ' + str(round( mynormal[1],ROUND_LEVEL)) + ' ' + str(round( mynormal[2],ROUND_LEVEL))+ '\n')
            # ~ else:
                # ~ writeb(0)
            writeb(0)
            # конец куска про ААВВ
            #


            K = 1   #float(context.scene.coefficient)  #коэффициент масштаба экспортируемых вершин и прочего

            V_GROUPS = [group.name for group in level_object.vertex_groups ]

            if level_object.parent and level_object.parent.type == 'ARMATURE':
                BONES = [bone.name for bone in level_object.parent.pose.bones ]

            boneCheckCounter = 0

            print('Almost done')

            #version with bones
            for uv_layer in level_object.data.uv_layers: #перебираем текстурные слои
                tris = 0
                for triangle in level_object.data.polygons:
                    tris=tris+1
                    a=0
                    for vert in triangle.vertices: # перебираем индексы вершин треугольника
                        uvCoord1 = uv_layer.data[triangle.index*3+a].uv
                        a = a+1
                        u1 = round(uvCoord1[0], 4) # % uvCoord1[0]# * scale# -  (math.sqrt(scale))/scale
                        v1 = round(uvCoord1[1], 4) # % uvCoord1[1]# * scale# -  math.sqrt(scale)/scale
                        if u1 < 0.001: #избавимся от машинных нулей
                            u1 = 0
                        if v1 < 0.001:
                            v1 = 0

                        if context.scene.bModelsAsText == True:
                            file_model.write('v ' + str(round( K * obj_verts[vert].co[0], ROUND_LEVEL)) + ' ' + str(round( K * obj_verts[vert].co[1],ROUND_LEVEL)) + ' ' + str(round( K * obj_verts[vert].co[2],ROUND_LEVEL)) +' ')

                        writeb( round( K * obj_verts[vert].co[0], ROUND_LEVEL))
                        writeb( round( K * obj_verts[vert].co[1], ROUND_LEVEL))
                        writeb( round( K * obj_verts[vert].co[2], ROUND_LEVEL))

                        if context.scene.export_normals_from == '1':
                            mynormal = triangle.normal
                        else:
                            mynormal = obj_verts[vert].normal

                        if context.scene.bModelsAsText == True:
                            file_model.write(str(round( mynormal[0],ROUND_LEVEL)) + ' ' + str(round( mynormal[1],ROUND_LEVEL)) + ' ' + str(round( mynormal[2],ROUND_LEVEL))+' ' + str(u1) + ' ' + str(v1) + ' ' + str(triangle.material_index) + ' ')

                        writeb( round( mynormal[0],ROUND_LEVEL))
                        writeb( round( mynormal[1],ROUND_LEVEL))
                        writeb( round( mynormal[2],ROUND_LEVEL))
                        writeb(u1)
                        writeb(v1)
                        writeb(triangle.material_index)


                        if level_object.parent and level_object.parent.type == 'ARMATURE':
                            pointBone = 0
                            for attached_group in obj_verts[vert].groups:      #переберем группы, в которых состоит данная вершина (vert)

                                attached_group_index = attached_group.group    #индекс группы
                                attached_group_weight = attached_group.weight  #вес группы
                                #но записать сразу индекс группы не вариант, ибо групп может быть больше, чем костей. Надо определить индекс именно кости
                                group_name = V_GROUPS[attached_group_index]    #по индексу группы определим имя этой самой группы
                                bone_index = 0
                                #if group_name in BONES:

                                #    if exportAnim.checkInfluence(level_object.parent, level_object.parent.data.bones[BONES.index(group_name)]) == 1:
                                #        bone_index = bone_index+1

                                try:    #если среди КОСТЕЙ есть кость с именем, как у группы group_name, то
                                    bone_index = BONES.index(group_name)           #возьмем индекс конкретно этой кости, без учета других групп
                                #group_index = 0
                                    #if context.scene.bModelsAsText == True:
                                        #file_model.write('\t ' + str(group_name)  +', weight:' + str(round(attached_group_weight,4)) +' ' )   #for debug
                                    #if context.scene.bModelsAsText == True:
                                        #file_model.write(' ' + str(bone_index) + '('+str(group_name)+') '+ str(round(attached_group_weight,4)) +'  ' ) #for debug

                                    if context.scene.bModelsAsText == True:
                                        file_model.write('' + str(bone_index) + ' ' + str(round(attached_group_weight,4)) +' ' )

                                    writeb(bone_index)
                                    writeb(round(attached_group_weight,4))
                                    pointBone = pointBone + 1
                                except:
                                    c=0 #заглушка
                                #pointBone = pointBone + 1
                            #if context.scene.bModelsAsText == True:
                                #file_model.write(' _'+str(pointBone)+'_ ')    # определили сколько костей назначено данной точке
                                #file_model.write('\t\t')
                            #if pointBone == 6:
                                #if context.scene.bModelsAsText == True:
                                    #file_model.write(' target ')
                                if pointBone > 6:
                                    boneCheckCounter = boneCheckCounter+1

                            while pointBone < 7:
                                if context.scene.bModelsAsText == True:
                                    file_model.write(' 0 0')
                                writeb(0)
                                writeb(0)
                                pointBone = pointBone + 1

                        #######################################################################
                        if context.scene.bModelsAsText == True:
                            file_model.write('\n')



            if context.scene.bModelsAsText == True:
                file_model.close()
                #EXPORTED_ASSETS.append(name_mesh+'.ltx')

            if context.scene.bModelsAsBinary == True:
                file_model_bin.close()
                #EXPORTED_ASSETS.append(name_mesh+'.model')

            #EXPORTED_ASSETS.append(name_mesh)

            #logFile.write(str(EXPORTED_ASSETS)+'\n')
            #logFile.close()


            #print('slkgndsldsnnsdlngds')
            #bpy.ops.console.scrollback_append(text='ggk4', type='OUTPUT')
            #log = 'Verts over 7 bones: ' + str(boneCheckCounter)
            #print('dfdffd')

            #console = bpy.context.window_manager.console_output
            #console.write("slkgndsldsnnsdlngds")

            #exportMeshClass.ShowMessageBox(log, 'Mesh log:', 'BLENDER')
            print('OK!')

        return meshPath
    ## FUNC END #########################################################

    
    
class exportMaterialClass(bpy.types.Operator):
    bl_idname = 'material.export_material' #запуск командой mesh.output_list_of_objects
    bl_label = 'Export material to file'
    bl_description = "print objects`s materials to file"


    LINKS = [] #массив для хранения слинкованных карт для данного материала
    anyNodeLinked = 'FALSE'
    
    EXPORTED_TEXTURES = [] # массив для хранения экспортированных текстур. Чтобы повторно не записывать в папку уже сохраненные текстуры

    xSize = 1024
    xScale = 1.0

    # ~ def resize_texture(src_path, dst_path, target_size=(2048, 2048)):
        # ~ if not os.path.exists(src_path):
            # ~ return False
        # ~ with Image.open(src_path) as img:
            # ~ # Для PBR лучше использовать Lanczos (хорошее качество)
            # ~ img_resized = img.resize(target_size, Image.LANCZOS)
            # ~ # Сохраняем как PNG или JPG в зависимости от типа текстуры
            # ~ fmt = "PNG" if img.mode == "RGBA" else "JPEG"
            # ~ img_resized.save(dst_path, format=fmt)
        # ~ return True


    def processMapping(materialsourcefile, linkedNode): #функция достает значение масштабирования текстуры через mappin node
        scaleInput = linkedNode.inputs['Scale']
        if scaleInput.is_linked:
            # тут обычно находится нода Value
            valueNode = scaleInput.links[0].from_node
            if valueNode.type == 'VALUE':
                materialsourcefile.write('scale ' + str(valueNode.outputs['Value'].default_value) +'\n')
                exportMaterialClass.xScale = valueNode.outputs['Value'].default_value
            else:
                materialsourcefile.write('scale ' + str(scaleInput.default_value[0]) +' (wrong mapping scale input value node type, print default mapping scale)\n')
                exportMaterialClass.xScale = scaleInput.default_value[0]
        else:
            materialsourcefile.write('scale ' + str(scaleInput.default_value[0]) +' (mapping scale input not linked, print default value)\n')
            exportMaterialClass.xScale = scaleInput.default_value[0]


    #############################################################################################################################
    # Эскортировать данные о слинкованной текстуре: параметры сэмплинга, сам файл текстуры и т.д.             
    def printLinkedImageTextureData(materialsourcefile, img, self, context, nodeType ):
        if img.image and img.image.name:
            imageName = img.image.name
        else:
            print('\t\t\t\t\t\tNode [' + str(nodeType) + '] has no attached image at all!')
            return False
        
        # 1) экспортируем сам файл (при возможности)
        if context.scene.bTextures == True and imageName not in exportMaterialClass.EXPORTED_TEXTURES:
            slash = '/' if context.scene.operationSystem == "0" else '\\'
            texturesPath    = context.scene.projectFolder + slash + 'textures' + slash
            filename = texturesPath + slash + imageName

            if img.image:
                if img.image.size[0] > 0 and img.image.size[1] > 0:
                    #print('Texture is loaded and has valid size')
                    # ~ img.image.save_render(filename)
                    
                    ## scale image
                    orig = img.image
                    target_w, target_h = 256, 256
                    # Создаём новый блок данных изображения (пустой, нужного размера)
                    dup = img.image.copy() #bpy.data.images.new(name="temp_resized", width=target_w, height=target_h)#, alpha=orig.use_alpha)
                    
                    dup.scale(target_w, target_h)  # ресемплинг внутри Blender
                    # Копируем пиксели из оригинала в новый (в Blender пиксели — это плоский массив RGBA)
                    # Важно: у dup.pixels сначала нужно задать длину (при создании она уже правильная)
                    #dup.pixels = orig.pixels[:]  # копируем все пиксели

                    # Теперь масштабируем уже дубликат (ресемплинг)
                    #dup.scale(target_w, target_h)

                    # Сохраняем именно дубликат
                    dup.save_render(filename)

                    # Удаляем временный дубликат из памяти Blender
                    bpy.data.images.remove(dup)
                    ##
                    
                    exportMaterialClass.EXPORTED_TEXTURES.append(imageName)
                    
                else:
                    print('\t\t\t\t\t\tNode [' + str(nodeType) + '] is referencing an empty no-data image [' + str(img.image.name) +'')
                    return False
            else:
                print('\t\t\t\t\t\tNode [' + str(nodeType) + '] has no attached image at all!')
                return False
        
        # если текстура существует и была успешно экспортирована, то:
        # 2) выпишем текстовое описание сэмплинга
        

        if imageName[len(imageName)-4] == '.' and imageName[len(imageName)-3] == '0':   #обрезаем точку и номер
            imageName = imageName[0:len(imageName)-4]
        name_texture = imageName

        materialsourcefile.write('\n\nmap\n' + str(nodeType) + ' ' + str(name_texture) +'\n')
        materialsourcefile.write('size '+str(img.image.size[0])+' '+str(img.image.size[1])+'\n') ## бесполезно и ненужно
        # scale
        try:
            vectorInput = img.inputs['Vector']
            if vectorInput.is_linked: #если vector залинкована
                linkedNode = vectorInput.links[0].from_node
                if linkedNode.type == 'MAPPING':
                    exportMaterialClass.processMapping(materialsourcefile, linkedNode)

                if linkedNode.type == 'REROUTE':
                #materialsourcefile.write('reroute knot linked\n')
                    routeNode = linkedNode.inputs[0].links[0].from_node
                    if routeNode.type == 'MAPPING':
                        exportMaterialClass.processMapping(materialsourcefile, routeNode)
            else:
               materialsourcefile.write('scale 1.0 (No mapping linked: image node vector input is empty, set default scale)\n')
        except:
            materialsourcefile.write('scale 1.0 (ERROR)\n')
        # end scale
        materialsourcefile.write('interpolation ' +str(img.interpolation) +' ' +'\n')
        materialsourcefile.write('extension ' +str(img.extension) +' ' +'\n')
        materialsourcefile.write('END\n')
        return True
        

            
            
		    #EXPORTED_ASSETS.append(imageName)
		    #materialsourcefile.write('etegegegeg\n')

	#materialsourcefile.write('\n\n '+str(bpy.types.Scene.texture_path)+'\n\n')
	#materialsourcefile.write('\n\n '+str(bpy.context.scene.AnimatorProps.texture_path)+'\n\n')

	# речь идет о нодах изображения, так что:
	
		
        # ~ return
    #############################################################################################################################
  

        
 
#############################################################################################################################
# Экспортировать данные с одного из входов ноды PrincipledBSDF - Base Color, Normal etc:
# попытаться экспортировать текстуру и описание ее сэмплинга 
# либо (в т.ч. если некорректная текстура вернула False) выписать данные (о цвете и т.д.) по-умолчанию из ноды PrincipledBSDF
    def printBSDFInputData(materialsourcefile, input1, self, context):    
        nodeType = 'none'
        
        if input1.name == 'Base Color':
            nodeType = 'BaseColor'
        if input1.name == 'Emission Color':
            nodeType = 'Lightmap'
        if input1.name == 'Normal':
            nodeType = 'Normal'
        if input1.name == 'Height':
            nodeType = 'Displacement'
        if input1.name == 'Metallic':
            nodeType = 'Metallic'
        if input1.name == 'Roughness':
            nodeType = 'Roughness'
        if input1.name == 'Emission Color':
            nodeType = 'Emission'
        if input1.name == 'Alpha':
            nodeType = 'Alpha'
            
        inputExportedSuccessfully = False
               
        # если что-то слинковано...
        if input1.is_linked:
            print('\t\t\t\t\tInfo of linked input: ' + str(nodeType) + '')  
            
            node = input1.links[0].from_node
            
            # node.type - тип ноды: TEX_IMAGE, NORMAL_MAP etc
            
            # 1) текстура может быть назначена сразу через Image Texture
            if node.type == "TEX_IMAGE":
                inputExportedSuccessfully = exportMaterialClass.printLinkedImageTextureData( materialsourcefile, node, self, context, nodeType )
            
            # 2) еще текстура может быть назначена через миксер с лайтмапой
            if node.type == "MIX_RGB":
                # node.inputs[0].name -> factor
                # node.inputs[1].name -> color 1 (как правило, lightmap)
                # node.inputs[2].name -> color 2 (как правило, текстура цвета)
    
                #если нода "color1" - lightmap залинкована
                if node.inputs[1].is_linked:
                    color1_node = node.inputs[1].links[0].from_node #image
                    color1_node_imageName = color1_node.image.name  #взять название и проверить, есть ли там в конце "_baked"?
                    #materialsourcefile.write(str(color1_node_imageName)+'\n')
    
                    #materialsourcefile.write(str(color1_node_imageName[ len(color1_node_imageName)-6 : len(color1_node_imageName) ]) +'\n')
    
                    if color1_node_imageName[ len(color1_node_imageName)-6 : len(color1_node_imageName) ] == '_baked':
                        #materialsourcefile.write('BAKED!!!!' + '\n' )
    
                        if color1_node.type == "TEX_IMAGE":
                            inputExportedSuccessfully = exportMaterialClass.printLinkedImageTextureData( materialsourcefile, color1_node, self, context, nodeType )
    
                #если нода "color2" - diffuse залинкована
                if node.inputs[2].is_linked:
                    color2_node = node.inputs[2].links[0].from_node #image
                    if color2_node.type == "TEX_IMAGE":
                        inputExportedSuccessfully = exportMaterialClass.printLinkedImageTextureData( materialsourcefile, color2_node, self, context, nodeType )      
            
            # 3) или вообще как normal map
            if node.type == "NORMAL_MAP": # node.inputs[0].name - Strength input, node.inputs[1].name - Color input
                if node.inputs[1].is_linked: #если нода цвета залинкована
                    normalmapImage = node.inputs[1].links[0].from_node
                    if normalmapImage.type == "TEX_IMAGE":
                        inputExportedSuccessfully = exportMaterialClass.printLinkedImageTextureData( materialsourcefile, normalmapImage, self, context, nodeType )
        
        # а если ничего не слинковано либо текстуру не удалось экспортировать, то inputExportedSuccessfully останется False 
        # и тогда выпишем значения по-умолчанию
        if inputExportedSuccessfully == False:
            # если вход - эмиссия или цвет (т.е. вектор), то запишем значения по-умолчанию
            if nodeType == 'Emission' or nodeType == 'BaseColor':
                materialsourcefile.write('\n\nvalue\n' + str(nodeType) + ' ' + str(round(input1.default_value[0], ROUND_LEVEL)) + ' ' + str(round(input1.default_value[1], ROUND_LEVEL)) + ' ' + str(round(input1.default_value[2], ROUND_LEVEL)) +'\nEND\n' )
			# а у остальных параметров значение состоит из 1 числа
            if nodeType == 'Metallic' or nodeType == 'Roughness':
                materialsourcefile.write('\n\nvalue\n' + str(nodeType) + ' ' + str(round(input1.default_value, ROUND_LEVEL)) + '\nEND\n' )
#############################################################################################################################  
            


    # ~ def setDefaultMaterial(materialsourcefile):
        # ~ materialsourcefile.write('\n;\tBaseColor is not setted, so link a default texture\n')
        # ~ if exportMaterialClass.xSize == 1024:
            # ~ materialsourcefile.write('\nmap\nBaseColor default_1k.png\n')
            # ~ materialsourcefile.write('size 1024 1024\n')
        # ~ if exportMaterialClass.xSize == 2048:
            # ~ materialsourcefile.write('map\nBaseColor default_2k.png\n')
            # ~ materialsourcefile.write('size 2048 2048\n')
#############################################################################################################################
       


    def exportMaterial(OBJECT, self, context):
		
        exportMaterialClass.EXPORTED_TEXTURES.clear() # в начале экспорта - очистка списка экспортированных текстур
		
        for material in OBJECT.data.materials:
            print('\t\t\t\tNow process material ['+str(material.name)+']')
            materialName = material.name #обрежем

            if materialName not in ALREADY_EXPORTED_RESOURCES:
                ALREADY_EXPORTED_RESOURCES.append(materialName)
                
                slash = '/' if context.scene.operationSystem == "0" else '\\'
                materialPath    = context.scene.projectFolder + slash + 'materials' + slash

                materialsourcefile = open(materialPath + slash + materialName+'.ltx', 'w')
                # ~ base_path = Path(context.scene.projectFolder)
                # ~ material_dir = base_path / 'materials'

                # ~ # Создаёт всю цепочку папок, если нет
                # ~ material_dir.mkdir(parents=True, exist_ok=True)

                # ~ file_path = material_dir / (materialName + '.ltx')

                # ~ with file_path.open('w', encoding='utf-8') as materialsourcefile:
                    # ~ materialsourcefile.write('ваши данные')
                materialsourcefile.write(';'+str(datetime.datetime.now()) + '\nmaterial '+str(materialName) +'\n')
                #########################################################

                # ~ exportMaterialClass.LINKS.clear()# = [] #массив для хранения слинкованных карт для данного материала
                # ~ exportMaterialClass.anyNodeLinked = 'FALSE'
                # ~ exportMaterialClass.xSize = 1024
                # ~ exportMaterialClass.xScale = 1.0

                for node in ( allNodes for allNodes in material.node_tree.nodes if allNodes.name == 'Principled BSDF'):
                    for input1 in node.inputs: # пройтись по всем входам ноды BSDF: Base Color, Normal, Emission etc
                        exportMaterialClass.printBSDFInputData(materialsourcefile, input1, self, context)
                
                # выпишем инфу о ноде смещения
                for node in ( allNodes for allNodes in material.node_tree.nodes if allNodes.name == 'Displacement'):
                    for input1 in (input0 for input0 in node.inputs if input0.is_linked):
                        if input1.name == 'Height':
                            exportMaterialClass.printBSDFInputData(materialsourcefile, input1, self, context)

                # ~ if exportMaterialClass.anyNodeLinked == 'FALSE':
                    # ~ exportMaterialClass.setDefaultMaterial(materialsourcefile)

                #materialsourcefile.write(str(exportMaterialClass.LINKS) + '\n')
                #EXPORTED_ASSETS.append(materialName)

                materialsourcefile.close()
    ## FUNC END #########################################################


    def createTextureNode(objMaterialName):
        bsdf = bpy.data.materials[objMaterialName].node_tree.nodes['Principled BSDF']
        texImage    = bpy.data.materials[objMaterialName].node_tree.nodes.new('ShaderNodeTexImage')     # создадим новую ноду изображения
        texImage.location.x = bsdf.location.x-350
        texImage.location.y = bsdf.location.y+10

        textureName = 'T_Default_1k.png'  # имя стандартной текстуры для любого объекта
        if textureName in (image.name for image in bpy.data.images):            # если такая картинка существует
            texImage.image = bpy.data.images[textureName]
        else:                                                                   # если такой картинки нет, то создадим
            bpy.ops.image.new(name=textureName, width=1024, height=1024, color=(1.0, 0.0, 0.0, 1.0), alpha=True, generated_type='UV_GRID', float=False, use_stereo_3d=False, tiled=False)
            image = bpy.data.images[textureName]
            image.file_format = "PNG"
            texImage.image = image
        # теперь слинкуем изображение с BSDF
        bpy.data.materials[objMaterialName].node_tree.links.new(bsdf.inputs['Base Color'],  texImage.outputs['Color'])


    def configureMaterial(OBJECT, tabs): #-- функция назначает материал если оный не назначен
        slotID = 0
        print( str(tabs)+'\tConfigure materials..')
        for slot in (mat for mat in OBJECT.data.materials if OBJECT.data.materials):
            if slot == None:                                                        # если слот материала пуст
                print( str(tabs) + '\tSlot is empty, try to attach new material')
                objMaterialName = 'M_'+OBJECT.data.name                             # сгенерировали имя материала
                if objMaterialName not in (mat.name for mat in bpy.data.materials): # если такого материала нет в проекте, создадим
                    new_mat = bpy.data.materials.new(objMaterialName)
                    new_mat.use_nodes = True
                slotMaterial = bpy.data.materials[objMaterialName]                  # запомним созданный материал
            else:
                print( str(tabs) + '\tSlot [' + str(slotID) + '] attached material: [' + str(slot.name)+']')
                slotMaterial = slot

            #-- настройка нового или отладка существующего материала slotMaterial
            bsdf = slotMaterial.node_tree.nodes['Principled BSDF']

            baseColor = slotMaterial.node_tree.nodes['Principled BSDF'].inputs['Base Color']

            # ~ if baseColor.is_linked and baseColor.links[0].from_node.type == 'TEX_IMAGE' and baseColor.links[0].from_node.image:
                # ~ aaa=5 #заглушка
                # ~ print( str(tabs)+'\tColor image attached, all right')
            # ~ else:
                # ~ print( str(tabs)+'\tNo color attached, create new node and attach texture')

                # ~ textureName = 'T_Default_1k.png'  # имя стандартной текстуры для любого объекта
                # ~ if textureName not in (image.name for image in bpy.data.images):  # если такая картинка не существует в проекте, создадим
                    # ~ bpy.ops.image.new(name=textureName, width=1024, height=1024, color=(1.0, 0.0, 0.0, 1.0), alpha=True, generated_type='UV_GRID', float=False, use_stereo_3d=False, tiled=False)
                    # ~ bpy.data.images[textureName].file_format = "PNG"

                # ~ texImage    = slotMaterial.node_tree.nodes.new('ShaderNodeTexImage')     # создадим новую ноду изображения
                # ~ texImage.location.x = bsdf.location.x-350
                # ~ texImage.location.y = bsdf.location.y+10
                # ~ texImage.image = bpy.data.images[textureName]           # назначим картинку
                # ~ slotMaterial.node_tree.links.new(bsdf.inputs['Base Color'],  texImage.outputs['Color']) # теперь слинкуем изображение с BSDF

            OBJECT.data.materials[slotID] = slotMaterial
            slotID = slotID + 1
        print( str(tabs)+'\tMaterials configured!\n')




# button for one export
class ExportObject(bpy.types.Operator):
    bl_idname = 'object.export_object' #запуск командой mesh.output_list_of_objects
    bl_label = 'Export data of 1 object.'
    bl_description = "Export marked resources of selected object."
    
    def CmulCXYZW(a, b):    #функция для перемножения комплексных чисел, например - кватернионов (в формате w i j k)
        c = [0,0,0,1] #XYZW
        c[0] = a[3]*b[0] + b[3]*a[0] + a[1]*b[2] - b[1]*a[2] #X
        c[1] = a[3]*b[1] + b[3]*a[1] + a[2]*b[0] - b[2]*a[0] #Y
        c[2] = a[3]*b[2] + b[3]*a[2] + a[0]*b[1] - b[0]*a[1] #Z
        c[3] = a[3]*b[3] - a[0]*b[0] - a[1]*b[1] - a[2]*b[2] #W
        return c

    def RotByQuatXYZW( coordinate,  quat):    #функция возвращает координаты вектора, измененные после применения кватерниона
        a = ExportObject.CmulCXYZW(quat, coordinate)
        qinv = [-quat[0], -quat[1], -quat[2], quat[3]]
        b = ExportObject.CmulCXYZW(a, qinv)
        return b
    
    def printObjectLocationRotation(Object):
        loc = Object.location
        quat = Object.rotation_quaternion
        print('\n['+str(Object.name)+'] coordinates:')
        print('\tposition ' + str(round(loc[0], ROUND_LEVEL)) + ' ' + str(round(loc[1], ROUND_LEVEL)) + ' ' + str(round(loc[2], ROUND_LEVEL)) + '' ) #position
        print('\tdirection ' + str(round(quat.w, ROUND_LEVEL)) +  ' ' + str(round(quat.x, ROUND_LEVEL)) + ' ' +  str(round(quat.y,ROUND_LEVEL)) + ' ' + str(round(quat.z, ROUND_LEVEL)) +   '\n') #direction

    def printAllObjects():
        print('\n------------------------\nbpy.data.objects:')
        for obj in bpy.data.objects:
            print(f"\t{obj.type:<10} {obj.name:<30} library: {str(obj.library):<50}")
        print('------------------------\n')

    def printAllMeshes():
        print('\n------------------------\nbpy.data.meshes:')
        for obj in bpy.data.meshes:
            print(f"\t{obj.name:<40} library: {str(obj.library):<50}")
        print('------------------------\n')
    
    
    def checkMaterialAlphaEmission(fileToWrite, materialName):
        material = bpy.data.materials[ materialName ]
        for node in ( allNodes for allNodes in material.node_tree.nodes if allNodes.name == 'Principled BSDF'):
            for input1 in node.inputs:	#(input0 for input0 in node.inputs if input0.is_linked):
                #надо проверить, был ли назначен base color и если нет, вписать дефолтную текстуру шахматной доски

                if input1.name == 'Alpha':
                    if input1.is_linked or input1.default_value < 1:
                        fileToWrite.write('type 1' + ' transparent\n') # str(input1.default_value) 
                if input1.name == 'Emission Strength':
                    if input1.default_value > 0.01:
                        fileToWrite.write('type 2' + ' emission\n')
    
    ## export object as a text block for runtime-loading (as level.ltx) #######################################################
    def printObjectRuntimeLike(fileToWrite, loc, quat, OBJECT, self, context):
        # ~ print('\nexport object as a text block for runtime-loading (as level.ltx)\n')
        
        fileToWrite.write('\n[' + str(0) + '] '+  str('MESH') +'\n')                #начало блока
        fileToWrite.write('sysname ' + str(OBJECT.name) + '\n')
        fileToWrite.write('position ' + str(round(loc[0], ROUND_LEVEL)) + ' ' + str(round(loc[1], ROUND_LEVEL)) + ' ' + str(round(loc[2], ROUND_LEVEL)) + '\n' ) #position
        fileToWrite.write('direction ' + str(round(quat.w, ROUND_LEVEL)) +  ' ' + str(round(quat.x, ROUND_LEVEL)) + ' ' +  str(round(quat.y,ROUND_LEVEL)) + ' ' + str(round(quat.z, ROUND_LEVEL)) +   '\n') #direction

        fileToWrite.write('scale ' + str(round(OBJECT.scale.x, ROUND_LEVEL)) + ' ' +  str(round(OBJECT.scale.y,ROUND_LEVEL)) + ' ' + str(round(OBJECT.scale.z, ROUND_LEVEL)) +   '\n') #direction


        name = OBJECT.data.name
        if name[len(name)-4] == '.' :   #обрезаем точку и номер
            name = name[0:len(name)-4]
            
        ####if name[len(name)-2] == '_' :   #обрезаем _temp
        ####    name = name[0:len(name)-2]

        fileToWrite.write('model '+str(name)+'\n') #путь к модели

        for material in OBJECT.data.materials:
            if material != None:
                # -- здесь возможно надо будет обрезать точки
                fileToWrite.write('material '+ str(material.name)+'\n')
                ExportObject.checkMaterialAlphaEmission(fileToWrite, material.name)
            else:
                fileToWrite.write('material default_1k\n')

        #fileToWrite.write('type 0\n')
        fileToWrite.write('END\n')
        runtimeCounter = runtimeCounter+1
    ## FUNC END #########################################################

    ## export object as a line of C++ code #######################################################
    def printObjectCodeLikeInString(fileToWrite, location, rotation_quaternion, OBJECT, self, context):
        #print('\nexport object as a line of C++ code\n')

        # example:
        # addEntity( "Slide", glm::vec3(0,0,0), glm::quat(1,0,0,0),  "Slide", emptyCollision, "MESH", { "M_Val_01", },  "none",  "forward" );
        
        fileToWrite.write('\t\taddEntity( "'+str(OBJECT.name)+ '", glm::vec3(' + str(round(location[0],4)) + ', ' + str(round(location[1],4)) + ', ' + str(round(location[2],4)) + '),'  )
        fileToWrite.write(' glm::quat(' + str(round(rotation_quaternion.w,4)) + ', ' + str(round(rotation_quaternion.x,4)) + ', ' + str(round(rotation_quaternion.y,4)) + ', ' + str(round(rotation_quaternion.z,4)) + '), ' )
        
        name = OBJECT.data.name
        if name[len(name)-4] == '.' :   #обрезаем точку и номер
            name = name[0:len(name)-4]
        ####if name[len(name)-2] == '_' :   #обрезаем точку и номер
        ####    name = name[0:len(name)-2]

        fileToWrite.write( ' "' + str(name) + '", { /*entity collision*/ }, "' + str(OBJECT.type) + '", {' )  #-- выписали имя модели и тип ообъекта

        for material in OBJECT.data.materials:
            if material != None:
                # -- здесь возможно надо будет обрезать точки
                fileToWrite.write(' "'+str(material.name)+'", ')
            else:
                fileToWrite.write(' "default_1k", ')
        fileToWrite.write('}, ')    #-- закончили выписку материалов

        try:
            if bpy.context.bEnableLightmaps == True and "Lightmap" in OBJECT:
                fileToWrite.write(' "' + str(OBJECT["Lightmap"].name) + '", '  )
        except:
            fileToWrite.write(' "none", '  )

        fileToWrite.write(' "forward" );\n')
    ## FUNC END #########################################################

    ## FUNC START #######################################################
    def printObjectCodeLikeInStruct(fileToWrite, location, rotation_quaternion, OBJECT, self, context):
        #print('\nexport object as a block of C++ code with struct-description\n')
   
        # example:
        # ~ entityInitializationParameters SM_AKSU_01_Mag;
        # ~ SM_AKSU_01_Mag.initSysname = "SM_AKSU_01_Mag";
            # ~ SM_AKSU_01_Mag.initPos = glm::vec3(0.1454, 0.0022, -0.095);
            # ~ SM_AKSU_01_Mag.initRot = glm::quat(1.0, 0.0, 0.0, 0.0);
            # ~ SM_AKSU_01_Mag.initMeshName = "SM_AKSU_01_Mag";	//dont forget initCollisionType
            # ~ SM_AKSU_01_Mag.initMeshMaterialsVector = { "M_AKSU_01_Mag", }; 
        # ~ addEntity( std::move(SM_AKSU_01_Mag) );
        
        #корректура имени сущности
        #OBJECT.name.find("") == -1:
        varName = OBJECT.name.replace(".", "_")
        
        name = OBJECT.data.name
        if name[len(name)-4] == '.' :   #обрезаем точку и номер
            name = name[0:len(name)-4]
        ####if name[len(name)-2] == '_' :   #обрезаем точку и номер
        ####    name = name[0:len(name)-2]

        fileToWrite.write('\n\tFhEntityInitializationInfo ' + str(varName) + ';\n')
        fileToWrite.write('\t\t' + str(varName) + '.initSysname = "' + str(OBJECT.name) + '";\n')
        fileToWrite.write('\t\t' + str(varName) + '.initPos = glm::vec3(' + str(round(location[0],4)) + ', ' + str(round(location[1],4)) + ', ' + str(round(location[2],4)) + ');\n')
        fileToWrite.write('\t\t' + str(varName) + '.initRot = glm::quat(' + str(round(rotation_quaternion.w,4)) + ', ' + str(round(rotation_quaternion.x,4)) + ', ' + str(round(rotation_quaternion.y,4)) + ', ' + str(round(rotation_quaternion.z,4)) + ');\n')
        fileToWrite.write('\t\t' + str(varName) + '.initScale = glm::vec3(' + str(round(OBJECT.scale.x, 4)) + ', ' + str(round(OBJECT.scale.y, 4)) + ', ' + str(round(OBJECT.scale.z, 4)) + ');\n')
        fileToWrite.write('\t\t' + str(varName) + '.initMeshName = "' + str(name) + '.model";	//dont forget initCollisionType\n')
        fileToWrite.write('\t\t//' + str(varName) + '.initCollisionType = emptyCollision;\n')
        
        fileToWrite.write('\t\t' + str(varName) + '.initMeshMaterialsVector = {')
        for material in OBJECT.data.materials:
            if material != None:
                # -- здесь возмодно надо будет обрезать точки
                fileToWrite.write(' "' + str(material.name) + '", ')
            else:
                fileToWrite.write(' "default_1k", ')
        fileToWrite.write('}; ')    #-- закончили выписку материалов

        #try:
        #    if bpy.context.bEnableLightmaps == True and "Lightmap" in OBJECT:
        #        fileToWrite.write(' "' + str(OBJECT["Lightmap"].name) + '", '  )
        #except:
        #    fileToWrite.write(' "none", '  )
        
        #fileToWrite.write('\n\taddEntity( std::move(' + str(varName) + ') );\n')
        fileToWrite.write('\n\taddEntity( ' + str(varName) + ' );\n')
    ## FUNC END #########################################################

    
    def exportObjectDescription(OBJECT, PARENT, self, context):
        if OBJECT.type == 'MESH':                           # если обрабатываемый объект коллекции - меш, то уточним для него кватернион с локацией и виден ли он вообще?
            existFlag = 0
            quaternion = OBJECT.rotation_quaternion
            location = OBJECT.location

            print('Name: ' + str(OBJECT.name))
            ExportObject.printObjectLocationRotation(OBJECT)

            # родитель либо связан в блендере либо это объект слинкованной коллекции. Приоритет у блендеровского родителя
            parent = OBJECT.parent if OBJECT.parent else (PARENT if PARENT else None)


            if parent: #OBJECT.parent:
                print('Has parent: ' + str(parent))
                ExportObject.printObjectLocationRotation(parent)
                
                if parent.hide_get() == False:
                    existFlag = 1
                    #print('\n\nAAAAAAAA\n\n')


                    if parent.type == 'ARMATURE':      # если родитель - арматура, то кватернион берем от НЕЕ
                        quaternion = parent.rotation_quaternion
                        location = parent.location

                    if parent.type == 'MESH' or parent.type == 'COLLECTION' or parent.type == 'EMPTY':          # а если родитель - меш или коллекция, то надо учесть его доворот!
                        #print('\n\nBFKJDBFKSK\n\n')
                        parent_quat = parent.rotation_quaternion
                        child_quat = OBJECT.rotation_quaternion
                        coord = [OBJECT.location.x, OBJECT.location.y, OBJECT.location.z, 1]    # представляем в виде массива
                        quat = [parent_quat.x, parent_quat.y, parent_quat.z, parent_quat.w]     # представляем в виде массива

                        location = ExportObject.RotByQuatXYZW(coord, quat)

                        location[0] += parent.location[0]    # добавляем смещение родителя
                        location[1] += parent.location[1]
                        location[2] += parent.location[2]

                        quaternion = parent_quat @ child_quat
            else:
                if OBJECT.hide_get() == False:  #если нет родительской арматуры и объект не скрыт
                    existFlag = 1

            # ~ if PARENT not None

            print('\tResult position ' + str(round(location[0], ROUND_LEVEL)) + ' ' + str(round(location[1], ROUND_LEVEL)) + ' ' + str(round(location[2], ROUND_LEVEL)) + '' ) #position


            if existFlag == 1:  #если объект видим, то выпишем его параметры согласно выбранному типу экспорта
                if context.scene.bExportLevel:                                      # если необходимо обновить файл описания уровня
                    try:
                        LevelDescription = open(context.scene.collectionFolder, 'a')
                        

                        if OBJECT.name.find("UCX") == -1: # экспортируем меш, только если это не ААВВ-коробка (т.е. UCX не найдено в названии)

                            if context.scene.setType == "0": # выпишем в файл описания уровня его параметры runtime-like
                                ExportObject.printObjectRuntimeLike( LevelDescription, location, quaternion, OBJECT, self, context )

                            if context.scene.setType == "1": # выпишем в файл описания уровня его параметры code-like 1 - через структуру
                                ExportObject.printObjectCodeLikeInStruct(LevelDescription, location, quaternion, OBJECT, self, context)
                                
                            if context.scene.setType == "2": # выпишем в файл описания уровня его параметры code-like 2 - в одну строку
                                ExportObject.printObjectCodeLikeInString(LevelDescription, location, quaternion, OBJECT, self, context)

                        LevelDescription.close()
                    except:
                        a=7#EXPORTED_ASSETS.append('Cannot create file for collection description')
    ## FUNC END #########################################################
        
    
    # AI
    def apply_modifiers_to_duplicate(obj, parent):
        # 1. Создаем дубликат объекта (не связанный с оригиналом)
        obj_copy = obj.copy()
        obj_copy.data = obj.data.copy()
        bpy.context.collection.objects.link(obj_copy)
    
        # 2. Делаем дубликат активным и выделенным
        bpy.context.view_layer.objects.active = obj_copy
        bpy.ops.object.select_all(action='DESELECT')
        obj_copy.select_set(True)
    
        # ~ # учтем координаты родительской коллекции
        quaternion = obj.rotation_quaternion
        location = obj.location
        
        # родитель либо связан в блендере либо это объект слинкованной коллекции. Приоритет у блендеровского родителя
        parent = parent if parent else None
        
        if parent: #OBJECT.parent:               
            if parent.hide_get() == False:
                existFlag = 1

                # ~ if parent.type == 'ARMATURE':      # если родитель - арматура, то кватернион берем от НЕЕ
                    # ~ quaternion = parent.rotation_quaternion
                    # ~ location = parent.location

                if parent.type == 'MESH' or parent.type == 'COLLECTION' or parent.type == 'EMPTY':          # а если родитель - меш или коллекция, то надо учесть его доворот!
                    #print('\n\nBFKJDBFKSK\n\n')
                    parent_quat = parent.rotation_quaternion
                    child_quat = obj.rotation_quaternion
                    coord = [obj.location.x, obj.location.y, obj.location.z, 1]    # представляем в виде массива
                    quat = [parent_quat.x, parent_quat.y, parent_quat.z, parent_quat.w]     # представляем в виде массива

                    location = ExportObject.RotByQuatXYZW(coord, quat)

                    location[0] += parent.location[0]    # добавляем смещение родителя
                    location[1] += parent.location[1]
                    location[2] += parent.location[2]

                    quaternion = parent_quat @ child_quat
        
        # ~ if not parent == None:
            # ~ obj_copy.location = parent.location + obj.location
            # ~ obj_copy.rotation_quaternion = parent.rotation_quaternion @ obj.rotation_quaternion
        # ~ else:
            # ~ obj_copy.location = obj.location
            # ~ obj_copy.rotation_quaternion = obj.rotation_quaternion
            
        # ~ if parent:# == None:
            # ~ obj_copy.location = parent.location
        # ~ else:
            # ~ obj_copy.location = obj.location
                
        # 3. Применяем все модификаторы
        for modifier in obj_copy.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except:
                pass
        return obj_copy
    
    
    def exportOneObjectData(Object, Parent, self, context, tabs):
        print( ''+str(tabs) + '\t\tExport object [' + str(Object.name) + '] start: ')

        # 2.1 configure and export object materials
        exportMaterialClass.configureMaterial(Object, tabs)
        if context.scene.bMaterials == True:                                            # по галочке
            print(str(tabs)+'\t\t\tMaterials...')
            exportMaterialClass.exportMaterial(Object, self, context)                   # материалы для этого объекта

        # 2.2 export object description
        if context.scene.bExportLevel:                                                  # по галочке запишем в файл
            print(str(tabs)+'\t\t\tDescription...')
            ExportObject.exportObjectDescription(Object, Parent, self, context)

        # 2.3 export object model after aplying (or not) modificators
        if context.scene.bModelsAsText == True or context.scene.bModelsAsBinary == True:
            print(str(tabs)+'\t\t\tMesh...')
            exportMeshClass.export_model(self, context, Object)                         # по галочке
    
    
    def exportOneObject(head, tail, OBJECT, self, context, tabs): # рассмотрим объект коллекции из уровня
        print( '\n'+str(tabs)+'___________________________________\n' + str(tabs) + '|Exporting one object ['+str(OBJECT.name)+']')
        
        # получили шапку, хвост и надо экспортировать все наши объекты
        # принятый OBJECT может быть местной моделькой (с модификаторами или без) или привязанным ассетом
       
        ###EXPORTING = []                                                                      # list of objects which need to be exported
        DUPLICATES_MESHES_NAMES = []                                                        # list of newly created meshes which need to be removed at the end
      
        
        # 1 make current object active
        bpy.ops.object.select_all(action='DESELECT')                                        # снимем выделение со всего
        OBJECT.select_set(True)                                                             # выберем только текущий объект
        bpy.context.view_layer.objects.active = OBJECT                                      # сделаем его активным
        
        
        # 2 ready если простой меш без модификаторов
        if OBJECT.type == 'MESH' and not OBJECT.modifiers:
            print( str(tabs) + '\tExport simple MESH [' + str(OBJECT.name) + '] start:')
            ###EXPORTING.append(OBJECT)
            ExportObject.exportOneObjectData(OBJECT, None, self, context, tabs)
            ###print( str(tabs) + '\tExport simple MESH [' + str(OBJECT.name) + '] done!')
                 
        # 3 ready если меш с модификаторами
        if OBJECT.type == 'MESH' and OBJECT.modifiers:# and context.scene.bApplyMeshModifiers == True:
            print( str(tabs) + '\tExport modified MESH [' + str(OBJECT.name) + '] start:')
            copy = ExportObject.apply_modifiers_to_duplicate(OBJECT, None)
            ###EXPORTING.append(copy)
            ExportObject.exportOneObjectData(copy, None, self, context, tabs)
            DUPLICATES_MESHES_NAMES.append(copy.data.name)                
            ###print( str(tabs) + '\tExport modified MESH [' + str(OBJECT.name) + '] done!')
                  
        # 4 ready если слинкованная коллекция (AI-generated)
        if OBJECT.instance_type == 'COLLECTION' and OBJECT.instance_collection:
            print( str(tabs) + '\t1) Export linked asset [' + str(OBJECT.name) + '] start:')
            ###print( str(tabs) + '\t\tType: ' + OBJECT.instance_type)
            ###print( str(tabs) + '\t\tCollection: ' + OBJECT.instance_collection.name)
        
            # Получаем все объекты из этой коллекции
            for sub in OBJECT.instance_collection.objects:
                print(str(tabs)+'\t\t%s: %s'%(sub.type, sub.name))
                
                # если модификаторов нет, просто заносим объект в экспортный список
                if not sub.modifiers:
                    print(str(tabs)+'\t\t\tNo modifiers')
                    ###EXPORTING.append(sub) # у этого sub координаты берутся из файла ассета, т.е как правило, в начале мира! а надо учесть смещение коллекции OBJECT
                    ExportObject.exportOneObjectData(sub, OBJECT, self, context, tabs)
                    
                else: # если меш имеет модификаторы, сделаем его копию
                    print(str(tabs)+'\t\t\tMake duplicates')
                    copy = ExportObject.apply_modifiers_to_duplicate(sub, OBJECT)
                    ###EXPORTING.append(copy)
                    ExportObject.exportOneObjectData(copy, OBJECT, self, context, tabs)
                    DUPLICATES_MESHES_NAMES.append(copy.data.name)
            ###print( str(tabs) + '\tExport linked asset [' + str(OBJECT.name) + '] done!')
      
      
        #print('\n'+ str(tabs)+ '\t2) Objects for export: '     + str(EXPORTING))
        #print(''  + str(tabs)+ '\t3) Duplicated meshes list: ' + str(DUPLICATES_MESHES_NAMES)+'\n')
        
        # ~ print(''  + str(tabs)+ '\t4) Export datas:')
        # ~ for exp in EXPORTING:
            # ~ print( ''+str(tabs) + '\t\tExport object [' + str(exp.name) + '] start: ')

            # ~ # 2.1 configure and export object materials
            # ~ exportMaterialClass.configureMaterial(exp, tabs)
            # ~ if context.scene.bMaterials == True:                                            # по галочке
                # ~ print(str(tabs)+'\t\t\tMaterials...')
                # ~ exportMaterialClass.exportMaterial(exp, self, context)                   # материалы для этого объекта

            # ~ # 2.2 export object description
            # ~ if context.scene.bExportLevel:                                                  # по галочке запишем в файл
                # ~ print(str(tabs)+'\t\t\tDescription...')
                # ~ ExportObject.exportObjectDescription(exp, self, context)

            # ~ # 2.3 export object model after aplying (or not) modificators
            # ~ if context.scene.bModelsAsText == True or context.scene.bModelsAsBinary == True:
                # ~ print(str(tabs)+'\t\t\tMesh...')
                # ~ exportMeshClass.export_model(self, context, exp)                         # по галочке
            # ~ #print('\n')
            # ~ #print( str(tabs) + '\tExport object [' + str(OBJECT.name) + '] done!')

        

        # 5 clear temporaries
        print(''+str(tabs) + '\t5) Clearing duplicates...')
        #-- DUPLICATES_MESHES_NAMES хранит имена мешей дубликатов. Если они не из слинкованной библиотеки, то надо удалить!
        for mesh in (m for m in bpy.data.meshes if m.name in DUPLICATES_MESHES_NAMES): #and m.library == None
            if mesh.library == None:
                print(str(tabs)+'\t\tRemove mesh ' + str(mesh) + ', lib: ' + str(mesh.library) )
                bpy.data.meshes.remove(mesh)
                
						# ~ for arm in (m for m in bpy.data.armatures if m.name in TEMPORARY_MESHES and m.library == None):
							# ~ bpy.data.armatures.remove(arm)
        
        # 6 end of function
        #print( str(tabs) + 'Solo object: [' + str(OBJECT.name) + '], exported!')
        
        print( str(tabs) + '|Exporting one object ['+str(OBJECT.name)+'] done!\n'+str(tabs)+'----------------------------------')

## end ###################


    
    def execute(self, context):
        ALREADY_EXPORTED_RESOURCES.clear()
        activeObject = bpy.context.active_object        # выберем объект
        if activeObject:
            ExportObject.exportOneObject('','', activeObject, self, context, '')
            title = 'Object [' + str(activeObject.name) + '] exported as [' + str(activeObject.name) + ']!'
            ShowMessageBox(title, 'Mesh log:', 'BLENDER')
        else:
            ShowMessageBox('No object selected!', 'Mesh log:', 'BLENDER')
        return {'FINISHED'}
                
        

# READY! button for many export 
class ExportCollection(bpy.types.Operator):
    bl_idname = 'object.export_collection' #запуск командой mesh.output_list_of_objects
    bl_label = 'Export data of collection of objects.'
    bl_description = "Export marked resources of objects from selected collection + write list to file (optional)."
    
    def execute(self, context):
        ALREADY_EXPORTED_RESOURCES.clear()
        runtimeCounter = 0
        
        print('\n\n\n\n\n------------------------------------------------------------------------\nExporting objects from collection: %s\n'%(context.scene.selectedCollection.name))
        
        head = ';demo collection, version of ' + str(datetime.datetime.now()) + '\n' + '\nCAMERA PARAMETERS\n;Camera position - x y z \n'
        try:    #if camera actor exists
            head = head + 'p ' + str(camera.location.x) + ' ' + str(camera.location.y) + ' ' + str(camera.location.z) + '\n' #записали координаты
            head = head + '\n;Camera rotation quaternion in format W X Y Z\n' + 'v ' + str(camera.rotation_quaternion.w) + ' ' + str(camera.rotation_quaternion.x) + ' ' + str(camera.rotation_quaternion.y) + ' ' + str(camera.rotation_quaternion.z) + '\nEND CAMERA PARAMETERS\n' #записали направление камеры
        except:  #if there are no Camera actor
            head = head + ';default position\np 7.35889 -6.92579 4.95831\n \n;Camera rotation quaternion \n v 0.483536 0.208704 0.336872 0.780483\n END CAMERA PARAMETERS\n\n'  #записали параметры камеры
        
        tail = '\n\nEND LEVEL OBJECTS LIST\n'
        
        
        
        # ~ LevelDescription = open(context.scene.collectionFolder, 'w')

        
        # only if check mark "Export Level to file" is true, update it 
        if context.scene.bExportLevel:
            # open file anyway
            try:
                LevelDescription = open(context.scene.collectionFolder, 'w')
                print('File opened: %s'%(context.scene.collectionFolder))
                #outputValue = context.scene.collectionFolder
            except:
                print('Collection export error: Cannot create file for collection description! Break!\n')
                return

            # rewrite file data depending of export type: 
            if context.scene.setType == "0":        # if export as runtime-like, add camera description
                LevelDescription.write(';demo collection, version of ' + str(datetime.datetime.now()) + '\n')
                LevelDescription.write('\nCAMERA PARAMETERS\n;Camera position - x y z \n')

                try:    #if camera actor exists
                    camera = bpy.data.objects['Camera']
                    LevelDescription.write('p ' +str(camera.location.x) + ' ' + str(camera.location.y) + ' ' + str(camera.location.z) + '\n' ) #записали координаты
                    LevelDescription.write('\n;Camera rotation quaternion in format W X Y Z\n')
                    LevelDescription.write('v ' + str(camera.rotation_quaternion.w) + ' ' + str(camera.rotation_quaternion.x) + ' ' + str(camera.rotation_quaternion.y) + ' ' + str(camera.rotation_quaternion.z) + '\nEND CAMERA PARAMETERS\n') #записали направление камеры

                except:  #if there are no Camera actor
                    LevelDescription.write(';default position\np 7.35889 -6.92579 4.95831\n\n;Camera rotation quaternion \nv 0.483536 0.208704 0.336872 0.780483\nEND CAMERA PARAMETERS\n\n' ) #записали параметры камеры
            
            # close file anyway
            LevelDescription.close()
        
        # просто перекидываем все видимые объекты коллекции в exportOneObject, там разберутся
        
        mainSelectedCollection = bpy.data.collections[context.scene.selectedCollection.name]
        
        if mainSelectedCollection.hide_viewport == False:														# если главная выбираемая в панели коллекция mainSelectedCollection не скрыта (значок монитора), то
            print('Collection [%s] is visible.'%(mainSelectedCollection.name))
            
            # 0-й уровень: переберем видимые объекты выбранной главной коллекции mycollection
            for OBJECT in (obj0 for obj0 in mainSelectedCollection.objects if obj0.hide_viewport==False) :
                ExportObject.exportOneObject(head, tail, OBJECT, self, context, '\t')

            # 1-й уровень: переберем дочерние видимые (монитор) коллекции
            for subCollection in  (collection_1 for collection_1 in mainSelectedCollection.children if collection_1.hide_viewport == False) :
                # 2-й уровень: переберем видимые объекты дочерней коллекции
                for subObject in (obj2 for obj2 in subCollection.objects if obj2.hide_viewport == False) :		#hide_get()==False):
                    ExportObject.exportOneObject(head, tail, subObject, self, context, '\t\t')

                # 2-й уровень: переберем дочерние коллекции данной дочерней коллекции
                for subSubCollection in ( subcollection_1 for subcollection_1 in subCollection.children if subcollection_1.hide_viewport == False):
                    # 3-й уровень: переберем видимые объекты данной поддочерней коллекции
                    for subSubObject in (obj3 for obj3 in subSubCollection.objects if obj3.hide_viewport == False ):		#hide_get()==False):
                        ExportObject.exportOneObject(head, tail, subSubObject, self, context,'\t\t\t')
        
        
        # only if check mark "Export Level to file" is true and export type is runtime-like, add final info 
        if context.scene.bExportLevel and context.scene.setType == "0":                                      
            LevelDescription = open(context.scene.collectionFolder, 'a')
            LevelDescription.write('\n\nEND LEVEL OBJECTS LIST\n')
            LevelDescription.close()
        
        print('\nCollection [%s] exported!'%(context.scene.selectedCollection.name))     
        ShowMessageBox('Collection exported', 'Mesh log:', 'BLENDER')
        return {'FINISHED'}    



# READY! this class desribes the visual of the addon: which fields exists
class interfaceDescriptionClass(PropertyGroup):

    def updateFolders(self, context):
        slash = '' if context.scene.operationSystem == "0" else '\\'
        context.scene.logFolder = context.scene.projectFolder+slash+"EXPORTER_LOG.txt"    #обновим местонахождение файла лога

    def updateCollectionOutputFileName(self, context):
        context.scene.collectionFolder = context.scene.projectFolder + str(context.scene.selectedCollection.name) + ".ltx"

    def updateFramesCount(self, context):
        a = int(context.scene.iEndKey)
        b = int(context.scene.iStartKey)
        c = a - b + 1
        context.scene.iTotalKeys = str(c)

    def updateKeyframesCount(self, context):

        #bpy.data.actions[context.scene.action].frame_range.x

        context.scene.iStartKey = str(int(context.scene.action.frame_range.x))
        context.scene.iEndKey = str(int(context.scene.action.frame_range.y))
        interfaceDescriptionClass.updateFramesCount(self, context)

    def updateAttachedAnimations(self, context):    #обновим список анимаций, назначенных выбранному скелету
        obj_bones = []


    bpy.types.Scene.operationSystem     = bpy.props.EnumProperty( name="OS", description="Path style depending on your OS ", items=[ ("0", "Linux-style", ""), ("1", "Windows-style", "")  ], default="0", update=updateFolders )

    bpy.types.Scene.export_normals_from        = bpy.props.EnumProperty( name="Get normals from:", description="Choose ",   items=  [
        ("1", "triangle", "get normals from triangles"),
        ("0", "vertex", "get normals from vertexes") ],
    default="1"  )

	# способ вывода информации о коллекции: для рантайм-чтения, для копирования в c++ код 1, для c++ кода 2
    bpy.types.Scene.setType        = bpy.props.EnumProperty( name="Export set", description="Choose ",   items=  [ ("0", "runtime-like", "[index] MESH\nsysname\nposition\ndirection\nmodel\nmaterial\nEND"), ("1", "code-like 1", "ccccbc"), ("2", "code-like 2", "addEntity(name,vec3(),quat(),meshName,{collision},""MESH"",{material_0,material_N,},""none"",""forward"");") ], default="0"  )

    bpy.types.Scene.projectFolder       = bpy.props.StringProperty(name="Project folder:", description="Place where to export data", default="/mnt/3D_OpenGL/fhJune2024/datas/", update = updateFolders)
    bpy.types.Scene.logFolder           = bpy.props.StringProperty(name="Logfile:", description="exporter log file", default="EXPORTER_LOG.txt")
    bpy.types.Scene.collectionFolder    = bpy.props.StringProperty(name="Set folder:", description="exporter collection file", default="")


    bpy.types.Scene.bExportLevel    = bpy.props.BoolProperty(name="Export level to file", description="enable exporting level description", default = True)		# галочка необходимости экспорта уровня
    bpy.types.Scene.bModelsAsBinary = bpy.props.BoolProperty(name="Export models binary", description="enable exporting meshes data in binary format", default = False)
    bpy.types.Scene.bModelsAsText   = bpy.props.BoolProperty(name="Export models as text", description="enable exporting meshes data as text", default = True)

    bpy.types.Scene.bApplyMeshModifiers = bpy.props.BoolProperty(name="Apply mesh modifiers", description="", default = False)

    bpy.types.Scene.bMaterials      = bpy.props.BoolProperty(name="Export materials", description="enable exporting materials", default = False)
    bpy.types.Scene.bTextures       = bpy.props.BoolProperty(name="Save used textures", description="enable exporting textures", default = False)

    bpy.types.Scene.bRewrite        = bpy.props.BoolProperty(name="Rewrite existing assets", description="enable rewriting assets", default = False)

    # bpy.types.Scene.bBakeLightmaps       = bpy.props.BoolProperty(name="Bake lightmap", description="enable baking textures", default = False)
    # #bpy.types.Scene.bBindLightmaps      = bpy.props.BoolProperty(name="Bind lightmap", description="enable export textures", default = False)
    # bpy.types.Scene.bExportLightmaps      = bpy.props.BoolProperty(name="Export lightmap", description="enable export textures", default = False)
    # bpy.types.Scene.eLightmapSize        = bpy.props.EnumProperty( name="Lightmap size", description="Choose ",   items=  [ ("1", "256", ""), ("2", "512", ""), ("4", "1024", ""), ("8", "2048", "") ], default="1"  )

    # bpy.types.Scene.bDraftLightmaps      = bpy.props.BoolProperty(name="Draft 128x128 lightmap", description="enable draft baking for speed", default = True)
    #
    # bpy.types.Scene.bEnableLightmaps      = bpy.props.BoolProperty(name="Enable use baked lightmaps", description="", default = False)

    bpy.types.Scene.selectedCollection  = bpy.props.PointerProperty(name="Collection", description="Which collection to export", type=bpy.types.Collection, update = updateCollectionOutputFileName) #Mesh Object Scene Sound Texture Armature Action


    bpy.types.Scene.skeleton                = bpy.props.PointerProperty(name="Armature", type=bpy.types.Armature, update = updateAttachedAnimations)
    bpy.types.Scene.action                  = bpy.props.PointerProperty(name="Action", description="Select animation for exporting", type=bpy.types.Action, update = updateKeyframesCount)
    bpy.types.Scene.action_baked            = bpy.props.PointerProperty(name="Action baked", type=bpy.types.Action)

    bpy.types.Scene.iStartKey          = bpy.props.StringProperty(name="Start", description="serialnumber of first key", default="0", update = updateFramesCount)
    bpy.types.Scene.iEndKey            = bpy.props.StringProperty(name="Finish", description="serialnumber of last key", default="59", update = updateFramesCount)
    bpy.types.Scene.iTotalKeys         = bpy.props.StringProperty(name="Frames", description="count of keys general", default="60")
    bpy.types.Scene.fScale             = bpy.props.StringProperty(name="Scale", description="scale coeff for models", default="1")

	##
    bpy.types.Scene.bBakeLightmaps       = bpy.props.BoolProperty(name="Bake lightmap", description="enable baking textures", default = False)
    #bpy.types.Scene.bBindLightmaps      = bpy.props.BoolProperty(name="Bind lightmap", description="enable export textures", default = False)
    bpy.types.Scene.bExportLightmaps      = bpy.props.BoolProperty(name="Export lightmap", description="enable export textures", default = False)
    bpy.types.Scene.eLightmapSize        = bpy.props.EnumProperty( name="Lightmap size", description="Choose ",   items=  [ ("1", "256", ""), ("2", "512", ""), ("4", "1024", ""), ("8", "2048", "") ], default="1"  )

    bpy.types.Scene.bDraftLightmaps      = bpy.props.BoolProperty(name="Draft 128x128 lightmap", description="enable draft baking for speed", default = True)

    bpy.types.Scene.bEnableLightmaps      = bpy.props.BoolProperty(name="Enable use baked lightmaps", description="", default = False)




#class which describes the visual of addon, like html
class VisualDescription(bpy.types.Panel):
    bl_idname = 'description.panel'
    bl_label = 'Visual Description'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context): #function which draws all the buttons and labels
        layout = self.layout
        scene = context.scene

        # ~ selectedObject = bpy.context.active_object     #select the object
        
        # ~ if selectedObject.type=='MESH' and selectedObject.parent:
            # ~ selectedObject = selectedObject.parent
        # ~ if selectedObject.type=='ARMATURE':
            # ~ selectedObject = selectedObject
        
        layout.prop(scene, "projectFolder")


        layout.prop(scene, "operationSystem", expand=True)      #переключалка стиля пути
        layout.prop(scene, "export_normals_from", expand=True)

        # ~ self.layout.operator("mesh.export_mesh",           text="Export Mesh")   #кнопка вызова экспорта меша
        self.layout.operator("mesh.export_collision",      text="Export Collision shell")   #кнопка вызова экспорта коллизии

        #### #self.layout.operator("mesh.export_material",       text="Export material")  # кнопка экспорта материала
        ##### ~ self.layout.operator("mesh.export_lightmap",       text="Export lightmap")  # кнопка экспорта карты света

        self.layout.label(text = "<--------Skeleton/Animation export---------------->")
        self.layout.operator("mesh.export_armature",           text="Export Armature")   #кнопка вызова экспорта скелета
        layout.prop(scene, "action")

        layout.prop(scene, "fScale")

        self.layout.operator("mesh.export_animation",           text="Export Animation")  # кнопка экспорта анимаций

        self.layout.label(text = "<--------Total collection export settings:------------------------------>")

        layout.prop(scene, "bModelsAsText")
        layout.prop(scene, "bModelsAsBinary")
        # ~ layout.prop(scene, "bApplyMeshModifiers")
        layout.prop(scene, "bMaterials")
        layout.prop(scene, "bTextures")
        
        layout.prop(scene, "bBakeLightmaps")
        layout.prop(scene, "bDraftLightmaps")
        layout.prop(scene, "bExportLightmaps")
        layout.prop(scene, "bEnableLightmaps")
        layout.prop(scene, "eLightmapSize", expand=False)
        
        self.layout.operator("mesh.export_lightmap",       text="Export object lightmap")  # кнопка экспорта карты света
        
        # ~ outputParametersString = "≡ Selected " + bpy.context.active_object.type + ": " + bpy.context.active_object.name
        # ~ self.layout.label(text=outputParametersString)

        self.layout.operator("object.export_object",           text="↑↑ Export object ↑↑")   #кнопка вызова экспорта одного объекта

        layout.prop(scene, "selectedCollection")
        collectionFilePath = context.scene.projectFolder + str(context.scene.selectedCollection.name) + ".ltx"
        self.layout.label(text=collectionFilePath)
        
        layout.prop(scene, "setType", expand=True)
        layout.prop(scene, "bExportLevel")
        
        self.layout.operator("object.export_collection",           text="↑↑ Export collection ↑↑")   #кнопка вызова экспорта сета (сборная солянка)


        


        version = "ver. %d.%d.%d" % bl_info["version"]
        self.layout.label(text=version, icon="SETTINGS")




# list of registered classes
registered_classes = []

# list of my addon`s classes
classes = ( VisualDescription, interfaceDescriptionClass, ExportCollection, ExportObject, exportMaterialClass, exportMeshClass, exportAnimationClass, exportArmatureClass, exportCollisionBoxClass, exportLightmapClass )


def register():
    from bpy.utils import register_class
    for cls in classes:
        bpy.utils.register_class(cls)
        registered_classes.append(cls)
    bpy.types.Scene.AnimatorProps = PointerProperty(type=interfaceDescriptionClass)

def unregister():
    from bpy.utils import unregister_class
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.AnimatorProps
