import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# ContourComparison
#

class ContourComparison(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ContourComparison" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# ContourComparisonWidget
#

class ContourComparisonWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/ContourComparison.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    self.ui.firstFiducialSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.secondFiducialSelector.setMRMLScene(slicer.mrmlScene)

    # connections
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    # self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    # self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    self.ui.applyButton.enabled = True


  def cleanup(self):
    pass

  def onApplyButton(self):
    logic = ContourComparisonLogic()
    # imageThreshold = self.ui.imageThresholdSliderWidget.value
    # logic.run(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

    firstFiducialNode = self.ui.firstFiducialSelector.currentNode()
    secondFiducialNode = self.ui.secondFiducialSelector.currentNode()

    if firstFiducialNode is None or secondFiducialNode is None:
      logging.warning("You need to select both fiducials!")
      return

    logic.createContours(firstFiducialNode, secondFiducialNode)

#
# ContourComparisonLogic
#

class ContourComparisonLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def createContours(self, firstFidcialNode, secondFiducialNode):

    firstMarkupsToModelNode = slicer.util.getFirstNodeByName('FirstContourNode', 'vtkMRMLMarkupsToModelNode')
    if firstMarkupsToModelNode is None:
      firstMarkupsToModelNode = slicer.vtkMRMLMarkupsToModelNode()
      firstMarkupsToModelNode.SetName('FirstContourNode')
      slicer.mrmlScene.AddNode(firstMarkupsToModelNode)

    firstMarkupsToModelNode.SetAndObserveInputNodeID(firstFidcialNode.GetID())

    firstCurve =  slicer.util.getFirstNodeByName('FirstCurveModel', 'vtkMRMLModelNode')
    if firstCurve is None:
      firstCurve = slicer.vtkMRMLModelNode()
      slicer.mrmlScene.AddNode(firstCurve)
      firstCurve.SetName("FirstCurveModel")
      display = slicer.vtkMRMLModelDisplayNode()
      slicer.mrmlScene.AddNode(display)
      firstCurve.SetAndObserveDisplayNodeID(display.GetID())
      display.SetColor(1,1,0)

    firstMarkupsToModelNode.SetAndObserveOutputModelNodeID(firstCurve.GetID())
    firstMarkupsToModelNode.SetModelType(firstMarkupsToModelNode.Curve)
    firstMarkupsToModelNode.SetCurveType(firstMarkupsToModelNode.CardinalSpline)
    firstMarkupsToModelNode.SetTubeRadius(1.0)


    secondMarkupsToModelNode = slicer.util.getFirstNodeByName('SecondContourNode', 'vtkMRMLMarkupsToModelNode')
    if secondMarkupsToModelNode is None:
      secondMarkupsToModelNode = slicer.vtkMRMLMarkupsToModelNode()
      secondMarkupsToModelNode.SetName('SecondContourNode')
      slicer.mrmlScene.AddNode(secondMarkupsToModelNode)

    secondMarkupsToModelNode.SetAndObserveInputNodeID(secondFiducialNode.GetID())

    secondCurve =  slicer.util.getFirstNodeByName('SecondCurveModel', 'vtkMRMLModelNode')
    if secondCurve is None:
      secondCurve = slicer.vtkMRMLModelNode()
      slicer.mrmlScene.AddNode(secondCurve)
      secondCurve.SetName("SecondCurveModel")
      display = slicer.vtkMRMLModelDisplayNode()
      slicer.mrmlScene.AddNode(display)
      secondCurve.SetAndObserveDisplayNodeID(display.GetID())
      display.SetColor(1,0,1)

    secondMarkupsToModelNode.SetAndObserveOutputModelNodeID(secondCurve.GetID())
    secondMarkupsToModelNode.SetModelType(secondMarkupsToModelNode.Curve)
    secondMarkupsToModelNode.SetCurveType(secondMarkupsToModelNode.CardinalSpline)
    secondMarkupsToModelNode.SetTubeRadius(1.0)


  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('ContourComparisonTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class ContourComparisonTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ContourComparison1()

  def test_ContourComparison1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767',
      checksums='SHA256:12d17fba4f2e1f1a843f0757366f28c3f3e1a8bb38836f0de2a32bb1cd476560')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = ContourComparisonLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
