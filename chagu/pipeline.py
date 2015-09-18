# This source file defines pipeline management functions for the visualisation
# class.

import copy
import vtk

import chagu.termini as termini


def autopipe(self):
    """
    Builds a pipeline from VTK objects managed by this visualisation instance
    by guessing what the user wants from the order objects were added.

    This can only be called once per visualisation instance, because I don't
    know how to clear ports yet. As such, all connections are done at
    once. This function creates the dictionary describing the pipeline, which
    is then passed to build_pipeline_from_dict.

    A pipeline guess requires:
      - A filereader object.
      - That Terminus objects are tracked before their filters.

    A pipeline guess is created by connecting each terminus with an output port
    with the filter that was added before it. If the terminus has no input
    ports, it is not considered in the guess. If it is a nasty vector terminus,
    it is connected directly to the filereader. The remaining vtkObjects are
    then connected in the order they were added, with objects added first as an
    input to objects added after them.

    As a tip, consider calling self.draw_pipeline_graphvis to understand how
    the pipeline is connected for this visualisation.

    Returns nothing.
    """

    pipelineDescription = []

    # Firstly, copy the order list to something we can remove entries from
    # safely. Reverse the list as well for easiness.
    order = copy.copy(self._order)[::-1]
    toPop = []

    # Connect each terminus object to the vtk object added before it.
    #
    # For each object, if that object is a terminus, search for the first
    # object added before it that was not a terminus. Add the two objects to
    # the pipeline, and remove the terminus to ensure its only drawn
    # once. Exceptions to this are:
    #
    # - If the terminus has no input ports, just remove it from the list
    #   because we are not connecting it to anything.
    # - If the terminus is a nasty vector terminus, connect it directly to the
    #   filereader if possible.
    for zJ in xrange(len(order)):
        vtkObjectRecv = order[zJ]
        if isinstance(self.get_vtk_object(vtkObjectRecv),
                      termini.Terminus) is True:

            # Make sure there are input ports to connect to.
            if hasattr(self.get_vtk_object(vtkObjectRecv),
                       "GetNumberOfInputPorts") is True:


                # If we are looking at nasty vectors, try to connect the
                # terminus directly to the filereader. This preserves the
                # direction. if the user wishes to slice their vector field,
                # it's best to do it with a mask as opposed to the slice
                # filter.
                if self.is_nasty(vtkObjectRecv) is True:

                    # Search for the filereader to connect to the terminus.
                    for zI in xrange(zJ, len(order)):
                        vtkObjectSend = order[zI]
                        if self.is_reader(vtkObjectSend) is True:
                            toPop.append(zJ)
                            pipelineDescription.append([vtkObjectSend,
                                                        vtkObjectRecv])
                            break
                else:

                    # Search for the vtkObject to connect to the terminus.
                    for zI in xrange(zJ, len(order)):
                        vtkObjectSend = order[zI]
                        if isinstance(self.get_vtk_object(vtkObjectSend),
                                      termini.Terminus) is False:
                            toPop.append(zJ)
                            pipelineDescription.append([vtkObjectSend,
                                                        vtkObjectRecv])
                            break

                # If we can't find a match for the terminus, raise an
                # exception.
                if zJ not in toPop:
                    raise # <!> Needs a message

            # If there are no input ports for the terminus, remove it from the
            # list.
            else:
                toPop.append(zJ)

    # Have to remove indeces in reverse order, because pop will reduce all
    # indeces by one.
    for index in toPop[::-1]:
        order.pop(index)

    # Connect remaining vtkObjects in order.
    for zI in xrange(1, len(order)):
        # If the zI-1th object is a fileReader, it means objects have been
        # added in a strange order. Not much we can do about this though, so we
        # need to check it.
        if self.is_reader(order[zI - 1]) is True:
            raise # <!> Needs a message

        pipelineDescription.append([order[zI], order[zI - 1]])


    # Build the pipeline from our guess.
    self.build_pipeline_from_dict(pipelineDescription)


def build_pipeline_from_dict(self, pipelineDescription):
    """
    Builds a pipeline from VTK objects managed by this visualisation instance
    by reading a nested iterable object.

    This can only be called once per visualisation instance, because I don't
    know how to clear ports yet. As such, all connections have to be done at
    once.

    Arguments:

      - pipelineDescription: Nested list where each internal list contains two
          either two strings denoting the names of objects to connect together,
          or a string and another iterable object in that order. The latter
          form is used for objects with multiple input or output ports, where
          the iterable object has three elements. In order, these should be:
            - String denoting name of the input object.
            - Integer denoting port of output object to connect.
            - Integer denoting port of input object to connect.
          If the value of a dictionary element is a string, input port zero is
          connected to output port zero, unless default_input_port or
          default_output_port are set as appropriate.

    Returns nothing.
    """
    # Ensure this is called only once.
    if self._pipeline != []:
        raise RuntimeError("'build_pipeline_from_dict' can only be called "
                           "once per visualisation instance without failure. "
                           "Sorry!")

    # Test each of the connections.
    for connection in pipelineDescription:
        outputObjName = connection[0]

        # If value is a string, we connect zero-ports together unless the
        # object has a default port set. Otherwise, read the data as defined in
        # the docstring.
        if type(connection[1]) is str:
            inputObjName = connection[1]

            if hasattr(self._vtkObjects[inputObjName],
                       "default_input_port") is True:
                inputPortIndex = self._vtkObjects[inputObjName].default_input_port
            else:
                inputPortIndex = 0

            if hasattr(self._vtkObjects[outputObjName],
                       "default_output_port") is True:
                outputPortIndex = self._vtkObjects[outputObjName].default_output_port
            else:
                outputPortIndex = 0

        else:
            inputObjName, outputPortIndex, inputPortIndex = connection[1]

        self.check_connection(outputObjName, inputObjName,
                              outputPortIndex=outputPortIndex,
                              inputPortIndex=inputPortIndex)

    # In the same way, make the connections. This ensures that a failure
    # anywhere in the dictionary makes no connections.
    for connection in pipelineDescription:
        outputObjName = connection[0]

        # If value is a string, we connect zero-ports together unless the
        # object has a default port set. Otherwise, read the data as defined in
        # the docstring.
        if type(connection[1]) is str:
            inputObjName = connection[1]

            if hasattr(self._vtkObjects[inputObjName],
                       "default_input_port") is True:
                inputPortIndex = self._vtkObjects[inputObjName].default_input_port
            else:
                inputPortIndex = 0

            if hasattr(self._vtkObjects[outputObjName],
                       "default_output_port") is True:
                outputPortIndex = self._vtkObjects[outputObjName].default_output_port
            else:
                outputPortIndex = 0

        else:
            inputObjName, outputPortIndex, inputPortIndex = connection[1]

        self.connect_vtk_objects(outputObjName, inputObjName,
                                 outputPortIndex=outputPortIndex,
                                 inputPortIndex=inputPortIndex)

    # Update the mappers for the actors. This in turn ensures that all objects
    # that are to be drawn are updated if they can be.
    allOutputObjectNames = [zI[1] if type(zI[1]) is str else zI[1][0]\
                            for zI in pipelineDescription]

    for terminusName in self._vtkTermini.keys():
        if terminusName in allOutputObjectNames:
            try:
                self._vtkTermini[terminusName].Update()
            except NameError:
                pass

    # Save the pipeline dict since we finished successfully.
    self._pipeline = pipelineDescription


def check_connection(self, outputObjectName, inputObjectName,
                     outputPortIndex=0, inputPortIndex=0):
    """
    Checks whether or not two VTK objects can be connected together without
    throwing a wobbly.

    Arguments:

      - outputObjectName: String denoting the name of the object to get the
          output port of.
      - inputObjectName: As above for the input object.
      - outputPortIndex: Integer denoting the output port of the object to
          connect, if any. For objects with only one outputPort, this should be
          zero.
      - inputPortIndex: As above for the input object.

    Returns nothing, but will raise an error if there is a problem.
    """

    # Check that port numbers are valid. We do this by getting the number of
    # output ports for the output object and the number of input ports for the
    # input object. If the requested index is greater than the number of
    # corresponding ports, we raise an error.
    outputTot = self._vtkObjects[outputObjectName].GetNumberOfOutputPorts() - 1
    if outputPortIndex > outputTot:
        raise ValueError("Output port index {} is greater than the number of "
                         "output ports that the object \"{}\" has, which is "
                         "{}."
                         .format(outputPortIndex, outputObjectName, outputTot))

    inputTot = self._vtkObjects[inputObjectName].GetNumberOfInputPorts() - 1
    if inputPortIndex > inputTot:
        raise ValueError("Input port index {} is greater than the number of "
                         "input ports that the object \"{}\" has, which is {}."
                         .format(inputPortIndex, inputObjectName, inputTot))

    # Check for invalid names.
    if self.is_tracked(outputObjectName) is False:
        raise ValueError("Invalid output object name {}. Did you mean one of "
                         "{}?".format(outputObjectName,
                                      self._vtkObjects.keys()))
    if self.is_tracked(inputObjectName) is False:
        raise ValueError("Invalid input object name {}. Did you mean one of "
                         "{}?".format(inputObjectName,
                                      self._vtkObjects.keys()))


def connect_vtk_objects(self, outputObjectName, inputObjectName,
                        outputPortIndex=0, inputPortIndex=0):
    """
    Connects two VTK objects that are managed by this visualisation instance
    together.

    Arguments:

      - outputObjectName: String denoting the name of the object to get the
          output port of.
      - inputObjectName: As above for the input object.
      - outputPortIndex: Integer denoting the output port of the object to
          connect, if any. For objects with only one outputPort, this should be
          zero.
      - inputPortIndex: As above for the input object.

    Returns nothing.
    """
    # Test the connection. We are working with a C library, so it's best to ask
    # permission first...
    self.check_connection(outputObjectName, inputObjectName, outputPortIndex=0,
                          inputPortIndex=0)

    # Connect the ports.
    outPort = self._vtkObjects[outputObjectName].GetOutputPort(outputPortIndex)
    self._vtkObjects[inputObjectName].SetInputConnection(inputPortIndex,
                                                         outPort)


def draw_pipeline_graphviz(self, directory=None, name=None):
    """
    Render the current pipeline of objects using graphviz as a PDF.

    Arguments:

      - directory: String denoting directory to save the render render to.
      - name: String denoting name of the PDF output (without extension).

    Returns nothing.
    """
    import graphviz

    graph = graphviz.Digraph(name=name if name is not None else
                             "{}_pipeline".format(self.name))

    # Build nodes.
    for objectName in self._vtkObjects.iterkeys():
        graph.node(objectName)

    # Build edges.
    for connection in self._pipeline:
        inputName = connection[0]

        if type(connection[1]) is str:
            outputName = connection[1]

        else:
            outputName = connection[1][0]

        graph.edge(inputName, outputName)

    # Draw the graph.
    graph.render(cleanup=True)
