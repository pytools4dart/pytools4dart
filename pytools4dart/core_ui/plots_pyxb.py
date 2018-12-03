# ./plots.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e92452c8d3e28a9e27abfc9994d2007779e7f4c9
# Generated 2018-09-24 13:33:48.113690 by PyXB version 1.2.6 using Python 2.7.12.final.0
# Namespace AbsentNamespace0

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six
# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b3d8868c-bfed-11e8-a7d7-e470b8806560')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.6'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# A holder for module-level binding classes so we can access them from
# inside class definitions where property names may conflict.
_module_typeBindings = pyxb.utils.utility.Object()

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.CreateAbsentNamespace()
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 16, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Plots uses Python identifier Plots
    __Plots = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Plots'), 'Plots', '__AbsentNamespace0_CTD_ANON_Plots', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 18, 3), )

    
    Plots = property(__Plots.value, __Plots.set, None, None)

    
    # Attribute version uses Python identifier version
    __version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'version'), 'version', '__AbsentNamespace0_CTD_ANON_version', pyxb.binding.datatypes.string, unicode_default='5.7.1')
    __version._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 20, 2)
    __version._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 20, 2)
    
    version = property(__version.value, __version.set, None, ' Version of the plots.xml file. Depends of the version on DART itself. Version of the plots.xml file. Depends of the version on DART itself.')

    
    # Attribute build uses Python identifier build
    __build = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'build'), 'build', '__AbsentNamespace0_CTD_ANON_build', pyxb.binding.datatypes.string, unicode_default='0')
    __build._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 26, 2)
    __build._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 26, 2)
    
    build = property(__build.value, __build.set, None, '  ')

    _ElementMap.update({
        __Plots.name() : __Plots
    })
    _AttributeMap.update({
        __version.name() : __version,
        __build.name() : __build
    })
_module_typeBindings.CTD_ANON = CTD_ANON


# Complex type _Plots with content type ELEMENT_ONLY
class Plots (pyxb.binding.basis.complexTypeDefinition):
    """ Contains the description of the working environment for the Vegetation module. Contains also the list of the plots for the simulation and their optical(s) property(ies). Contains the description of the working environment for the Vegetation module. Contains also the list of the plots for the simulation and their optical(s) property(ies)."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_Plots')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 35, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element ExtraPlotsTextFileDefinition uses Python identifier ExtraPlotsTextFileDefinition
    __ExtraPlotsTextFileDefinition = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ExtraPlotsTextFileDefinition'), 'ExtraPlotsTextFileDefinition', '__AbsentNamespace0_Plots_ExtraPlotsTextFileDefinition', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 41, 3), )

    
    ExtraPlotsTextFileDefinition = property(__ExtraPlotsTextFileDefinition.value, __ExtraPlotsTextFileDefinition.set, None, None)

    
    # Element ImportationFichierRaster uses Python identifier ImportationFichierRaster
    __ImportationFichierRaster = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ImportationFichierRaster'), 'ImportationFichierRaster', '__AbsentNamespace0_Plots_ImportationFichierRaster', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 42, 3), )

    
    ImportationFichierRaster = property(__ImportationFichierRaster.value, __ImportationFichierRaster.set, None, None)

    
    # Element Plot uses Python identifier Plot
    __Plot = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Plot'), 'Plot', '__AbsentNamespace0_Plots_Plot', True, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 43, 3), )

    
    Plot = property(__Plot.value, __Plot.set, None, None)

    
    # Attribute isVegetation uses Python identifier isVegetation
    __isVegetation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'isVegetation'), 'isVegetation', '__AbsentNamespace0_Plots_isVegetation', pyxb.binding.datatypes.int, unicode_default='0')
    __isVegetation._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 45, 2)
    __isVegetation._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 45, 2)
    
    isVegetation = property(__isVegetation.value, __isVegetation.set, None, ' Indicate if there is information for the module Vegetation. 1 if the user wants to use the Vegetation module, 0 otherwise. Indicate if there is information for the module Vegetation. 1 if the user wants to use the Vegetation module, 0 otherwise.')

    
    # Attribute addExtraPlotsTextFile uses Python identifier addExtraPlotsTextFile
    __addExtraPlotsTextFile = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'addExtraPlotsTextFile'), 'addExtraPlotsTextFile', '__AbsentNamespace0_Plots_addExtraPlotsTextFile', pyxb.binding.datatypes.int, unicode_default='0')
    __addExtraPlotsTextFile._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 51, 2)
    __addExtraPlotsTextFile._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 51, 2)
    
    addExtraPlotsTextFile = property(__addExtraPlotsTextFile.value, __addExtraPlotsTextFile.set, None, ' Choose if you want to add an extra plot file  Choose if you want to add an extra plot file ')

    _ElementMap.update({
        __ExtraPlotsTextFileDefinition.name() : __ExtraPlotsTextFileDefinition,
        __ImportationFichierRaster.name() : __ImportationFichierRaster,
        __Plot.name() : __Plot
    })
    _AttributeMap.update({
        __isVegetation.name() : __isVegetation,
        __addExtraPlotsTextFile.name() : __addExtraPlotsTextFile
    })
_module_typeBindings.Plots = Plots
Namespace.addCategoryObject('typeBinding', '_Plots', Plots)


# Complex type _ExtraPlotsTextFileDefinition with content type EMPTY
class ExtraPlotsTextFileDefinition (pyxb.binding.basis.complexTypeDefinition):
    """ Extra plot file definition Extra plot file definition"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_ExtraPlotsTextFileDefinition')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 59, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute extraPlotsFileName uses Python identifier extraPlotsFileName
    __extraPlotsFileName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'extraPlotsFileName'), 'extraPlotsFileName', '__AbsentNamespace0_ExtraPlotsTextFileDefinition_extraPlotsFileName', pyxb.binding.datatypes.string, unicode_default='plots.txt')
    __extraPlotsFileName._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 66, 2)
    __extraPlotsFileName._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 66, 2)
    
    extraPlotsFileName = property(__extraPlotsFileName.value, __extraPlotsFileName.set, None, ' Path to extra plot file Path to extra plot file')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __extraPlotsFileName.name() : __extraPlotsFileName
    })
_module_typeBindings.ExtraPlotsTextFileDefinition = ExtraPlotsTextFileDefinition
Namespace.addCategoryObject('typeBinding', '_ExtraPlotsTextFileDefinition', ExtraPlotsTextFileDefinition)


# Complex type _ImportationFichierRaster with content type ELEMENT_ONLY
class ImportationFichierRaster (pyxb.binding.basis.complexTypeDefinition):
    """ Contains the information of the input files for the Vegetation module. Contains the information of the input files for the Vegetation module."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_ImportationFichierRaster')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 74, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element VegetationProperties uses Python identifier VegetationProperties
    __VegetationProperties = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'VegetationProperties'), 'VegetationProperties', '__AbsentNamespace0_ImportationFichierRaster_VegetationProperties', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 80, 3), )

    
    VegetationProperties = property(__VegetationProperties.value, __VegetationProperties.set, None, None)

    
    # Element RasterCOSInformation uses Python identifier RasterCOSInformation
    __RasterCOSInformation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'RasterCOSInformation'), 'RasterCOSInformation', '__AbsentNamespace0_ImportationFichierRaster_RasterCOSInformation', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 81, 3), )

    
    RasterCOSInformation = property(__RasterCOSInformation.value, __RasterCOSInformation.set, None, None)

    _ElementMap.update({
        __VegetationProperties.name() : __VegetationProperties,
        __RasterCOSInformation.name() : __RasterCOSInformation
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ImportationFichierRaster = ImportationFichierRaster
Namespace.addCategoryObject('typeBinding', '_ImportationFichierRaster', ImportationFichierRaster)


# Complex type _VegetationProperties with content type ELEMENT_ONLY
class VegetationProperties (pyxb.binding.basis.complexTypeDefinition):
    """ Properties of the raster image of the Vegetation module (name, number of lines/colunms, type of the pixel ...). Properties of the raster image of the Vegetation module (name, number of lines/colunms, type of the pixel ...)."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_VegetationProperties')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 85, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element SelectSubZoneProperties uses Python identifier SelectSubZoneProperties
    __SelectSubZoneProperties = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'SelectSubZoneProperties'), 'SelectSubZoneProperties', '__AbsentNamespace0_VegetationProperties_SelectSubZoneProperties', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 91, 3), )

    
    SelectSubZoneProperties = property(__SelectSubZoneProperties.value, __SelectSubZoneProperties.set, None, None)

    
    # Attribute selectSubZone uses Python identifier selectSubZone
    __selectSubZone = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'selectSubZone'), 'selectSubZone', '__AbsentNamespace0_VegetationProperties_selectSubZone', pyxb.binding.datatypes.int, unicode_default='0')
    __selectSubZone._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 93, 2)
    __selectSubZone._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 93, 2)
    
    selectSubZone = property(__selectSubZone.value, __selectSubZone.set, None, ' Allows the user to work on a subzone of the raster image. 1 for extracting a sub-zone of the COS, 0 otherwise.  Allows the user to work on a subzone of the raster image. 1 for extracting a sub-zone of the COS, 0 otherwise. ')

    
    # Attribute coverLandMapFileName uses Python identifier coverLandMapFileName
    __coverLandMapFileName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'coverLandMapFileName'), 'coverLandMapFileName', '__AbsentNamespace0_VegetationProperties_coverLandMapFileName', pyxb.binding.datatypes.string, unicode_default='land_cover.mp#')
    __coverLandMapFileName._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 99, 2)
    __coverLandMapFileName._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 99, 2)
    
    coverLandMapFileName = property(__coverLandMapFileName.value, __coverLandMapFileName.set, None, ' Raster file name. It must be in the simulation "input" directory of the simulation. Raster file name. It must be in the simulation "input" directory of the simulation.')

    
    # Attribute coverLandMapDescFileName uses Python identifier coverLandMapDescFileName
    __coverLandMapDescFileName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'coverLandMapDescFileName'), 'coverLandMapDescFileName', '__AbsentNamespace0_VegetationProperties_coverLandMapDescFileName', pyxb.binding.datatypes.string, unicode_default='Desc_CoverLandMap.txt')
    __coverLandMapDescFileName._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 105, 2)
    __coverLandMapDescFileName._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 105, 2)
    
    coverLandMapDescFileName = property(__coverLandMapDescFileName.value, __coverLandMapDescFileName.set, None, '  ')

    
    # Attribute OverwritePlots uses Python identifier OverwritePlots
    __OverwritePlots = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'OverwritePlots'), 'OverwritePlots', '__AbsentNamespace0_VegetationProperties_OverwritePlots', pyxb.binding.datatypes.int, unicode_default='1')
    __OverwritePlots._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 111, 2)
    __OverwritePlots._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 111, 2)
    
    OverwritePlots = property(__OverwritePlots.value, __OverwritePlots.set, None, ' Allows Vegetation module to keep or crush the current plots. 1, the plots are crushed. 0, the plots are kept. Allows Vegetation module to keep or crush the current plots. 1, the plots are crushed. 0, the plots are kept.')

    _ElementMap.update({
        __SelectSubZoneProperties.name() : __SelectSubZoneProperties
    })
    _AttributeMap.update({
        __selectSubZone.name() : __selectSubZone,
        __coverLandMapFileName.name() : __coverLandMapFileName,
        __coverLandMapDescFileName.name() : __coverLandMapDescFileName,
        __OverwritePlots.name() : __OverwritePlots
    })
_module_typeBindings.VegetationProperties = VegetationProperties
Namespace.addCategoryObject('typeBinding', '_VegetationProperties', VegetationProperties)


# Complex type _SelectSubZoneProperties with content type EMPTY
class SelectSubZoneProperties (pyxb.binding.basis.complexTypeDefinition):
    """ Properties of the sub zone. It's defined by a starting point and a number of lines/colunms. Properties of the sub zone. It's defined by a starting point and a number of lines/colunms."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_SelectSubZoneProperties')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 119, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute lineNbSubZone uses Python identifier lineNbSubZone
    __lineNbSubZone = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'lineNbSubZone'), 'lineNbSubZone', '__AbsentNamespace0_SelectSubZoneProperties_lineNbSubZone', pyxb.binding.datatypes.int, unicode_default='5')
    __lineNbSubZone._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 126, 2)
    __lineNbSubZone._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 126, 2)
    
    lineNbSubZone = property(__lineNbSubZone.value, __lineNbSubZone.set, None, ' Number of lines of the subzone. Number of lines of the subzone.')

    
    # Attribute columnOfTopLeftPixel uses Python identifier columnOfTopLeftPixel
    __columnOfTopLeftPixel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'columnOfTopLeftPixel'), 'columnOfTopLeftPixel', '__AbsentNamespace0_SelectSubZoneProperties_columnOfTopLeftPixel', pyxb.binding.datatypes.int, unicode_default='0')
    __columnOfTopLeftPixel._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 132, 2)
    __columnOfTopLeftPixel._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 132, 2)
    
    columnOfTopLeftPixel = property(__columnOfTopLeftPixel.value, __columnOfTopLeftPixel.set, None, ' First column of the sub-zone. First column of the sub-zone.')

    
    # Attribute columnNbSubZone uses Python identifier columnNbSubZone
    __columnNbSubZone = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'columnNbSubZone'), 'columnNbSubZone', '__AbsentNamespace0_SelectSubZoneProperties_columnNbSubZone', pyxb.binding.datatypes.int, unicode_default='5')
    __columnNbSubZone._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 138, 2)
    __columnNbSubZone._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 138, 2)
    
    columnNbSubZone = property(__columnNbSubZone.value, __columnNbSubZone.set, None, ' Number of columns of the sub-zone. Number of columns of the sub-zone.')

    
    # Attribute lineOfTopLeftPixel uses Python identifier lineOfTopLeftPixel
    __lineOfTopLeftPixel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'lineOfTopLeftPixel'), 'lineOfTopLeftPixel', '__AbsentNamespace0_SelectSubZoneProperties_lineOfTopLeftPixel', pyxb.binding.datatypes.int, unicode_default='0')
    __lineOfTopLeftPixel._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 144, 2)
    __lineOfTopLeftPixel._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 144, 2)
    
    lineOfTopLeftPixel = property(__lineOfTopLeftPixel.value, __lineOfTopLeftPixel.set, None, ' First line of the sub-zone. First line of the sub-zone.')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __lineNbSubZone.name() : __lineNbSubZone,
        __columnOfTopLeftPixel.name() : __columnOfTopLeftPixel,
        __columnNbSubZone.name() : __columnNbSubZone,
        __lineOfTopLeftPixel.name() : __lineOfTopLeftPixel
    })
_module_typeBindings.SelectSubZoneProperties = SelectSubZoneProperties
Namespace.addCategoryObject('typeBinding', '_SelectSubZoneProperties', SelectSubZoneProperties)


# Complex type _RasterCOSInformation with content type EMPTY
class RasterCOSInformation (pyxb.binding.basis.complexTypeDefinition):
    """ Properties of the raster image of the Vegetation module (name, number of lines/colunms, type of the pixel ...). Properties of the raster image of the Vegetation module (name, number of lines/colunms, type of the pixel ...)."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_RasterCOSInformation')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 152, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute pixelSizeCol uses Python identifier pixelSizeCol
    __pixelSizeCol = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'pixelSizeCol'), 'pixelSizeCol', '__AbsentNamespace0_RasterCOSInformation_pixelSizeCol', pyxb.binding.datatypes.double, unicode_default='1')
    __pixelSizeCol._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 159, 2)
    __pixelSizeCol._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 159, 2)
    
    pixelSizeCol = property(__pixelSizeCol.value, __pixelSizeCol.set, None, ' Dimension in meters of a pixel of the raster image, along a column. Dimension in meters of a pixel of the raster image, along a column.')

    
    # Attribute nbColCOS uses Python identifier nbColCOS
    __nbColCOS = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'nbColCOS'), 'nbColCOS', '__AbsentNamespace0_RasterCOSInformation_nbColCOS', pyxb.binding.datatypes.int, unicode_default='20')
    __nbColCOS._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 165, 2)
    __nbColCOS._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 165, 2)
    
    nbColCOS = property(__nbColCOS.value, __nbColCOS.set, None, ' Number of columns of the raster image. Number of columns of the raster image.')

    
    # Attribute pixelSizeLi uses Python identifier pixelSizeLi
    __pixelSizeLi = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'pixelSizeLi'), 'pixelSizeLi', '__AbsentNamespace0_RasterCOSInformation_pixelSizeLi', pyxb.binding.datatypes.double, unicode_default='1')
    __pixelSizeLi._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 171, 2)
    __pixelSizeLi._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 171, 2)
    
    pixelSizeLi = property(__pixelSizeLi.value, __pixelSizeLi.set, None, ' Dimension in meters of a pixel of the raster image, along a line. Dimension in meters of a pixel of the raster image, along a line.')

    
    # Attribute pixelByteSizeCOS uses Python identifier pixelByteSizeCOS
    __pixelByteSizeCOS = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'pixelByteSizeCOS'), 'pixelByteSizeCOS', '__AbsentNamespace0_RasterCOSInformation_pixelByteSizeCOS', pyxb.binding.datatypes.int, unicode_default='1')
    __pixelByteSizeCOS._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 177, 2)
    __pixelByteSizeCOS._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 177, 2)
    
    pixelByteSizeCOS = property(__pixelByteSizeCOS.value, __pixelByteSizeCOS.set, None, ' double. double.')

    
    # Attribute nbLiCOS uses Python identifier nbLiCOS
    __nbLiCOS = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'nbLiCOS'), 'nbLiCOS', '__AbsentNamespace0_RasterCOSInformation_nbLiCOS', pyxb.binding.datatypes.int, unicode_default='20')
    __nbLiCOS._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 183, 2)
    __nbLiCOS._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 183, 2)
    
    nbLiCOS = property(__nbLiCOS.value, __nbLiCOS.set, None, ' Number of lines of the raster image. Number of lines of the raster image.')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __pixelSizeCol.name() : __pixelSizeCol,
        __nbColCOS.name() : __nbColCOS,
        __pixelSizeLi.name() : __pixelSizeLi,
        __pixelByteSizeCOS.name() : __pixelByteSizeCOS,
        __nbLiCOS.name() : __nbLiCOS
    })
_module_typeBindings.RasterCOSInformation = RasterCOSInformation
Namespace.addCategoryObject('typeBinding', '_RasterCOSInformation', RasterCOSInformation)


# Complex type _Plot with content type ELEMENT_ONLY
class Plot (pyxb.binding.basis.complexTypeDefinition):
    """ Representation of a DART plot. It's defined by its type, a geometric property and its optical(s) property(ies). The number of optical properties depends of the type of the plot. It can be formed of soil, vegetation or a combinaison of soil and vegetation. Representation of a DART plot. It's defined by its type, a geometric property and its optical(s) property(ies). The number of optical properties depends of the type of the plot. It can be formed of soil, vegetation or a combinaison of soil and vegetation."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_Plot')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 191, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Polygon2D uses Python identifier Polygon2D
    __Polygon2D = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Polygon2D'), 'Polygon2D', '__AbsentNamespace0_Plot_Polygon2D', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 197, 3), )

    
    Polygon2D = property(__Polygon2D.value, __Polygon2D.set, None, None)

    
    # Element Rectangle2D uses Python identifier Rectangle2D
    __Rectangle2D = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Rectangle2D'), 'Rectangle2D', '__AbsentNamespace0_Plot_Rectangle2D', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 198, 3), )

    
    Rectangle2D = property(__Rectangle2D.value, __Rectangle2D.set, None, None)

    
    # Element GroundOpticalPropertyLink uses Python identifier GroundOpticalPropertyLink
    __GroundOpticalPropertyLink = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'GroundOpticalPropertyLink'), 'GroundOpticalPropertyLink', '__AbsentNamespace0_Plot_GroundOpticalPropertyLink', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 199, 3), )

    
    GroundOpticalPropertyLink = property(__GroundOpticalPropertyLink.value, __GroundOpticalPropertyLink.set, None, None)

    
    # Element GroundThermalPropertyLink uses Python identifier GroundThermalPropertyLink
    __GroundThermalPropertyLink = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink'), 'GroundThermalPropertyLink', '__AbsentNamespace0_Plot_GroundThermalPropertyLink', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 200, 3), )

    
    GroundThermalPropertyLink = property(__GroundThermalPropertyLink.value, __GroundThermalPropertyLink.set, None, None)

    
    # Element PlotVegetationProperties uses Python identifier PlotVegetationProperties
    __PlotVegetationProperties = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'PlotVegetationProperties'), 'PlotVegetationProperties', '__AbsentNamespace0_Plot_PlotVegetationProperties', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 201, 3), )

    
    PlotVegetationProperties = property(__PlotVegetationProperties.value, __PlotVegetationProperties.set, None, None)

    
    # Element PlotAirProperties uses Python identifier PlotAirProperties
    __PlotAirProperties = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'PlotAirProperties'), 'PlotAirProperties', '__AbsentNamespace0_Plot_PlotAirProperties', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 202, 3), )

    
    PlotAirProperties = property(__PlotAirProperties.value, __PlotAirProperties.set, None, None)

    
    # Element PlotWaterProperties uses Python identifier PlotWaterProperties
    __PlotWaterProperties = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'PlotWaterProperties'), 'PlotWaterProperties', '__AbsentNamespace0_Plot_PlotWaterProperties', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 203, 3), )

    
    PlotWaterProperties = property(__PlotWaterProperties.value, __PlotWaterProperties.set, None, None)

    
    # Attribute hidden uses Python identifier hidden
    __hidden = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'hidden'), 'hidden', '__AbsentNamespace0_Plot_hidden', pyxb.binding.datatypes.int, unicode_default='0')
    __hidden._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 205, 2)
    __hidden._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 205, 2)
    
    hidden = property(__hidden.value, __hidden.set, None, " If you select this option, this plot are not use in all DART modules, \\n it's useful if you want conserve plot properties backup without delete this for tests  If you select this option, this plot are not use in all DART modules, \\n it's useful if you want conserve plot properties backup without delete this for tests ")

    
    # Attribute repeatedOnBorder uses Python identifier repeatedOnBorder
    __repeatedOnBorder = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'repeatedOnBorder'), 'repeatedOnBorder', '__AbsentNamespace0_Plot_repeatedOnBorder', pyxb.binding.datatypes.int, unicode_default='1')
    __repeatedOnBorder._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 211, 2)
    __repeatedOnBorder._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 211, 2)
    
    repeatedOnBorder = property(__repeatedOnBorder.value, __repeatedOnBorder.set, None, ' If part of the object goes beyond the border of the scene, this part is copied on the other side of the scene.  If part of the object goes beyond the border of the scene, this part is copied on the other side of the scene. ')

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__AbsentNamespace0_Plot_type', pyxb.binding.datatypes.int, unicode_default='1')
    __type._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 217, 2)
    __type._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 217, 2)
    
    type = property(__type.value, __type.set, None, ' Plot: "vegetation layer + ground surface over the ground of the scene", "ground surface over the ground of the scene" or "vegetation layer over the ground of the scene" Plot: "vegetation layer + ground surface over the ground of the scene", "ground surface over the ground of the scene" or "vegetation layer over the ground of the scene"')

    
    # Attribute form uses Python identifier form
    __form = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'form'), 'form', '__AbsentNamespace0_Plot_form', pyxb.binding.datatypes.int, unicode_default='0')
    __form._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 223, 2)
    __form._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 223, 2)
    
    form = property(__form.value, __form.set, None, ' How the plot geometry will be defined. This can be done by giving the dimension and position of a rectangle, or by directly giving the coordinates of the four corners of the the delimiting quadrilater. How the plot geometry will be defined. This can be done by giving the dimension and position of a rectangle, or by directly giving the coordinates of the four corners of the the delimiting quadrilater.')

    
    # Attribute isDisplayed uses Python identifier isDisplayed
    __isDisplayed = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'isDisplayed'), 'isDisplayed', '__AbsentNamespace0_Plot_isDisplayed', pyxb.binding.datatypes.int, unicode_default='1')
    __isDisplayed._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 229, 2)
    __isDisplayed._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 229, 2)
    
    isDisplayed = property(__isDisplayed.value, __isDisplayed.set, None, " Objects's positions are taken from the position file.\\nDesactivate this option if you experience some slowdown. Objects's positions are taken from the position file.\\nDesactivate this option if you experience some slowdown.")

    _ElementMap.update({
        __Polygon2D.name() : __Polygon2D,
        __Rectangle2D.name() : __Rectangle2D,
        __GroundOpticalPropertyLink.name() : __GroundOpticalPropertyLink,
        __GroundThermalPropertyLink.name() : __GroundThermalPropertyLink,
        __PlotVegetationProperties.name() : __PlotVegetationProperties,
        __PlotAirProperties.name() : __PlotAirProperties,
        __PlotWaterProperties.name() : __PlotWaterProperties
    })
    _AttributeMap.update({
        __hidden.name() : __hidden,
        __repeatedOnBorder.name() : __repeatedOnBorder,
        __type.name() : __type,
        __form.name() : __form,
        __isDisplayed.name() : __isDisplayed
    })
_module_typeBindings.Plot = Plot
Namespace.addCategoryObject('typeBinding', '_Plot', Plot)


# Complex type _Polygon2D with content type ELEMENT_ONLY
class Polygon2D (pyxb.binding.basis.complexTypeDefinition):
    """ Representation of a DART polygon. He's defined by his 4 corners, starting form the top left one, and turning anticlockwise. Representation of a DART polygon. He's defined by his 4 corners, starting form the top left one, and turning anticlockwise."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_Polygon2D')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 237, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Point2D uses Python identifier Point2D
    __Point2D = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Point2D'), 'Point2D', '__AbsentNamespace0_Polygon2D_Point2D', True, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 243, 3), )

    
    Point2D = property(__Point2D.value, __Point2D.set, None, None)

    _ElementMap.update({
        __Point2D.name() : __Point2D
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Polygon2D = Polygon2D
Namespace.addCategoryObject('typeBinding', '_Polygon2D', Polygon2D)


# Complex type _Point2D with content type EMPTY
class Point2D (pyxb.binding.basis.complexTypeDefinition):
    """ Optical properties for a DART soil phase function. Optical properties for a DART soil phase function."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_Point2D')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 247, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute y uses Python identifier y
    __y = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'y'), 'y', '__AbsentNamespace0_Point2D_y', pyxb.binding.datatypes.double, unicode_default='0.00')
    __y._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 254, 2)
    __y._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 254, 2)
    
    y = property(__y.value, __y.set, None, ' y coordinate of a corner of the quadrilateral that defines the plot. Points are defined anticlockwise y coordinate of a corner of the quadrilateral that defines the plot. Points are defined anticlockwise')

    
    # Attribute x uses Python identifier x
    __x = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'x'), 'x', '__AbsentNamespace0_Point2D_x', pyxb.binding.datatypes.double, unicode_default='0.00')
    __x._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 260, 2)
    __x._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 260, 2)
    
    x = property(__x.value, __x.set, None, ' x coordinate of a corner of the quadrilateral that defines the plot. Points are defined anticlockwise x coordinate of a corner of the quadrilateral that defines the plot. Points are defined anticlockwise')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __y.name() : __y,
        __x.name() : __x
    })
_module_typeBindings.Point2D = Point2D
Namespace.addCategoryObject('typeBinding', '_Point2D', Point2D)


# Complex type _Rectangle2D with content type EMPTY
class Rectangle2D (pyxb.binding.basis.complexTypeDefinition):
    """ Rectangle2D Rectangle2D"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_Rectangle2D')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 268, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute coteX uses Python identifier coteX
    __coteX = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'coteX'), 'coteX', '__AbsentNamespace0_Rectangle2D_coteX', pyxb.binding.datatypes.double, unicode_default='10')
    __coteX._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 275, 2)
    __coteX._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 275, 2)
    
    coteX = property(__coteX.value, __coteX.set, None, ' Length along X axis (in meters) Length along X axis (in meters)')

    
    # Attribute coteY uses Python identifier coteY
    __coteY = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'coteY'), 'coteY', '__AbsentNamespace0_Rectangle2D_coteY', pyxb.binding.datatypes.double, unicode_default='10')
    __coteY._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 281, 2)
    __coteY._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 281, 2)
    
    coteY = property(__coteY.value, __coteY.set, None, ' Length along Y axis (in meters) Length along Y axis (in meters)')

    
    # Attribute intrinsicRotation uses Python identifier intrinsicRotation
    __intrinsicRotation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'intrinsicRotation'), 'intrinsicRotation', '__AbsentNamespace0_Rectangle2D_intrinsicRotation', pyxb.binding.datatypes.double, unicode_default='0')
    __intrinsicRotation._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 287, 2)
    __intrinsicRotation._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 287, 2)
    
    intrinsicRotation = property(__intrinsicRotation.value, __intrinsicRotation.set, None, ' Rotation around the plot center (in degrees, in the range [-180, 180]) Rotation around the plot center (in degrees, in the range [-180, 180])')

    
    # Attribute centreX uses Python identifier centreX
    __centreX = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'centreX'), 'centreX', '__AbsentNamespace0_Rectangle2D_centreX', pyxb.binding.datatypes.double, unicode_default='5')
    __centreX._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 293, 2)
    __centreX._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 293, 2)
    
    centreX = property(__centreX.value, __centreX.set, None, ' Center along X axis (in meters) Center along X axis (in meters)')

    
    # Attribute centreY uses Python identifier centreY
    __centreY = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'centreY'), 'centreY', '__AbsentNamespace0_Rectangle2D_centreY', pyxb.binding.datatypes.double, unicode_default='5')
    __centreY._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 299, 2)
    __centreY._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 299, 2)
    
    centreY = property(__centreY.value, __centreY.set, None, ' Center along Y axis (in meters) Center along Y axis (in meters)')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __coteX.name() : __coteX,
        __coteY.name() : __coteY,
        __intrinsicRotation.name() : __intrinsicRotation,
        __centreX.name() : __centreX,
        __centreY.name() : __centreY
    })
_module_typeBindings.Rectangle2D = Rectangle2D
Namespace.addCategoryObject('typeBinding', '_Rectangle2D', Rectangle2D)


# Complex type _GroundOpticalPropertyLink with content type EMPTY
class GroundOpticalPropertyLink (pyxb.binding.basis.complexTypeDefinition):
    """ Optical properties for a DART soil phase function (name, type and index). Optical properties for a DART soil phase function (name, type and index)."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_GroundOpticalPropertyLink')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 307, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute indexFctPhase uses Python identifier indexFctPhase
    __indexFctPhase = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'indexFctPhase'), 'indexFctPhase', '__AbsentNamespace0_GroundOpticalPropertyLink_indexFctPhase', pyxb.binding.datatypes.int, unicode_default='0')
    __indexFctPhase._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 314, 2)
    __indexFctPhase._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 314, 2)
    
    indexFctPhase = property(__indexFctPhase.value, __indexFctPhase.set, None, ' Index of the DART phase function of the ground of the plot. Index of the DART phase function of the ground of the plot.')

    
    # Attribute ident uses Python identifier ident
    __ident = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'ident'), 'ident', '__AbsentNamespace0_GroundOpticalPropertyLink_ident', pyxb.binding.datatypes.string, unicode_default='Lambertian_Phase_Function_1')
    __ident._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 320, 2)
    __ident._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 320, 2)
    
    ident = property(__ident.value, __ident.set, None, ' proportion of photons intercepted along an incident direction that are scattered within a solid angle along a given direction proportion of photons intercepted along an incident direction that are scattered within a solid angle along a given direction')

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__AbsentNamespace0_GroundOpticalPropertyLink_type', pyxb.binding.datatypes.int, unicode_default='0')
    __type._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 326, 2)
    __type._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 326, 2)
    
    type = property(__type.value, __type.set, None, ' Type of phase function (lambertian, etc.) Type of phase function (lambertian, etc.)')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __indexFctPhase.name() : __indexFctPhase,
        __ident.name() : __ident,
        __type.name() : __type
    })
_module_typeBindings.GroundOpticalPropertyLink = GroundOpticalPropertyLink
Namespace.addCategoryObject('typeBinding', '_GroundOpticalPropertyLink', GroundOpticalPropertyLink)


# Complex type _GroundThermalPropertyLink with content type EMPTY
class GroundThermalPropertyLink (pyxb.binding.basis.complexTypeDefinition):
    """ GroundThermalPropertyLink GroundThermalPropertyLink"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_GroundThermalPropertyLink')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 334, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute indexTemperature uses Python identifier indexTemperature
    __indexTemperature = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'indexTemperature'), 'indexTemperature', '__AbsentNamespace0_GroundThermalPropertyLink_indexTemperature', pyxb.binding.datatypes.int, unicode_default='0')
    __indexTemperature._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 341, 2)
    __indexTemperature._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 341, 2)
    
    indexTemperature = property(__indexTemperature.value, __indexTemperature.set, None, ' indexTemperature indexTemperature')

    
    # Attribute idTemperature uses Python identifier idTemperature
    __idTemperature = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'idTemperature'), 'idTemperature', '__AbsentNamespace0_GroundThermalPropertyLink_idTemperature', pyxb.binding.datatypes.string, unicode_default='ThermalFunction290_310')
    __idTemperature._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 347, 2)
    __idTemperature._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 347, 2)
    
    idTemperature = property(__idTemperature.value, __idTemperature.set, None, ' Thermal Function ID Thermal Function ID')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __indexTemperature.name() : __indexTemperature,
        __idTemperature.name() : __idTemperature
    })
_module_typeBindings.GroundThermalPropertyLink = GroundThermalPropertyLink
Namespace.addCategoryObject('typeBinding', '_GroundThermalPropertyLink', GroundThermalPropertyLink)


# Complex type _PlotVegetationProperties with content type ELEMENT_ONLY
class PlotVegetationProperties (pyxb.binding.basis.complexTypeDefinition):
    """ Caracteristics of a plot (height of its vegetation, LAI ...). Caracteristics of a plot (height of its vegetation, LAI ...)."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_PlotVegetationProperties')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 355, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element MeshPlotRepresentation uses Python identifier MeshPlotRepresentation
    __MeshPlotRepresentation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'MeshPlotRepresentation'), 'MeshPlotRepresentation', '__AbsentNamespace0_PlotVegetationProperties_MeshPlotRepresentation', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 361, 3), )

    
    MeshPlotRepresentation = property(__MeshPlotRepresentation.value, __MeshPlotRepresentation.set, None, None)

    
    # Element VegetationGeometry uses Python identifier VegetationGeometry
    __VegetationGeometry = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'VegetationGeometry'), 'VegetationGeometry', '__AbsentNamespace0_PlotVegetationProperties_VegetationGeometry', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 362, 3), )

    
    VegetationGeometry = property(__VegetationGeometry.value, __VegetationGeometry.set, None, None)

    
    # Element VegetationFillGeometry uses Python identifier VegetationFillGeometry
    __VegetationFillGeometry = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'VegetationFillGeometry'), 'VegetationFillGeometry', '__AbsentNamespace0_PlotVegetationProperties_VegetationFillGeometry', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 363, 3), )

    
    VegetationFillGeometry = property(__VegetationFillGeometry.value, __VegetationFillGeometry.set, None, None)

    
    # Element LAIVegetation uses Python identifier LAIVegetation
    __LAIVegetation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'LAIVegetation'), 'LAIVegetation', '__AbsentNamespace0_PlotVegetationProperties_LAIVegetation', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 364, 3), )

    
    LAIVegetation = property(__LAIVegetation.value, __LAIVegetation.set, None, None)

    
    # Element UFVegetation uses Python identifier UFVegetation
    __UFVegetation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'UFVegetation'), 'UFVegetation', '__AbsentNamespace0_PlotVegetationProperties_UFVegetation', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 365, 3), )

    
    UFVegetation = property(__UFVegetation.value, __UFVegetation.set, None, None)

    
    # Element VegetationOpticalPropertyLink uses Python identifier VegetationOpticalPropertyLink
    __VegetationOpticalPropertyLink = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'VegetationOpticalPropertyLink'), 'VegetationOpticalPropertyLink', '__AbsentNamespace0_PlotVegetationProperties_VegetationOpticalPropertyLink', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 366, 3), )

    
    VegetationOpticalPropertyLink = property(__VegetationOpticalPropertyLink.value, __VegetationOpticalPropertyLink.set, None, None)

    
    # Element GroundThermalPropertyLink uses Python identifier GroundThermalPropertyLink
    __GroundThermalPropertyLink = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink'), 'GroundThermalPropertyLink', '__AbsentNamespace0_PlotVegetationProperties_GroundThermalPropertyLink', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 367, 3), )

    
    GroundThermalPropertyLink = property(__GroundThermalPropertyLink.value, __GroundThermalPropertyLink.set, None, None)

    
    # Attribute verticalFillMode uses Python identifier verticalFillMode
    __verticalFillMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'verticalFillMode'), 'verticalFillMode', '__AbsentNamespace0_PlotVegetationProperties_verticalFillMode', pyxb.binding.datatypes.int, unicode_default='0')
    __verticalFillMode._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 369, 2)
    __verticalFillMode._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 369, 2)
    
    verticalFillMode = property(__verticalFillMode.value, __verticalFillMode.set, None, ' Fill everything in the defined area below a given altitude.                 Fill everything in the defined area below a given altitude.                ')

    
    # Attribute trianglePlotRepresentation uses Python identifier trianglePlotRepresentation
    __trianglePlotRepresentation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'trianglePlotRepresentation'), 'trianglePlotRepresentation', '__AbsentNamespace0_PlotVegetationProperties_trianglePlotRepresentation', pyxb.binding.datatypes.int, unicode_default='0')
    __trianglePlotRepresentation._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 375, 2)
    __trianglePlotRepresentation._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 375, 2)
    
    trianglePlotRepresentation = property(__trianglePlotRepresentation.value, __trianglePlotRepresentation.set, None, ' If checked, the plot will be represented as a cloud of triangles. Otherwise, it will be represented as a juxtaposition of turbid cells. If checked, the plot will be represented as a cloud of triangles. Otherwise, it will be represented as a juxtaposition of turbid cells.')

    
    # Attribute densityDefinition uses Python identifier densityDefinition
    __densityDefinition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'densityDefinition'), 'densityDefinition', '__AbsentNamespace0_PlotVegetationProperties_densityDefinition', pyxb.binding.datatypes.int, unicode_default='0')
    __densityDefinition._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 381, 2)
    __densityDefinition._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 381, 2)
    
    densityDefinition = property(__densityDefinition.value, __densityDefinition.set, None, ' Choose if you define vegetation by LAI (foliar m2 / m2 of the plot) or Ul (foliar m2 / m3 of the plot)  Choose if you define vegetation by LAI (foliar m2 / m2 of the plot) or Ul (foliar m2 / m3 of the plot) ')

    _ElementMap.update({
        __MeshPlotRepresentation.name() : __MeshPlotRepresentation,
        __VegetationGeometry.name() : __VegetationGeometry,
        __VegetationFillGeometry.name() : __VegetationFillGeometry,
        __LAIVegetation.name() : __LAIVegetation,
        __UFVegetation.name() : __UFVegetation,
        __VegetationOpticalPropertyLink.name() : __VegetationOpticalPropertyLink,
        __GroundThermalPropertyLink.name() : __GroundThermalPropertyLink
    })
    _AttributeMap.update({
        __verticalFillMode.name() : __verticalFillMode,
        __trianglePlotRepresentation.name() : __trianglePlotRepresentation,
        __densityDefinition.name() : __densityDefinition
    })
_module_typeBindings.PlotVegetationProperties = PlotVegetationProperties
Namespace.addCategoryObject('typeBinding', '_PlotVegetationProperties', PlotVegetationProperties)


# Complex type _MeshPlotRepresentation with content type ELEMENT_ONLY
class MeshPlotRepresentation (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_MeshPlotRepresentation')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 389, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element NumberOfTriangleParameters uses Python identifier NumberOfTriangleParameters
    __NumberOfTriangleParameters = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'NumberOfTriangleParameters'), 'NumberOfTriangleParameters', '__AbsentNamespace0_MeshPlotRepresentation_NumberOfTriangleParameters', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 395, 3), )

    
    NumberOfTriangleParameters = property(__NumberOfTriangleParameters.value, __NumberOfTriangleParameters.set, None, None)

    
    # Element MeshLeafDimensionParameters uses Python identifier MeshLeafDimensionParameters
    __MeshLeafDimensionParameters = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'MeshLeafDimensionParameters'), 'MeshLeafDimensionParameters', '__AbsentNamespace0_MeshPlotRepresentation_MeshLeafDimensionParameters', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 396, 3), )

    
    MeshLeafDimensionParameters = property(__MeshLeafDimensionParameters.value, __MeshLeafDimensionParameters.set, None, None)

    
    # Attribute distributionMode uses Python identifier distributionMode
    __distributionMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'distributionMode'), 'distributionMode', '__AbsentNamespace0_MeshPlotRepresentation_distributionMode', pyxb.binding.datatypes.int, unicode_default='0')
    __distributionMode._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 398, 2)
    __distributionMode._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 398, 2)
    
    distributionMode = property(__distributionMode.value, __distributionMode.set, None, ' Defines how the leaves are geometrically distributed in the crown. Defines how the leaves are geometrically distributed in the crown.')

    
    # Attribute leafDefinition uses Python identifier leafDefinition
    __leafDefinition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'leafDefinition'), 'leafDefinition', '__AbsentNamespace0_MeshPlotRepresentation_leafDefinition', pyxb.binding.datatypes.int, unicode_default='1')
    __leafDefinition._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 404, 2)
    __leafDefinition._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 404, 2)
    
    leafDefinition = property(__leafDefinition.value, __leafDefinition.set, None, ' Definition of the leaves geometry and numbers. Definition of the leaves geometry and numbers.')

    _ElementMap.update({
        __NumberOfTriangleParameters.name() : __NumberOfTriangleParameters,
        __MeshLeafDimensionParameters.name() : __MeshLeafDimensionParameters
    })
    _AttributeMap.update({
        __distributionMode.name() : __distributionMode,
        __leafDefinition.name() : __leafDefinition
    })
_module_typeBindings.MeshPlotRepresentation = MeshPlotRepresentation
Namespace.addCategoryObject('typeBinding', '_MeshPlotRepresentation', MeshPlotRepresentation)


# Complex type _NumberOfTriangleParameters with content type EMPTY
class NumberOfTriangleParameters (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_NumberOfTriangleParameters')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 412, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute nbTriangles uses Python identifier nbTriangles
    __nbTriangles = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'nbTriangles'), 'nbTriangles', '__AbsentNamespace0_NumberOfTriangleParameters_nbTriangles', pyxb.binding.datatypes.int, unicode_default='10000')
    __nbTriangles._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 419, 2)
    __nbTriangles._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 419, 2)
    
    nbTriangles = property(__nbTriangles.value, __nbTriangles.set, None, ' Fix the number of leaves/triangles of the plot. The leaf area will then be the total area of leaves in the plot divided by this number. The real effective number generated may vary due to rounding and distribution errors. Fix the number of leaves/triangles of the plot. The leaf area will then be the total area of leaves in the plot divided by this number. The real effective number generated may vary due to rounding and distribution errors.')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __nbTriangles.name() : __nbTriangles
    })
_module_typeBindings.NumberOfTriangleParameters = NumberOfTriangleParameters
Namespace.addCategoryObject('typeBinding', '_NumberOfTriangleParameters', NumberOfTriangleParameters)


# Complex type _MeshLeafDimensionParameters with content type EMPTY
class MeshLeafDimensionParameters (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_MeshLeafDimensionParameters')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 427, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute meshLeafDimension uses Python identifier meshLeafDimension
    __meshLeafDimension = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'meshLeafDimension'), 'meshLeafDimension', '__AbsentNamespace0_MeshLeafDimensionParameters_meshLeafDimension', pyxb.binding.datatypes.double, unicode_default='0.003')
    __meshLeafDimension._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 434, 2)
    __meshLeafDimension._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 434, 2)
    
    meshLeafDimension = property(__meshLeafDimension.value, __meshLeafDimension.set, None, ' Area of each individual leaf/triangle. The number of leaves/triangles will then be the total area of leaves in the plot divided by this number. The real effective number generated may vary due to rounding and distribution errors. Area of each individual leaf/triangle. The number of leaves/triangles will then be the total area of leaves in the plot divided by this number. The real effective number generated may vary due to rounding and distribution errors.')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __meshLeafDimension.name() : __meshLeafDimension
    })
_module_typeBindings.MeshLeafDimensionParameters = MeshLeafDimensionParameters
Namespace.addCategoryObject('typeBinding', '_MeshLeafDimensionParameters', MeshLeafDimensionParameters)


# Complex type _VegetationGeometry with content type EMPTY
class VegetationGeometry (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_VegetationGeometry')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 442, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute height uses Python identifier height
    __height = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'height'), 'height', '__AbsentNamespace0_VegetationGeometry_height', pyxb.binding.datatypes.double, unicode_default='1.0')
    __height._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 449, 2)
    __height._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 449, 2)
    
    height = property(__height.value, __height.set, None, ' Thickness of the vegetation layer  Thickness of the vegetation layer ')

    
    # Attribute baseheight uses Python identifier baseheight
    __baseheight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'baseheight'), 'baseheight', '__AbsentNamespace0_VegetationGeometry_baseheight', pyxb.binding.datatypes.double, unicode_default='0')
    __baseheight._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 455, 2)
    __baseheight._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 455, 2)
    
    baseheight = property(__baseheight.value, __baseheight.set, None, ' Altitude in meter of the base of the vegetation above the ground of the plot. Altitude in meter of the base of the vegetation above the ground of the plot.')

    
    # Attribute stDev uses Python identifier stDev
    __stDev = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'stDev'), 'stDev', '__AbsentNamespace0_VegetationGeometry_stDev', pyxb.binding.datatypes.double, unicode_default='0.0')
    __stDev._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 461, 2)
    __stDev._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 461, 2)
    
    stDev = property(__stDev.value, __stDev.set, None, ' Standard deviation of the vegetation layer height Standard deviation of the vegetation layer height')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __height.name() : __height,
        __baseheight.name() : __baseheight,
        __stDev.name() : __stDev
    })
_module_typeBindings.VegetationGeometry = VegetationGeometry
Namespace.addCategoryObject('typeBinding', '_VegetationGeometry', VegetationGeometry)


# Complex type _VegetationFillGeometry with content type EMPTY
class VegetationFillGeometry (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_VegetationFillGeometry')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 469, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute topHeight uses Python identifier topHeight
    __topHeight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'topHeight'), 'topHeight', '__AbsentNamespace0_VegetationFillGeometry_topHeight', pyxb.binding.datatypes.double, unicode_default='1.0')
    __topHeight._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 476, 2)
    __topHeight._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 476, 2)
    
    topHeight = property(__topHeight.value, __topHeight.set, None, ' Altitude up to which the plot fill the scene, stating from the bottom of the scene Altitude up to which the plot fill the scene, stating from the bottom of the scene')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __topHeight.name() : __topHeight
    })
_module_typeBindings.VegetationFillGeometry = VegetationFillGeometry
Namespace.addCategoryObject('typeBinding', '_VegetationFillGeometry', VegetationFillGeometry)


# Complex type _LAIVegetation with content type EMPTY
class LAIVegetation (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_LAIVegetation')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 484, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute LAI uses Python identifier LAI
    __LAI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'LAI'), 'LAI', '__AbsentNamespace0_LAIVegetation_LAI', pyxb.binding.datatypes.double, unicode_default='1.0')
    __LAI._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 491, 2)
    __LAI._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 491, 2)
    
    LAI = property(__LAI.value, __LAI.set, None, ' Leaf Area Index: total leaf area in the plot divided by the scene area.     Leaf Area Index: total leaf area in the plot divided by the scene area.    ')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __LAI.name() : __LAI
    })
_module_typeBindings.LAIVegetation = LAIVegetation
Namespace.addCategoryObject('typeBinding', '_LAIVegetation', LAIVegetation)


# Complex type _UFVegetation with content type EMPTY
class UFVegetation (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_UFVegetation')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 499, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute UF uses Python identifier UF
    __UF = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'UF'), 'UF', '__AbsentNamespace0_UFVegetation_UF', pyxb.binding.datatypes.double, unicode_default='1.0')
    __UF._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 506, 2)
    __UF._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 506, 2)
    
    UF = property(__UF.value, __UF.set, None, ' Ul Ul')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __UF.name() : __UF
    })
_module_typeBindings.UFVegetation = UFVegetation
Namespace.addCategoryObject('typeBinding', '_UFVegetation', UFVegetation)


# Complex type _VegetationOpticalPropertyLink with content type EMPTY
class VegetationOpticalPropertyLink (pyxb.binding.basis.complexTypeDefinition):
    """ Optical properties for a DART vegetation phase function (name, type and index). Optical properties for a DART vegetation phase function (name, type and index)."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_VegetationOpticalPropertyLink')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 514, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute indexFctPhase uses Python identifier indexFctPhase
    __indexFctPhase = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'indexFctPhase'), 'indexFctPhase', '__AbsentNamespace0_VegetationOpticalPropertyLink_indexFctPhase', pyxb.binding.datatypes.int, unicode_default='0')
    __indexFctPhase._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 521, 2)
    __indexFctPhase._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 521, 2)
    
    indexFctPhase = property(__indexFctPhase.value, __indexFctPhase.set, None, ' Index of the DART phase function of the ground of the plot. Index of the DART phase function of the ground of the plot.')

    
    # Attribute ident uses Python identifier ident
    __ident = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'ident'), 'ident', '__AbsentNamespace0_VegetationOpticalPropertyLink_ident', pyxb.binding.datatypes.string, unicode_default='Turbid_Leaf_Deciduous_Phase_Function')
    __ident._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 527, 2)
    __ident._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 527, 2)
    
    ident = property(__ident.value, __ident.set, None, ' proportion of photons intercepted along an incident direction that are scattered within a solid angle along a given direction proportion of photons intercepted along an incident direction that are scattered within a solid angle along a given direction')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __indexFctPhase.name() : __indexFctPhase,
        __ident.name() : __ident
    })
_module_typeBindings.VegetationOpticalPropertyLink = VegetationOpticalPropertyLink
Namespace.addCategoryObject('typeBinding', '_VegetationOpticalPropertyLink', VegetationOpticalPropertyLink)


# Complex type _PlotAirProperties with content type ELEMENT_ONLY
class PlotAirProperties (pyxb.binding.basis.complexTypeDefinition):
    """ PlotAirProperties PlotAirProperties"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_PlotAirProperties')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 535, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element AirGeometry uses Python identifier AirGeometry
    __AirGeometry = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AirGeometry'), 'AirGeometry', '__AbsentNamespace0_PlotAirProperties_AirGeometry', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 541, 3), )

    
    AirGeometry = property(__AirGeometry.value, __AirGeometry.set, None, None)

    
    # Element AirFillGeometry uses Python identifier AirFillGeometry
    __AirFillGeometry = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AirFillGeometry'), 'AirFillGeometry', '__AbsentNamespace0_PlotAirProperties_AirFillGeometry', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 542, 3), )

    
    AirFillGeometry = property(__AirFillGeometry.value, __AirFillGeometry.set, None, None)

    
    # Element AirOpticalProperties uses Python identifier AirOpticalProperties
    __AirOpticalProperties = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AirOpticalProperties'), 'AirOpticalProperties', '__AbsentNamespace0_PlotAirProperties_AirOpticalProperties', True, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 543, 3), )

    
    AirOpticalProperties = property(__AirOpticalProperties.value, __AirOpticalProperties.set, None, None)

    
    # Element GroundThermalPropertyLink uses Python identifier GroundThermalPropertyLink
    __GroundThermalPropertyLink = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink'), 'GroundThermalPropertyLink', '__AbsentNamespace0_PlotAirProperties_GroundThermalPropertyLink', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 544, 3), )

    
    GroundThermalPropertyLink = property(__GroundThermalPropertyLink.value, __GroundThermalPropertyLink.set, None, None)

    
    # Attribute verticalFillMode uses Python identifier verticalFillMode
    __verticalFillMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'verticalFillMode'), 'verticalFillMode', '__AbsentNamespace0_PlotAirProperties_verticalFillMode', pyxb.binding.datatypes.int, unicode_default='0')
    __verticalFillMode._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 546, 2)
    __verticalFillMode._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 546, 2)
    
    verticalFillMode = property(__verticalFillMode.value, __verticalFillMode.set, None, ' Fill everything in the defined area below a given altitude.                  Fill everything in the defined area below a given altitude.                 ')

    
    # Attribute nbParticule uses Python identifier nbParticule
    __nbParticule = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'nbParticule'), 'nbParticule', '__AbsentNamespace0_PlotAirProperties_nbParticule', pyxb.binding.datatypes.int, unicode_default='1')
    __nbParticule._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 552, 2)
    __nbParticule._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 552, 2)
    
    nbParticule = property(__nbParticule.value, __nbParticule.set, None, ' Number of gas/particles in the air plot. Number of gas/particles in the air plot.')

    _ElementMap.update({
        __AirGeometry.name() : __AirGeometry,
        __AirFillGeometry.name() : __AirFillGeometry,
        __AirOpticalProperties.name() : __AirOpticalProperties,
        __GroundThermalPropertyLink.name() : __GroundThermalPropertyLink
    })
    _AttributeMap.update({
        __verticalFillMode.name() : __verticalFillMode,
        __nbParticule.name() : __nbParticule
    })
_module_typeBindings.PlotAirProperties = PlotAirProperties
Namespace.addCategoryObject('typeBinding', '_PlotAirProperties', PlotAirProperties)


# Complex type _AirGeometry with content type EMPTY
class AirGeometry (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_AirGeometry')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 560, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute height uses Python identifier height
    __height = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'height'), 'height', '__AbsentNamespace0_AirGeometry_height', pyxb.binding.datatypes.double, unicode_default='1.0')
    __height._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 567, 2)
    __height._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 567, 2)
    
    height = property(__height.value, __height.set, None, ' Thickness of the air layer  Thickness of the air layer ')

    
    # Attribute baseheight uses Python identifier baseheight
    __baseheight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'baseheight'), 'baseheight', '__AbsentNamespace0_AirGeometry_baseheight', pyxb.binding.datatypes.double, unicode_default='0')
    __baseheight._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 573, 2)
    __baseheight._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 573, 2)
    
    baseheight = property(__baseheight.value, __baseheight.set, None, ' Altitude in meter of the base of the vegetation above the ground of the plot. Altitude in meter of the base of the vegetation above the ground of the plot.')

    
    # Attribute stDev uses Python identifier stDev
    __stDev = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'stDev'), 'stDev', '__AbsentNamespace0_AirGeometry_stDev', pyxb.binding.datatypes.double, unicode_default='0.0')
    __stDev._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 579, 2)
    __stDev._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 579, 2)
    
    stDev = property(__stDev.value, __stDev.set, None, ' Standard deviation of the air layer height Standard deviation of the air layer height')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __height.name() : __height,
        __baseheight.name() : __baseheight,
        __stDev.name() : __stDev
    })
_module_typeBindings.AirGeometry = AirGeometry
Namespace.addCategoryObject('typeBinding', '_AirGeometry', AirGeometry)


# Complex type _AirFillGeometry with content type EMPTY
class AirFillGeometry (pyxb.binding.basis.complexTypeDefinition):
    """  """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_AirFillGeometry')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 587, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute topHeight uses Python identifier topHeight
    __topHeight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'topHeight'), 'topHeight', '__AbsentNamespace0_AirFillGeometry_topHeight', pyxb.binding.datatypes.double, unicode_default='1.0')
    __topHeight._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 594, 2)
    __topHeight._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 594, 2)
    
    topHeight = property(__topHeight.value, __topHeight.set, None, ' Altitude up to which the plot fill the scene, stating from the bottom of the scene  Altitude up to which the plot fill the scene, stating from the bottom of the scene ')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __topHeight.name() : __topHeight
    })
_module_typeBindings.AirFillGeometry = AirFillGeometry
Namespace.addCategoryObject('typeBinding', '_AirFillGeometry', AirFillGeometry)


# Complex type _AirOpticalProperties with content type ELEMENT_ONLY
class AirOpticalProperties (pyxb.binding.basis.complexTypeDefinition):
    """ AirOpticalProperties AirOpticalProperties"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_AirOpticalProperties')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 602, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element AirOpticalPropertyLink uses Python identifier AirOpticalPropertyLink
    __AirOpticalPropertyLink = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AirOpticalPropertyLink'), 'AirOpticalPropertyLink', '__AbsentNamespace0_AirOpticalProperties_AirOpticalPropertyLink', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 608, 3), )

    
    AirOpticalPropertyLink = property(__AirOpticalPropertyLink.value, __AirOpticalPropertyLink.set, None, None)

    
    # Attribute extinctionCoefficient uses Python identifier extinctionCoefficient
    __extinctionCoefficient = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'extinctionCoefficient'), 'extinctionCoefficient', '__AbsentNamespace0_AirOpticalProperties_extinctionCoefficient', pyxb.binding.datatypes.double, unicode_default='5E-16')
    __extinctionCoefficient._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 610, 2)
    __extinctionCoefficient._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 610, 2)
    
    extinctionCoefficient = property(__extinctionCoefficient.value, __extinctionCoefficient.set, None, ' Particle Density (Number of particle per meter-cube) Particle Density (Number of particle per meter-cube)')

    _ElementMap.update({
        __AirOpticalPropertyLink.name() : __AirOpticalPropertyLink
    })
    _AttributeMap.update({
        __extinctionCoefficient.name() : __extinctionCoefficient
    })
_module_typeBindings.AirOpticalProperties = AirOpticalProperties
Namespace.addCategoryObject('typeBinding', '_AirOpticalProperties', AirOpticalProperties)


# Complex type _AirOpticalPropertyLink with content type EMPTY
class AirOpticalPropertyLink (pyxb.binding.basis.complexTypeDefinition):
    """ AirOpticalPropertyLink AirOpticalPropertyLink"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_AirOpticalPropertyLink')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 618, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute indexFctPhase uses Python identifier indexFctPhase
    __indexFctPhase = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'indexFctPhase'), 'indexFctPhase', '__AbsentNamespace0_AirOpticalPropertyLink_indexFctPhase', pyxb.binding.datatypes.int, unicode_default='0')
    __indexFctPhase._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 625, 2)
    __indexFctPhase._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 625, 2)
    
    indexFctPhase = property(__indexFctPhase.value, __indexFctPhase.set, None, ' Index of the DART phase function of the ground of the plot. Index of the DART phase function of the ground of the plot.')

    
    # Attribute ident uses Python identifier ident
    __ident = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'ident'), 'ident', '__AbsentNamespace0_AirOpticalPropertyLink_ident', pyxb.binding.datatypes.string, unicode_default='Molecule')
    __ident._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 631, 2)
    __ident._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 631, 2)
    
    ident = property(__ident.value, __ident.set, None, ' proportion of photons intercepted along an incident direction that are scattered within a solid angle along a given direction proportion of photons intercepted along an incident direction that are scattered within a solid angle along a given direction')

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __indexFctPhase.name() : __indexFctPhase,
        __ident.name() : __ident
    })
_module_typeBindings.AirOpticalPropertyLink = AirOpticalPropertyLink
Namespace.addCategoryObject('typeBinding', '_AirOpticalPropertyLink', AirOpticalPropertyLink)


# Complex type _PlotWaterProperties with content type ELEMENT_ONLY
class PlotWaterProperties (pyxb.binding.basis.complexTypeDefinition):
    """ Water properties Water properties"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_PlotWaterProperties')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 639, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element WaterOpticalProperties uses Python identifier WaterOpticalProperties
    __WaterOpticalProperties = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'WaterOpticalProperties'), 'WaterOpticalProperties', '__AbsentNamespace0_PlotWaterProperties_WaterOpticalProperties', True, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 645, 3), )

    
    WaterOpticalProperties = property(__WaterOpticalProperties.value, __WaterOpticalProperties.set, None, None)

    
    # Element GroundThermalPropertyLink uses Python identifier GroundThermalPropertyLink
    __GroundThermalPropertyLink = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink'), 'GroundThermalPropertyLink', '__AbsentNamespace0_PlotWaterProperties_GroundThermalPropertyLink', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 646, 3), )

    
    GroundThermalPropertyLink = property(__GroundThermalPropertyLink.value, __GroundThermalPropertyLink.set, None, None)

    
    # Attribute nbComponents uses Python identifier nbComponents
    __nbComponents = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'nbComponents'), 'nbComponents', '__AbsentNamespace0_PlotWaterProperties_nbComponents', pyxb.binding.datatypes.int, unicode_default='1')
    __nbComponents._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 648, 2)
    __nbComponents._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 648, 2)
    
    nbComponents = property(__nbComponents.value, __nbComponents.set, None, ' Number of components of the water volume Number of components of the water volume')

    
    # Attribute waterDepth uses Python identifier waterDepth
    __waterDepth = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'waterDepth'), 'waterDepth', '__AbsentNamespace0_PlotWaterProperties_waterDepth', pyxb.binding.datatypes.double, unicode_default='10.0')
    __waterDepth._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 654, 2)
    __waterDepth._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 654, 2)
    
    waterDepth = property(__waterDepth.value, __waterDepth.set, None, ' Water depth Water depth')

    
    # Attribute waterHeight uses Python identifier waterHeight
    __waterHeight = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'waterHeight'), 'waterHeight', '__AbsentNamespace0_PlotWaterProperties_waterHeight', pyxb.binding.datatypes.double, unicode_default='0.0')
    __waterHeight._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 660, 2)
    __waterHeight._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 660, 2)
    
    waterHeight = property(__waterHeight.value, __waterHeight.set, None, ' Water height level Water height level')

    
    # Attribute stDev uses Python identifier stDev
    __stDev = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'stDev'), 'stDev', '__AbsentNamespace0_PlotWaterProperties_stDev', pyxb.binding.datatypes.double, unicode_default='0.0')
    __stDev._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 666, 2)
    __stDev._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 666, 2)
    
    stDev = property(__stDev.value, __stDev.set, None, ' stDev stDev')

    _ElementMap.update({
        __WaterOpticalProperties.name() : __WaterOpticalProperties,
        __GroundThermalPropertyLink.name() : __GroundThermalPropertyLink
    })
    _AttributeMap.update({
        __nbComponents.name() : __nbComponents,
        __waterDepth.name() : __waterDepth,
        __waterHeight.name() : __waterHeight,
        __stDev.name() : __stDev
    })
_module_typeBindings.PlotWaterProperties = PlotWaterProperties
Namespace.addCategoryObject('typeBinding', '_PlotWaterProperties', PlotWaterProperties)


# Complex type _WaterOpticalProperties with content type ELEMENT_ONLY
class WaterOpticalProperties (pyxb.binding.basis.complexTypeDefinition):
    """ Component properties Component properties"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, '_WaterOpticalProperties')
    _XSDLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 674, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element AirOpticalPropertyLink uses Python identifier AirOpticalPropertyLink
    __AirOpticalPropertyLink = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AirOpticalPropertyLink'), 'AirOpticalPropertyLink', '__AbsentNamespace0_WaterOpticalProperties_AirOpticalPropertyLink', False, pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 680, 3), )

    
    AirOpticalPropertyLink = property(__AirOpticalPropertyLink.value, __AirOpticalPropertyLink.set, None, None)

    
    # Attribute extinctionCoefficient uses Python identifier extinctionCoefficient
    __extinctionCoefficient = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'extinctionCoefficient'), 'extinctionCoefficient', '__AbsentNamespace0_WaterOpticalProperties_extinctionCoefficient', pyxb.binding.datatypes.double, unicode_default='0.5')
    __extinctionCoefficient._DeclarationLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 682, 2)
    __extinctionCoefficient._UseLocation = pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 682, 2)
    
    extinctionCoefficient = property(__extinctionCoefficient.value, __extinctionCoefficient.set, None, ' Extinction coefficient Extinction coefficient')

    _ElementMap.update({
        __AirOpticalPropertyLink.name() : __AirOpticalPropertyLink
    })
    _AttributeMap.update({
        __extinctionCoefficient.name() : __extinctionCoefficient
    })
_module_typeBindings.WaterOpticalProperties = WaterOpticalProperties
Namespace.addCategoryObject('typeBinding', '_WaterOpticalProperties', WaterOpticalProperties)


DartFile = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'DartFile'), CTD_ANON, documentation='  ', location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 11, 1))
Namespace.addCategoryObject('elementBinding', DartFile.name().localName(), DartFile)



CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Plots'), Plots, scope=CTD_ANON, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 18, 3)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(None, 'Plots')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 18, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON._Automaton = _BuildAutomaton()




Plots._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'ExtraPlotsTextFileDefinition'), ExtraPlotsTextFileDefinition, scope=Plots, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 41, 3)))

Plots._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'ImportationFichierRaster'), ImportationFichierRaster, scope=Plots, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 42, 3)))

Plots._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Plot'), Plot, scope=Plots, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 43, 3)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 43, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Plots._UseForTag(pyxb.namespace.ExpandedName(None, 'ExtraPlotsTextFileDefinition')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 41, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Plots._UseForTag(pyxb.namespace.ExpandedName(None, 'ImportationFichierRaster')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 42, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(Plots._UseForTag(pyxb.namespace.ExpandedName(None, 'Plot')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 43, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Plots._Automaton = _BuildAutomaton_()




ImportationFichierRaster._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'VegetationProperties'), VegetationProperties, scope=ImportationFichierRaster, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 80, 3)))

ImportationFichierRaster._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'RasterCOSInformation'), RasterCOSInformation, scope=ImportationFichierRaster, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 81, 3)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImportationFichierRaster._UseForTag(pyxb.namespace.ExpandedName(None, 'VegetationProperties')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 80, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ImportationFichierRaster._UseForTag(pyxb.namespace.ExpandedName(None, 'RasterCOSInformation')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 81, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ImportationFichierRaster._Automaton = _BuildAutomaton_2()




VegetationProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'SelectSubZoneProperties'), SelectSubZoneProperties, scope=VegetationProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 91, 3)))

def _BuildAutomaton_3 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(VegetationProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'SelectSubZoneProperties')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 91, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
VegetationProperties._Automaton = _BuildAutomaton_3()




Plot._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Polygon2D'), Polygon2D, scope=Plot, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 197, 3)))

Plot._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Rectangle2D'), Rectangle2D, scope=Plot, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 198, 3)))

Plot._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'GroundOpticalPropertyLink'), GroundOpticalPropertyLink, scope=Plot, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 199, 3)))

Plot._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink'), GroundThermalPropertyLink, scope=Plot, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 200, 3)))

Plot._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'PlotVegetationProperties'), PlotVegetationProperties, scope=Plot, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 201, 3)))

Plot._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'PlotAirProperties'), PlotAirProperties, scope=Plot, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 202, 3)))

Plot._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'PlotWaterProperties'), PlotWaterProperties, scope=Plot, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 203, 3)))

def _BuildAutomaton_4 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Plot._UseForTag(pyxb.namespace.ExpandedName(None, 'Polygon2D')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 197, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Plot._UseForTag(pyxb.namespace.ExpandedName(None, 'Rectangle2D')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 198, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Plot._UseForTag(pyxb.namespace.ExpandedName(None, 'GroundOpticalPropertyLink')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 199, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Plot._UseForTag(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 200, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Plot._UseForTag(pyxb.namespace.ExpandedName(None, 'PlotVegetationProperties')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 201, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Plot._UseForTag(pyxb.namespace.ExpandedName(None, 'PlotAirProperties')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 202, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Plot._UseForTag(pyxb.namespace.ExpandedName(None, 'PlotWaterProperties')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 203, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    st_6._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Plot._Automaton = _BuildAutomaton_4()




Polygon2D._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Point2D'), Point2D, scope=Polygon2D, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 243, 3)))

def _BuildAutomaton_5 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=4, max=4, metadata=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 243, 3))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(Polygon2D._UseForTag(pyxb.namespace.ExpandedName(None, 'Point2D')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 243, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Polygon2D._Automaton = _BuildAutomaton_5()




PlotVegetationProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'MeshPlotRepresentation'), MeshPlotRepresentation, scope=PlotVegetationProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 361, 3)))

PlotVegetationProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'VegetationGeometry'), VegetationGeometry, scope=PlotVegetationProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 362, 3)))

PlotVegetationProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'VegetationFillGeometry'), VegetationFillGeometry, scope=PlotVegetationProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 363, 3)))

PlotVegetationProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'LAIVegetation'), LAIVegetation, scope=PlotVegetationProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 364, 3)))

PlotVegetationProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'UFVegetation'), UFVegetation, scope=PlotVegetationProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 365, 3)))

PlotVegetationProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'VegetationOpticalPropertyLink'), VegetationOpticalPropertyLink, scope=PlotVegetationProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 366, 3)))

PlotVegetationProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink'), GroundThermalPropertyLink, scope=PlotVegetationProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 367, 3)))

def _BuildAutomaton_6 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotVegetationProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'MeshPlotRepresentation')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 361, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotVegetationProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'VegetationGeometry')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 362, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotVegetationProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'VegetationFillGeometry')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 363, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotVegetationProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'LAIVegetation')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 364, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotVegetationProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'UFVegetation')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 365, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotVegetationProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'VegetationOpticalPropertyLink')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 366, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PlotVegetationProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 367, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    st_6._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PlotVegetationProperties._Automaton = _BuildAutomaton_6()




MeshPlotRepresentation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'NumberOfTriangleParameters'), NumberOfTriangleParameters, scope=MeshPlotRepresentation, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 395, 3)))

MeshPlotRepresentation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'MeshLeafDimensionParameters'), MeshLeafDimensionParameters, scope=MeshPlotRepresentation, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 396, 3)))

def _BuildAutomaton_7 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(MeshPlotRepresentation._UseForTag(pyxb.namespace.ExpandedName(None, 'NumberOfTriangleParameters')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 395, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(MeshPlotRepresentation._UseForTag(pyxb.namespace.ExpandedName(None, 'MeshLeafDimensionParameters')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 396, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
MeshPlotRepresentation._Automaton = _BuildAutomaton_7()




PlotAirProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AirGeometry'), AirGeometry, scope=PlotAirProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 541, 3)))

PlotAirProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AirFillGeometry'), AirFillGeometry, scope=PlotAirProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 542, 3)))

PlotAirProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AirOpticalProperties'), AirOpticalProperties, scope=PlotAirProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 543, 3)))

PlotAirProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink'), GroundThermalPropertyLink, scope=PlotAirProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 544, 3)))

def _BuildAutomaton_8 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_8
    del _BuildAutomaton_8
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotAirProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'AirGeometry')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 541, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotAirProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'AirFillGeometry')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 542, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotAirProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'AirOpticalProperties')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 543, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PlotAirProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 544, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PlotAirProperties._Automaton = _BuildAutomaton_8()




AirOpticalProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AirOpticalPropertyLink'), AirOpticalPropertyLink, scope=AirOpticalProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 608, 3)))

def _BuildAutomaton_9 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_9
    del _BuildAutomaton_9
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AirOpticalProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'AirOpticalPropertyLink')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 608, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
AirOpticalProperties._Automaton = _BuildAutomaton_9()




PlotWaterProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'WaterOpticalProperties'), WaterOpticalProperties, scope=PlotWaterProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 645, 3)))

PlotWaterProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink'), GroundThermalPropertyLink, scope=PlotWaterProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 646, 3)))

def _BuildAutomaton_10 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_10
    del _BuildAutomaton_10
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PlotWaterProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'WaterOpticalProperties')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 645, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PlotWaterProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'GroundThermalPropertyLink')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 646, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PlotWaterProperties._Automaton = _BuildAutomaton_10()




WaterOpticalProperties._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AirOpticalPropertyLink'), AirOpticalPropertyLink, scope=WaterOpticalProperties, location=pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 680, 3)))

def _BuildAutomaton_11 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_11
    del _BuildAutomaton_11
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(WaterOpticalProperties._UseForTag(pyxb.namespace.ExpandedName(None, 'AirOpticalPropertyLink')), pyxb.utils.utility.Location('/home/boissieu/git/pytools4dartMTD/core_ui/plots.xsd', 680, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
WaterOpticalProperties._Automaton = _BuildAutomaton_11()

