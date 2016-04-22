# This is the "main" source file for VTK visualisation in this package. It
# defines the visualisation class, its initialisation, its properties, and
# other methods that don't fit into the other source files.

import filters
import pipeline
import render
import sources
import termini
import tracking


class Visualisation(object):
    """
    This class provides a unified interface to an entire visualisation using
    VTK.

    The major underlying mechanism of this class is that it stores each VTK
    class with a user-defined handle, and manages the pipeline and
    configuration of these objects without the user having to worry too much
    about connecting ports together manually. This is friendly for interactive
    visualisation sessions, and for sessions where multiple visualisations are
    to be produced through a loop construct.

    The user may load a file using a sourcing function, such as
    "load_visualisation_toolkit_file". They may then add filters. Once the data
    is filtered, termini (similar to actors) can be created with methods with
    the "act_" prefix. These methods create the high-level objects to draw. The
    pipeline connecting the source, filters, and termini together can be
    specified by the user, though this class can have a good go at getting that
    right. Once the components of the pipeline have been assembled,
    visualisation can begin by calling a visualisation method, which are
    methods with the "visualise_" prefix.

    Initialisation arguments:

      - name: String that names the visualisation object.
      - filePath: String determining file to load, or None if it is to be
          loaded manually later.

    Properties:

      - background: A three-element iterable object denoting RGB colours for
          the background of the visualisation.

      - camera: A dictionary dictating some properties of the camera. Valid
          keys and corresponding properties are:
            > focal point: A three-element iterable object denoting the point
                that the centre of the camera aligns with.
            > parallel projection: A boolean denoting whether or not to use
                parallel projection.
            > position: A three-element iterable object denoting the position
                of the camera in world co-ordinates.
            > view up: A three-element iterable object denoting the 'up'
                view direction. Note that this will not change the focal
                point and will only be used to orient the image.
            > zoom: A floating point number denoting zoom factor. Values
                greater than 1 zoom the camera in, and their reciprocals zoom
                the camera out. Zoom behaviour is different depending on
                whether or not parallel projection is used.

      - windowSize: A two-element iterable object denoting the size of the
          window to render to. Tiling window managers will resize the window,
          unless the window is floating.

    """

    def __init__(self, name="visualisation", filePath=None):

        # Set initial values for properties.
        self._background = [0., 0., 0.]
        self._camera = {}
        self._windowSize = [600, 600]

        # Set initial values for "accessible" member variables.
        self.name = name

        # Set initial values for member variables that the public shouldn't
        # see.
        self._boundingBox = [0 for zI in range(6)]
        self._colourmap_lut = termini.lookup_table_from_RGB_colourmap("PuOr")
        self._order = []  # This list maintains the order objects were
                          # added. This is for autopiping.
        self._pipeline = []
        self._vtkObjects = {}
        self._vtkTermini = {}

        # Load file if needed.
        if filePath is not None:
            self.load_visualisation_toolkit_file(filePath)

    ## Properties and setters.
    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, backgroundInput):
        """
        The input value must be an iterable object of length three containing
        only numerical elements (RGB). Any element less than zero will be set
        to zero, and any element greater than one will be set to one.
        """

        backgroundValue = []
        if hasattr(backgroundInput, "__getitem__") is False:
            raise TypeError("Background value \"{}\" must be iterable."
                            .format(backgroundInput))
        if len(backgroundInput) != 3:
            raise ValueError("Background value \"{}\" should contain exactly "
                             "three elements.".format(backgroundInput))
        for rgbValue in backgroundInput:
            try:
                convertedValue = float(rgbValue)
            except TypeError:
                raise ValueError("Background value \"{}\" has element "
                                 "\"{}\", which is not numerical"
                                 .format(backgroundInput, rgbValue))

            if convertedValue < 0:
                backgroundValue.append(0.)
            elif convertedValue > 1:
                backgroundValue.append(1.)
            else:
                backgroundValue.append(convertedValue)

        self._background = backgroundValue

    @property
    def camera(self):
        return self._camera

    _validCameraKeys = ("parallel projection", "view up", "position",
                        "focal point", "zoom")

    @camera.setter
    def camera(self, cameraInput):
        """
        The input value must have keys and values, can only have {} as
        keys. "view up", "position", and "focal point" keys must have values
        that are iterable objects containing only three numerical
        elements. "zoom" must have a single numerical value greater than
        zero. "parallel projection" must have a boolean value.
        """.format(self._validCameraKeys)

        cameraValue = {}

        if hasattr(cameraInput, "iteritems") is False:
            raise TypeError("Camera input \"{}\" must have keys and values."
                            .format(cameraInput))

        # For each of the inputs, we check it for errors. If it passes, it gets
        # added.
        for key, value in cameraInput.iteritems():
            if key not in self._validCameraKeys:
                raise ValueError("Camera key \"{}\" is not valid. Try one of "
                                 "\"{}\".".format(key, self._validCameraKeys))
            if key == "view up" or key == "position" or key == "focal point":
                if len(value) != 3:
                    raise ValueError("Camera key \"{}\" has invalid value "
                                     "\"{}\", which should contain exactly "
                                     "three elements.".format(key, value))
                for element in value:
                    try:
                        float(element)
                    except (ValueError, TypeError):
                        raise TypeError("Camera key \"{}\" has value with "
                                        "element \"{}\", which is not "
                                        "numerical".format(key, element))
            if key == "zoom":
                try:
                    float(value)
                except (ValueError, TypeError):
                    raise TypeError("Invalid zoom value \"{}\" is not "
                                    "numerical.".format(value))
                if value <= 0:
                    raise ValueError("Invalid zoom value \"{}\". This must be "
                                     "greater than zero.".format(value))
            if key == "parallel projection":
                if type(value) is not bool:
                    raise TypeError("Invalid parallel projection value \"{}\""
                                    ". This must be a boolean.".format(value))
            cameraValue[key] = value

        self._camera = cameraInput

    @property
    def colourmap_lut(self):
        return self._colourmap_lut

    @colourmap_lut.setter
    def colourmap_lut(self, colourMap, **kwargs):
        out = termini.lookup_table_from_RGB_colourmap(colourMap, **kwargs)
        self._colourmap_lut = out

    @property
    def windowSize(self):
        return self._windowSize

    @windowSize.setter
    def windowSize(self, windowSizeInput):
        """
        The input value must be an iterable object of length two containing
        only integer-like elements greater than zero (width, height).
        """

        windowSizeValue = []
        if hasattr(windowSizeInput, "__getitem__") is False:
            raise TypeError("Window size value \"{}\" must be iterable."
                            .format(windowSizeInput))
        if len(windowSizeInput) != 2:
            raise ValueError("Window size value \"{}\" should contain exactly "
                             "two elements.".format(windowSizeInput))
        for resolution in windowSizeInput:
            if resolution <= 0:
                raise ValueError("Window size value \"{}\" has element "
                                 "\"{}\", which must be greater than zero."
                                 .format(windowSizeInput, resolution))
            try:
                convertedValue = int(resolution)

                # Check to see if the value is integer-like
                if float(resolution) != convertedValue:
                    raise TypeError
            except TypeError:
                raise ValueError("Window size value \"{}\" has element "
                                 "\"{}\", which is not an integer."
                                 .format(windowSizeInput, resolution))

            windowSizeValue.append(convertedValue)

        self._windowSize = windowSizeValue

    # Filter functions.
    extract_vector_components = filters.extract_vector_components
    slice_data_with_plane = filters.slice_data_with_plane

    # Pipeline functions.
    autopipe = pipeline.autopipe
    build_pipeline_from_dict = pipeline.build_pipeline_from_dict
    check_connection = pipeline.check_connection
    connect_vtk_objects = pipeline.connect_vtk_objects
    draw_pipeline_graphviz = pipeline.draw_pipeline_graphviz

    # Rendering-related functions.
    build_renderer_and_window = render.build_renderer_and_window
    visualise_animate_rotate = render.visualise_animate_rotate
    visualise_interact = render.visualise_interact
    visualise_save = render.visualise_save

    # Sourcing functions.
    load_visualisation_toolkit_file = sources.load_visualisation_toolkit_file

    # Terminus / actor functions.
    act_colourbar = termini.act_colourbar
    act_cone_vector_field = termini.act_cone_vector_field
    act_nasty_vector_field = termini.act_nasty_vector_field
    act_surface = termini.act_surface

    # Tracking functions.
    get_vtk_object = tracking.get_vtk_object
    is_nasty = tracking.is_nasty
    is_reader = tracking.is_reader
    is_tracked = tracking.is_tracked
    track_object = tracking.track_object
